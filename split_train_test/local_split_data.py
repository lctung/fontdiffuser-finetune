import os
import shutil
import random
import argparse

# 建立參數解析器
parser = argparse.ArgumentParser(description="從來源資料夾中挑選圖片並複製")
parser.add_argument("--folder_param", type=str, required=True, help="請輸入來源資料夾，例如 112598018")
args = parser.parse_args()

# 使用傳入的參數
folder_param = args.folder_param.strip()

# 定義來源資料夾與目標資料夾
source_dir1 = folder_param
source_dir2 = "Noto_Sans_TC_JPG"
target_dir1 = os.path.join("train", "TargetImage", folder_param)
target_dir2 = os.path.join("train", "ContentImage")

os.makedirs(target_dir1, exist_ok=True)
os.makedirs(target_dir2, exist_ok=True)

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'

def decode_filename(filename):
    base, _ = os.path.splitext(filename)
    if base.startswith("U+"):
        try:
            code = base[2:]
            return chr(int(code, 16))
        except ValueError:
            return None
    return None

def get_chinese_images(directory):
    images = {}
    for file in os.listdir(directory):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            char = decode_filename(file)
            if char and is_chinese(char):
                if char not in images:
                    images[char] = os.path.join(directory, file)
    return images

images1 = get_chinese_images(source_dir1)
images2 = get_chinese_images(source_dir2)

common_chars = list(set(images1.keys()) & set(images2.keys()))
print("共同符合條件的中文檔案數量:", len(common_chars))

select_count = min(800, len(common_chars))
selected_chars = random.sample(common_chars, select_count)
print("隨機挑選的中文檔案:", selected_chars)

with open("train.txt", "w", encoding="utf-8") as f:
    for char in selected_chars:
        f.write(f"{char}\n")

for char in selected_chars:
    source_path1 = images1[char]
    new_name1 = f"{folder_param}+{char}.jpg"
    target_path1 = os.path.join(target_dir1, new_name1)
    shutil.copy2(source_path1, target_path1)

    source_path2 = images2[char]
    new_name2 = f"{char}.jpg"
    target_path2 = os.path.join(target_dir2, new_name2)
    shutil.copy2(source_path2, target_path2)

print("檔案複製與重新命名完成！")

# 修正路徑：從 split_train_test 目錄向上一層，然後進入 data_examples/train
final_target = os.path.join("..", "data_examples", "train")
final_target_abs = os.path.abspath(final_target)

print(f"目標路徑（相對）：{final_target}")
print(f"目標路徑（絕對）：{final_target_abs}")

# 檢查並建立父目錄
parent_dir = os.path.dirname(final_target_abs)
if not os.path.exists(parent_dir):
    print(f"建立父目錄：{parent_dir}")
    os.makedirs(parent_dir, exist_ok=True)

# 如果目標目錄存在，先刪除
if os.path.exists(final_target_abs):
    print(f"刪除既有目錄：{final_target_abs}")
    shutil.rmtree(final_target_abs)

# 複製 train 資料夾
source_train = os.path.abspath("train")
print(f"來源路徑：{source_train}")

if os.path.exists(source_train):
    shutil.copytree(source_train, final_target_abs)
    print(f"train 資料夾已成功複製到：{final_target_abs}")
else:
    print(f"錯誤：來源 train 資料夾不存在：{source_train}")
