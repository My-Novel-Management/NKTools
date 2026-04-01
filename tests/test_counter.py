import pytest
import sys
import os

# srcディレクトリをモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.counter import count_characters_by_script

# テスト用のダミーファイルを作成するフィクスチャ
@pytest.fixture
def sample_script_file(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "test_script.txt"
    content = """
# タイトル行（削除対象）
（ト書き：これは削除対象）
//キャラA：
こんにちは！
//キャラB：
（笑）そうですね♪
# 次の行
//キャラA：
また明日。
"""
    f.write_text(content, encoding='utf-8')
    return f, d

def test_character_count(sample_script_file):
    script_file, target_dir = sample_script_file
    output_file = target_dir / "result.txt"
    exclude_chars = ['！', '？', '♡', '♪', '★', '☆', '（', '）', '（', '）']
    
    # 関数の実行
    count_characters_by_script(str(target_dir), str(output_file), exclude_chars)
    
    # 結果の検証
    with open(output_file, 'r', encoding='utf-8') as f:
        results = f.read()
    
    # キャラAの文字数: "こんにちは" (5文字) + "また明日" (4文字) = 9文字
    # キャラBの文字数: "そうですね" (5文字)
    assert "キャラA" in results
    assert "9" in results
    assert "キャラB" in results
    assert "5" in results