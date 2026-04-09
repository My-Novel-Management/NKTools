import os
import glob
import re
import random
import sys # コマンドライン引数を扱うために追加
from moan_generator import generate_fellatio, generate_onomatopoeia

EXTENTIONS = ['*.txt', '*.md']
TARGET_WORD = "（喘ぎ）"
TARGET_WORD_FELA = "（フェラ音）"
TARGET_WORD_OHO = "（オホ声）"

# （鳴き声） または （鳴き声1） または （鳴き声１） にマッチ
# pattern = r"（鳴き声[1１]?）"

ONOM_FILENAME = "data/moan.txt"
FELLA_FILENAME = "data/fella.txt"
OHO_FILENAME = "data/oho_moan.txt"

def load_wordlist(list_file):
    """
    テキストファイルから一行ずつオノマトペを読み込んでリストにする
    """
    if not os.path.exists(list_file):
        print(f"警告: リストファイル '{list_file}' が見つかりません。デフォルトのリストを使用します。")
        return ["ん…", "あむ、", "じゅぽ…"] # 最低限のフォールバック
    
    with open(list_file, "r", encoding="utf-8") as f:
        # 空行や前後の空白を除去してリスト化
        words = [line.strip() for line in f if line.strip()]
    
    if not words:
        print(f"エラー: '{list_file}' が空です。")
        sys.exit(1)
        
    return words

def replace_onom_all_files(base_path: str="build"):
    """フォルダ内の喘ぎとフェラ音を追加"""
    files = []
    words_onom = load_wordlist(ONOM_FILENAME)
    words_fella = load_wordlist(FELLA_FILENAME)
    words_oho = load_wordlist(OHO_FILENAME)

    for ext in EXTENTIONS:
        files.extend(glob.glob(os.path.join(base_path, '**', ext), recursive=True))
        for file_path in files:
            try:
                # ファイルの読み込み
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # フェラ音
                    tmp_content = replace_moan(TARGET_WORD_FELA, words_fella, content)
                    # 喘ぎ
                    tmp_content = replace_moan(TARGET_WORD, words_onom, tmp_content)
                    # オホ声
                    print(f"changed: {len(tmp_content)}")
                # 上書き保存（または別名保存も可能）
                output_path = file_path.replace('build', 'results')
                with open(f"{output_path}", "w", encoding="utf-8") as f2:
                    f2.write(tmp_content)
                print(f"完了: '{file_path}'->{output_path} 内の置換処理が終わりました。")
            except FileNotFoundError:
                print(f"エラー: ファイル '{file_path}' が見つかりません。")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")

    print("終了しました")

def replace_moan(target, wordlist, content):
    """ファイル内の該当箇所を置換する"""
    return re.sub(
        re.escape(target),
        lambda m: m.group(0) + "\n" + random.choice(wordlist),
        content
    )

def replace_onomatopoeia_in_file(content):
    """
    ファイル内の「（喘ぎ）」を「（喘ぎ）オノマトペ」に置換する
    """
    # 正規表現の置換機能を利用（マッチするたびに生成関数を呼び出す）
    # 置換後の文字列 = 元の単語 + 生成したオノマトペ
    new_content = re.sub(
        re.escape(TARGET_WORD),
        lambda m: m.group(0) + "\n" + "".join(generate_onomatopoeia(random.randint(1, 5))),
        content
    )
    new_content_fela = re.sub(
        re.escape(TARGET_WORD_FELA),
        lambda m: m.group(0) + "\n" + "".join(generate_fellatio(random.randint(1, 5))),
        new_content
    )
    return new_content_fela

# --- 実行セクション ---
if __name__ == "__main__":
    replace_onom_all_files()
