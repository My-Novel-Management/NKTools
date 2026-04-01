import os
import glob
import re
import pandas as pd
from dataclasses import dataclass, field

class CountType:
    TOTAL = 'total'
    INDIVIDUAL = 'individual'

@dataclass
class CountState:
    count_type: CountType = CountType.INDIVIDUAL
    file_name: str = "Unknonw"  # ファイル名
    total: int = 0              # 総文字数
    exclude_space: int = 0      # 空白除去文字数
    exclude_togaki: int = 0     # ト書き抜き文字数
    exclude_marks: int = 0      # 記号抜き文字数
    dialogues: dict = field(default_factory=dict)

class CharCounter:
    def __init__(self, base_path: str="", save_dir: str="results"):
        self.base_path = base_path
        self.save_dir = save_dir

    EXTENTIONS = ['*.txt', '*.md']
    PUNCTUATIONS = ['、', '。', '.', ',']

    def count_characters(self, output_file: str, exclue_chars: list):
        """
        対象のフォルダ内のファイルの文字数を計算する
        """
        # 記号除外用の正規表現パターン作成
        exclude_pattern = self._get_exclue_pattern(exclude_chars)

        files = []
        states = []
        for ext in self.EXTENTIONS:
            files.extend(glob.glob(os.path.join(self.base_path, '**', ext), recursive=True))
            # 総文字数のチェック
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 個別ファイルの文字数状況取得
                        state = self._get_count_state(file_path, content, exclude_pattern)
                        # 状態をリストに追加
                        states.append(state)
                except Exception as e:
                    print(f"エラー: {file_path} - {e}")
        if states:
            # 総合stateを算出し、保存
            total_state = CountState(count_type=CountType.TOTAL, file_name=self.base_path)
            total_state.total = sum(s.total for s in states)
            total_state.exclude_space = sum(s.exclude_space for s in states)
            total_state.exclude_togaki = sum(s.exclude_togaki for s in states)
            total_state.exclude_marks = sum(s.exclude_marks for s in states)
            states.append(total_state)
            df = pd.DataFrame(states)
            # 保存する
            save_path = f"{self.save_dir}/{output_file}.csv"
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(df)

    def _get_count_state(self, file_path: str, content: str, exclude_pattern: str) -> CountState:
        """コンテンツの文字数状況の取得"""
        # 1. 総文字数
        total_char_count = self._get_total_char_count(content)
        # 2. 空白改行除去文字数
        ex_space_count = len(self._exclude_spaces(content))
        # 3. 基本記号除去文字数
        ex_togai_count = len(self._get_exclude_togakis(content))
        # 4. 句読点記号除去文字数
        ex_marks_count = len(self._get_exclude_all_marks(content, exclude_pattern))
        return CountState(
            count_type=CountType.INDIVIDUAL,
            file_name=file_path,
            total=total_char_count,
            exclude_space=ex_space_count,
            exclude_togaki=ex_togai_count,
            exclude_marks=ex_marks_count,
            dialogues={}
        )
    
    def _get_exclude_togakis(self, content: str) -> str:
        # 不要行削除
        tmp_cond = self._exclude_head_of_line(content)
        # //指示行も削除
        tmp_cond = self._exclude_direction_headline(tmp_cond)
        # （）文字の削除
        tmp_cond = self._exclude_parentheses_chars(tmp_cond)
        # 最後に空白削除
        return self._exclude_spaces(tmp_cond)
    
    def _get_exclude_all_marks(self, content: str, exclude_pattern) -> str:
        """ト書きと句読点、記号除去する"""
        # 不要行削除
        tmp_cond = self._exclude_head_of_line(content)
        # //指示行も削除
        tmp_cond = self._exclude_direction_headline(tmp_cond)
        # （）文字の削除
        tmp_cond = self._exclude_parentheses_chars(tmp_cond)
        # 句読点の削除
        tmp_cond = self._exclude_punctuations(tmp_cond)
        # 指定文字の削除
        tmp_cond = self._exclude_special_patterns(tmp_cond, exclude_pattern)
        # 最後に空白削除
        return self._exclude_spaces(tmp_cond)

    def _get_exclue_pattern(self, exclue_chars: list) -> str:
        """記号除外用の正規表現パターン作成"""
        return "|".join(re.escape(char) for char in exclude_chars)
    
    def _get_total_char_count(self, content: str) -> int:
        """総文字数の取得"""
        return len(content)
    
    def _exclude_head_of_line(self, content: str) -> str:
        """行頭から不要な行の削除"""
        # 1. 行頭が「#」で始まる行、または「（」で始まる行を削除
        # ^#.* : 行頭が#で始まる行
        # ^\(.* : 行頭が(で始まる行
        lines = content.splitlines()
        filtered_lines = [
            line for line in lines 
            if not (line.strip().startswith('#') or line.strip().startswith('（'))
        ]
        return "\n".join(filtered_lines)
    
    def _exclude_direction_headline(self, content: str) -> str:
        """行頭にディレクション　//　がある行の削除"""
        lines = content.splitlines()
        filtered_lines = [
            line for line in lines 
            if not line.strip().startswith('//')
        ]
        return "\n".join(filtered_lines)
    
    def _exclude_parentheses_chars(self, content: str) -> str:
        """（）で囲まれた部分の削除"""
        # 2. （文字列）で囲まれた部分を削除 (※全角括弧を想定)
        # \(.*?\) : （ ）で囲まれた中身（最短一致）
        return re.sub(r'（.*?）', '', content)
    
    def _exclude_punctuations(self, content: str) -> str:
        """句読点の削除"""
        patterns = self._get_exclue_pattern(self.PUNCTUATIONS)
        return self._exclude_special_patterns(content, patterns)
    
    def _exclude_special_patterns(self, content: str, exclude_pattern: str):
        """指定文字の削除"""
        return re.sub(exclude_pattern, '', content)
    
    def _exclude_spaces(self, content: str) -> str:
        """スペース、タブ、改行の削除"""
        return re.sub(r'\s', '', content)
    
    def _get_excluded_content_chars(self, content: str, exclude_pattern: str) -> str:
        # 1. 不要行の削除
        ex_linehead_cont = self._exclude_head_of_line(content)

        # 2. 括弧（）で囲まれた部分の削除
        ex_parentheses_cont = self._exclude_parentheses_chars(ex_linehead_cont)

        # 3. 指定した特定の記号を除去
        ex_patterns_cont = self._exclude_special_patterns(ex_parentheses_cont, exclude_pattern)
                    
        # 4. 最後にスペース・タブ・改行を削除
        content_final = self._exclude_spaces(ex_patterns_cont)

        return content_final




if __name__ == "__main__":
    # --- 設定 ---
    output_filename = 'count_result'
    exclude_chars = ['！', '？', '♡', '♥', '♪', '★', '☆', '!', '?',]

    counter = CharCounter("build")
    counter.count_characters(output_filename, exclude_chars)

