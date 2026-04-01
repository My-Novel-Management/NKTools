import os
import glob
import re
from dataclasses import dataclass

class CountType:
    TOTAL = 'total'
    INDIVIDUAL = 'individual'

@dataclass
class CountState:
    count_type: CountType = CountType.INDIVIDUAL
    file_name: str = "Unknonw"
    total: int = 0
    exclude_togaki: int = 0
    exclude_marks: int = 0

class CharCounter:
    def __init__(self, base_path: str=""):
        self.base_path = base_path

    EXTENTIONS = ['*.txt', '*.md']
    PUNCATIONS = ['、', '。', '.', ',']

    def count_characters(self, output_file: str, exclue_chars: list):
        """
        対象のフォルダ内のファイルの文字数を計算する
        """
        # 記号除外用の正規表現パターン作成
        exclude_pattern = self._get_exclue_pattern(exclude_chars)

        files = []
        for ext in self.EXTENTIONS:
            files.extend(glob.glob(os.path.join(self.base_path, '**', ext), recursive=True))
        with open(output_file, 'w', encoding='utf-8') as f:
            # 総文字数のチェック
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 個別ファイルの文字数状況取得
                        state = self._get_count_state(file_path, content, exclude_pattern)
                        # 状態保存
                        print(state)
                except Exception as e:
                    print(f"エラー: {file_path} - {e}")

    def _get_count_state(self, file_path: str, content: str, exclude_pattern: str) -> CountState:
        """コンテンツの文字数状況の取得"""
        # 1. 総文字数
        total_char_count = self._get_total_char_count(content)
        print(f"total: {total_char_count}")
        # 2. 空白改行除去文字数
        ex_space_count = len(self._exclude_spaces(content))
        # 3. 基本記号除去文字数
        # 4. 句読点記号除去文字数
        return CountState(
            count_type=CountType.INDIVIDUAL,
            file_name=file_path,
            total=total_char_count,
            exclude_togaki=0,
            exclude_marks=0,
        )

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
    
    def _exclude_parentheses_chars(self, content: str) -> str:
        """（）で囲まれた部分の削除"""
        # 2. （文字列）で囲まれた部分を削除 (※全角括弧を想定)
        # \(.*?\) : （ ）で囲まれた中身（最短一致）
        return re.sub(r'（.*?）', '', content)
    
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


def count_characters(target_directory, output_file, exclude_chars):
    # 対象の拡張子
    extensions = ['*.txt', '*.md']
    total_chars_full = 0
    total_chars_final = 0
    
    # 記号除外用の正規表現パターン
    exclude_pattern = "|".join(re.escape(char) for char in exclude_chars)
    
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(target_directory, '**', ext), recursive=True))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{'ファイルパス':<40} | {'総文字数':>8} | {'調整後文字数':>8}\n")
        f.write("-" * 70 + "\n")
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    char_count_full = len(content)
                    
                    # --- 処理プロセス ---
                    
                    # 1. 行頭が「#」で始まる行、または「（」で始まる行を削除
                    # ^#.* : 行頭が#で始まる行
                    # ^\(.* : 行頭が(で始まる行
                    lines = content.splitlines()
                    filtered_lines = [
                        line for line in lines 
                        if not (line.strip().startswith('#') or line.strip().startswith('（'))
                    ]
                    content_processed = "\n".join(filtered_lines)
                    
                    # 2. （文字列）で囲まれた部分を削除 (※全角括弧を想定)
                    # \(.*?\) : （ ）で囲まれた中身（最短一致）
                    content_processed = re.sub(r'（.*?）', '', content_processed)
                    
                    # 3. 指定した特定の記号を除去
                    content_processed = re.sub(exclude_pattern, '', content_processed)
                    
                    # 4. 最後にスペース・タブ・改行を削除
                    content_final = re.sub(r'\s', '', content_processed)
                    char_count_final = len(content_final)
                    
                    total_chars_full += char_count_full
                    total_chars_final += char_count_final
                    
                    relative_path = os.path.relpath(file_path, target_directory)
                    f.write(f"{relative_path[:40]:<40} | {char_count_full:8,d} | {char_count_final:10,d}\n")
                    
            except Exception as e:
                print(f"エラー: {file_path} - {e}")
        
        f.write("-" * 70 + "\n")
        f.write(f"{'合計':<40} | {total_chars_full:8,d} | {total_chars_final:10,d}\n")
    
    print(f"完了しました。結果: {output_file}")

# --- 設定 ---
output_filename = 'count_result.txt'
exclude_chars = ['！', '？', '♡', '♥', '♪', '★', '☆', '!', '?',]

if __name__ == "__main__":
    counter = CharCounter("build")
    counter.count_characters(output_filename, exclude_chars)

