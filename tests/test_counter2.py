import pytest
from src.core.counter import CharCounter

class TestCharCounter:
    @pytest.fixture
    def counter(self):
        # テスト用のインスタンスを作成
        return CharCounter(base_path="", save_dir="test_results")

    @pytest.fixture
    def sample_text(self):
        # テスト用の混在テキスト
        # 1. # タイトル (除外対象)
        # 2. //話者： (除外対象)
        # 3. （ト書き） (除外対象)
        # 4. 「台詞、。！？」 (句読点と記号のテスト用)
        return (
            "# シナリオタイトル\n"
            "//キャラ：名前\n"
            "（ト書きが入ります）\n"
            "「こんにちは、。！？」\n"
            "（笑いながら）「元気ですか？」"
        )

    def test_get_exclude_togakis(self, counter, sample_text):
        """
        ト書き・特殊行は消えるが、句読点や記号は残るはずのテスト
        """
        result = counter._get_exclude_togakis(sample_text)
        
        # 期待される挙動:
        # ・# 行は消える
        # ・// 行は消える
        # ・（）とその中身は消える
        # ・「」は消える (PARENTHESESに含まれるため)
        # ・、。！？ は「残る」
        
        assert "シナリオタイトル" not in result
        assert "ト書き" not in result
        assert "こんにちは" in result
        assert "、" in result
        assert "。" in result
        assert "！" in result
        assert "？" in result

    def test_get_exclude_all_marks(self, counter, sample_text):
        """
        ト書きに加え、句読点や指定記号もすべて消えるはずのテスト
        """
        exclude_chars = ['！', '？']
        pattern = counter._get_exclude_pattern(exclude_chars)
        
        result = counter._get_exclude_all_marks(sample_text, pattern)
        
        # 期待される挙動:
        # ・ト書き等は当然消える
        # ・「、」「。」も消える (_exclude_punctuations)
        # ・「！」「？」も消える (_exclude_special_patterns)
        
        assert "こんにちは" in result
        assert "、" not in result
        assert "。" not in result
        assert "！" not in result
        assert "？" not in result
        assert "「" not in result

    def test_comparison_between_methods(self, counter):
        """
        両メソッドの結果に差が出ることを直接比較するテスト
        """
        text = "「あ、。！？」"
        exclude_chars = ['！', '？']
        pattern = counter._get_exclude_pattern(exclude_chars)

        togaki_only = counter._get_exclude_togakis(text)
        all_marks = counter._get_exclude_all_marks(text, pattern)

        # 句読点や記号が残っているため、togaki_onlyの方が長くなるはず
        assert len(togaki_only) > len(all_marks)
        assert "、" in togaki_only
        assert "、" not in all_marks