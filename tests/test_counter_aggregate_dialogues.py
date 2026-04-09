import pytest
from collections import defaultdict
from src.core.counter import CharCounter, CountState, CountType

class TestCharCounterAggregate:
    @pytest.fixture
    def counter(self):
        return CharCounter(base_path="test_project", save_dir="test_results")

    @pytest.fixture
    def mock_states(self):
        """
        2つのファイル分のカウント結果を模したテストデータ
        """
        # ファイル1の結果
        state1 = CountState(
            count_type=CountType.INDIVIDUAL,
            file_name="file1.txt",
            total=100,
            exclude_marks=80,
            dialogues={
                "主人公": CountState(total=50, exclude_marks=40),
                "ヒロイン": CountState(total=30, exclude_marks=25)
            }
        )
        
        # ファイル2の結果
        state2 = CountState(
            count_type=CountType.INDIVIDUAL,
            file_name="file2.txt",
            total=200,
            exclude_marks=150,
            dialogues={
                "主人公": CountState(total=100, exclude_marks=80),
                "モブ": CountState(total=20, exclude_marks=15)
            }
        )
        
        return [state1, state2]

    def test_aggregate_dialogues(self, counter, mock_states):
        """
        キャラごとの合算値が正しいかテスト
        """
        # メソッドの実行
        total_dialogues = counter._aggregate_dialogues(mock_states)

        # 1. 登場キャラ数が正しいか (主人公、ヒロイン、モブの3人)
        assert len(total_dialogues) == 3
        assert "主人公" in total_dialogues
        assert "ヒロイン" in total_dialogues
        assert "モブ" in total_dialogues

        # 2. 主人公の合算値チェック (50 + 100 = 150)
        assert total_dialogues["主人公"].total == 150
        assert total_dialogues["主人公"].exclude_marks == 120

        # 3. ヒロインの合算値チェック (ファイル1のみ登場)
        assert total_dialogues["ヒロイン"].total == 30
        assert total_dialogues["ヒロイン"].exclude_marks == 25

        # 4. count_type が TOTAL になっているか
        assert total_dialogues["主人公"].count_type == CountType.TOTAL

    def test_total_count_of_states_with_dialogues(self, counter, mock_states):
        """
        全体の集計メソッドを実行したとき、dialoguesも含まれているかテスト
        """
        total_state = counter._total_count_of_states(mock_states)

        # 全体合計のチェック (100 + 200 = 300)
        assert total_state.total == 300
        
        # 全体Stateの中にキャラ別集計が含まれているか
        assert "主人公" in total_state.dialogues
        assert total_state.dialogues["主人公"].total == 150