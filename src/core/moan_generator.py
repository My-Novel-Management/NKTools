import random

def generate_onomatopoeia(count=10):
    # オノマトペの構成要素
    bases = ["あ", "あぁ", "あん", "い", "う", "は", "ふ", "ん"]
    suffixes = ["ぁ", "っ", "…", "、", "！", "〜"]
    breaths = ["はぁ", "くっ", "ふぅ", "ひっ"]
    
    results = []
    
    for _ in range(count):
        # パターンの抽選
        choice = random.random()
        
        if choice < 0.4:
            # 短い溜め: 「あっ」「はっ」
            word = random.choice(bases) + random.choice(suffixes[:2])
        elif choice < 0.7:
            # 連続・吐息: 「はぁ、っ…」「あ、あ…」
            word = random.choice(breaths) + random.choice(suffixes) + random.choice(suffixes)
        else:
            # 長い余韻: 「あん…っ」「ふぅ〜…」
            word = random.choice(bases) + "ん" + random.choice(suffixes[1:])
            
        results.append(word)
    
    return results

def generate_fellatio(count=10):
    """
    フェラチオ時の水音や密着感のあるオノマトペを1つ生成する
    """
    # カテゴリ別のパーツ
    deep_parts = ["ぐ、", "ぐっ…", "ぐぽっ", "ごふっ", "んぐ、"]
    wet_parts = ["じゅぽ…", "ちゅぱッ", "じゅるぅ", "んちゅ…", "じゅっ"]
    lick_parts = ["れろ…", "れろれろれろッ", "ぺろ…", "じゅり…"]
    short_parts = ["あむ、", "ん…", "んんっ", "はふっ"]

    results = []
    
    for _ in range(count):
        # パターンの抽選
        choice = random.random()

        if choice < 0.3:
            # 舐める・絡める系
            word = random.choice(lick_parts)
        elif choice < 0.6:
            # 深く突く・飲み込む系
            word = random.choice(deep_parts) + random.choice(["", "んぅ…", "っ！"])
        elif choice < 0.85:
            # 水音・吸入系
            word = random.choice(wet_parts)
        else:
            # 溜め・短い反応
            word = random.choice(short_parts)

        results.append(word)
    
    return results
    
def save_to_text(save_dir="results", num_lines=20):
    """
    ランダムなオノマトペを生成してテキストファイルに保存する
    """
    save_file_onom = f"{save_dir}/onom.txt"
    save_file_fella = f"{save_dir}/fella.txt"

    try:
        with open(save_file_onom, "w", encoding="utf-8") as f:
            for _ in range(num_lines):
                # 1行に1〜3個のフレーズを並べる
                line_data = generate_onomatopoeia(random.randint(1, 10))
                f.write(" ".join(line_data) + "\n")
        
        print(f"成功: '{save_file_onom}' に {num_lines} 行のデータを出力しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    try:
        with open(save_file_fella, "w", encoding="utf-8") as f:
            for _ in range(num_lines):
                # 1行に1〜3個のフレーズを並べる
                line_data = generate_fellatio(random.randint(1, 10))
                f.write(" ".join(line_data) + "\n")
        
        print(f"成功: '{save_file_fella}' に {num_lines} 行のデータを出力しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 実行
if __name__ == "__main__":
    save_to_text("results", 200)
