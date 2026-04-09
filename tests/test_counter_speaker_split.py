import pytest
from src.core.counter import CharCounter

class TestSpeakerSplit:
    @pytest.fixture
    def counter(self):
        # テスト用のインスタンス
        return CharCounter(base_path="", save_dir="test_results")

    @pytest.fixture
    def scenario_text(self):
        """
        テスト用のシナリオデータ
        - 指定なし（冒頭）
        - キャラA（複数回登場）
        - キャラB（1回登場）
        """
        return (
            "ここまでは指定なしの地の文です。\n"
            "//キャラA：\n"
            "こんにちは！\n"
            "（ト書き）\n"
            "//キャラB：\n"
            "お疲れ様です、。！\n"
            "//キャラA：\n"
            "また明日。「」"
        )

    def test_count_each_charas_dialogue_keys(self, counter, scenario_text):
        """
        正しく話者名が辞書のキーとして抽出されているかテスト
        """
        exclude_chars = ['！', '？']
        pattern = counter._get_exclude_pattern(exclude_chars)
        
        # メソッド実行
        # is_skip_dialogues=True にして再帰ループを防ぐ
        dialogue_counts = counter._count_each_charas_dialogue("test.txt", scenario_text, pattern)

        # 1. 期待される話者がすべて含まれているか
        assert "指定なし" in dialogue_counts
        assert "キャラA" in dialogue_counts
        assert "キャラB" in dialogue_counts
        
        # 2. 存在しないはずの話者が混じっていないか
        assert "ト書き" not in dialogue_counts

    def test_speaker_character_calculation(self, counter, scenario_text):
        """
        特定のキャラの文字数計算が正しいかテスト
        """
        exclude_chars = ['！'] # びっくりマークを除外
        pattern = counter._get_exclude_pattern(exclude_chars)
        
        dialogue_counts = counter._count_each_charas_dialogue("test.txt", scenario_text, pattern)

        # キャラAの検証
        # 内容：「こんにちは！」「また明日。「」」
        # ト書き（）や「」、！を除去した後の文字数を確認
        char_a_state = dialogue_counts["キャラA"]
        
        # 「こんにちは」 (5文字) + 「また明日」 (4文字) = 9文字
        # ※ //キャラA： 行自体はカウントに含まれない
        assert char_a_state.exclude_marks == 9

        # キャラBの検証
        # 内容：「お疲れ様です、。！」
        # 「お疲れ様です」 (6文字) 、句読点と！は除去される
        char_b_state = dialogue_counts["キャラB"]
        assert char_b_state.exclude_marks == 6

    def test_no_speaker_text(self, counter):
        """
        話者指定がない行が「指定なし」に集計されるかテスト
        """
        text = "冒頭の文\n//キャラA：台詞"
        pattern = "" # 記号なし
        
        dialogue_counts = counter._count_each_charas_dialogue("test.txt", text, pattern)
        
        assert "指定なし" in dialogue_counts
        # 「冒頭の文」のみカウントされる（4文字）
        assert dialogue_counts["指定なし"].exclude_marks == 4