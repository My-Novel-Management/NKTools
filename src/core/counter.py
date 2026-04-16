import os
import glob
import re
import pandas as pd
from dataclasses import dataclass, field
from collections import defaultdict

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
    PUNCTUATIONS = ['、', '。', '.', ',', '・']
    PARENTHESES = ['(', ')', '「', '」', '『', '』', '【', '】']

    def count_characters(self, output_file: str, exclude_chars: list):
        """
        対象のフォルダ内のファイルの文字数を計算する
        """
        # 記号除外用の正規表現パターン作成
        exclude_pattern = self._get_exclude_pattern(exclude_chars)

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
                        state = self._get_count_state(file_path, content, exclude_pattern, is_skip_dialogues=False)
                        # 状態をリストに追加
                        states.append(state)
                except Exception as e:
                    print(f"エラー: {file_path} - {e}")
        if states:
            # 総合stateを算出し、保存
            total_state = self._total_count_of_states(states)
            # TODO: Speaker毎のTotalを計算する
            states.append(total_state)
            df = pd.DataFrame(states)
            # 保存する
            save_path = f"{self.save_dir}/{output_file}.csv"
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(df)
            # キャラ別集計のみを別のCSVで出す場合
            speaker_data = []
            for speaker, s in total_state.dialogues.items():
                speaker_data.append({
                    "Speaker": speaker,
                    "Total": s.total,
                    "Ex_Space": s.exclude_space, # 空白抜き
                    "Ex_Togaki": s.exclude_togaki, # ト書き抜き
                    "Ex_Marks": s.exclude_marks # 記号抜き
                })
            df_speakers = pd.DataFrame(speaker_data)
            df_speakers.to_csv(f"{self.save_dir}/speaker_totals.csv", index=False, encoding="utf-8-sig")
            print(df_speakers)

    def _get_count_state(self, file_path: str, content: str, exclude_pattern: str, is_skip_dialogues: bool=True) -> CountState:
        """コンテンツの文字数状況の取得"""
        # 1. 総文字数
        total_char_count = self._get_total_char_count(content)
        # 2. 空白改行除去文字数
        ex_space_count = len(self._exclude_spaces(content))
        # 3. 基本記号除去文字数
        ex_togai_count = len(self._get_exclude_togakis(content))
        # 4. 句読点記号除去文字数
        ex_marks_count = len(self._get_exclude_all_marks(content, exclude_pattern))
        # 5. 話者別文字数カウント（記号、句読点除去）
        dialogues = {}
        if not is_skip_dialogues:
            dialogues = self._count_each_charas_dialogue(file_path, content, exclude_pattern)
        return CountState(
            count_type=CountType.INDIVIDUAL,
            file_name=file_path,
            total=total_char_count,
            exclude_space=ex_space_count,
            exclude_togaki=ex_togai_count,
            exclude_marks=ex_marks_count,
            dialogues=dialogues
        )
    
    def _total_count_of_states(self, state_list: list[CountState]) -> CountState:
        """すべてのStateの合計をCountStateにして返す（dialoguesの集計も行わせる）"""
        total_state = CountState(count_type=CountType.TOTAL, file_name=self.base_path)
        total_state.total = sum(s.total for s in state_list)
        total_state.exclude_space = sum(s.exclude_space for s in state_list)
        total_state.exclude_togaki = sum(s.exclude_togaki for s in state_list)
        total_state.exclude_marks = sum(s.exclude_marks for s in state_list)
        
        # キャラ別合計を算出
        total_state.dialogues = self._aggregate_dialogues(state_list)
        
        return total_state

    def _count_each_charas_dialogue(self, file_path: str, content: str, exclude_pattern: str) -> dict:
        """キャラ毎に分割して、それの当該文字数をカウントした辞書を返す"""
        # キャラ毎の文字数を収める辞書作成
        char_contents = defaultdict(str)
        current_speaker = "指定なし" # キャラ指定外のカウント用
        # 行分割してキャラ毎に分ける
        lines = content.splitlines(keepends=True)
        for line in lines:
            stripped_line = line.strip()
            # 空行は飛ばす
            if not stripped_line:
                continue
            # キャラクター行判定（//キャラ：）
            name_match = re.match(r'^//(.+?)[:：]', stripped_line)
            if name_match:
                current_speaker = name_match.group(1)
                continue # 名前行そのものはここで削除

            # 現在のスピーカーに追加
            char_contents[current_speaker] += line
        # 分割されたスピーカー毎に、State処理
        char_counts = {}
        for speaker, cont in char_contents.items():
            if cont:
                state = self._get_count_state(file_path, cont, exclude_pattern, is_skip_dialogues=True)
                char_counts[speaker] = state
            else:
                # 空の場合は 0 クリアした State を入れる
                char_counts[speaker] = CountState(file_name=file_path)
        return char_counts

    
    def _get_exclude_togakis(self, content: str) -> str:
        # 不要行削除
        tmp_cond1 = self._exclude_head_of_line(content)
        # //指示行も削除
        tmp_cond2 = self._exclude_direction_headline(tmp_cond1)
        # （）文字の削除
        tmp_cond3 = self._exclude_parentheses_chars(tmp_cond2)
        # 括弧記号の削除
        tmp_cond4 = self._exclude_parentheses_marks(tmp_cond3)
        # 最後に空白削除
        return self._exclude_spaces(tmp_cond4)
    
    def _get_exclude_all_marks(self, content: str, exclude_pattern) -> str:
        """ト書きと句読点、記号除去する"""
        # 不要行削除
        tmp_cond0 = self._exclude_head_of_line(content)
        # //指示行も削除
        tmp_cond1 = self._exclude_direction_headline(tmp_cond0)
        # （）文字の削除
        tmp_cond2 = self._exclude_parentheses_chars(tmp_cond1)
        # 句読点の削除
        tmp_cond3 = self._exclude_punctuations(tmp_cond2)
        # 括弧記号の削除
        tmp_cond4 = self._exclude_parentheses_marks(tmp_cond3)
        # 指定文字の削除
        tmp_cond5 = self._exclude_special_patterns(tmp_cond4, exclude_pattern)
        # 最後に空白削除
        return self._exclude_spaces(tmp_cond5)

    def _get_exclude_pattern(self, exclude_chars: list) -> str:
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
        patterns = self._get_exclude_pattern(self.PUNCTUATIONS)
        return self._exclude_special_patterns(content, patterns)

    def _exclude_parentheses_marks(self, content: str) -> str:
        """文中の括弧記号の除去"""
        patterns = self._get_exclude_pattern(self.PARENTHESES)
        return self._exclude_special_patterns(content, patterns)
    
    def _exclude_special_patterns(self, content: str, exclude_pattern: str):
        """指定文字の削除"""
        return re.sub(exclude_pattern, '', content)
    
    def _exclude_spaces(self, content: str) -> str:
        """スペース、タブ、改行の削除"""
        return re.sub(r'\s', '', content)

    def _aggregate_dialogues(self, state_list: list[CountState]) -> dict:
        """
        複数のStateからキャラクター別の文字数を集計して合算する
        """
        total_dialogues = defaultdict(lambda: {
            'total': 0,
            'exclude_space': 0,
            'exclude_togaki': 0,
            'exclude_marks': 0
        })

        for state in state_list:
            if not state.dialogues:
                continue
            
            for speaker, s in state.dialogues.items():
                # 各項目の数値を加算
                total_dialogues[speaker]['total'] += s.total
                total_dialogues[speaker]['exclude_space'] += s.exclude_space
                total_dialogues[speaker]['exclude_togaki'] += s.exclude_togaki
                total_dialogues[speaker]['exclude_marks'] += s.exclude_marks

        # 最終的に CountState の辞書形式に変換して返す
        result = {}
        for speaker, counts in total_dialogues.items():
            result[speaker] = CountState(
                count_type=CountType.TOTAL,
                file_name="Total (All Files)",
                **counts
            )
        return result

if __name__ == "__main__":
    # --- 設定 ---
    output_filename = 'count_result'
    exclude_chars = ['！', '？', '♡', '♥', '♪', '★', '☆', '!', '?',]

    counter = CharCounter("build")
    counter.count_characters(output_filename, exclude_chars)

