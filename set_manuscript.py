handwriting_path = r"./0_written_newline.txt" 
target_file_path = r"./3_notosanschar_newline.txt"
output_file_path = r"./test"

with open(handwriting_path, "r", encoding="utf-8") as file:
    text = file.read()
with open(target_file_path, "r", encoding="utf-8") as file:
    target_content = "".join(file.read().split())

clean_text = "".join(text.lstrip('\ufeff')  .split()) # delete all elements which is not char
unique_characters = set(clean_text)

set_target_file = set(target_content)


unseen_char_simple = set_target_file - unique_characters

with open(output_file_path, "w", encoding="utf-8") as file:
    file.write("\n".join(sorted(unseen_char_simple)))

print(f"target: ({target_file_path}): ", len(set_target_file))
print("扣掉手寫過的 字數共有: ", len(unseen_char_simple))

