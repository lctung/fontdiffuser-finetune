@echo off
python sample.py ^
    --ckpt_dir="ckpt/" ^
    --style_image_path="data_examples/sampling/example_style.jpg" ^
    --save_image ^
    --character_input ^
    --character_list_path="characters.txt" ^
    --save_image_dir="outputs_generater_character_list/" ^
    --device="cuda:0" ^
    --algorithm_type="dpmsolver++" ^
    --guidance_type="classifier-free" ^
    --guidance_scale=7.5 ^
    --num_inference_steps=20 ^
    --method="multistep"
