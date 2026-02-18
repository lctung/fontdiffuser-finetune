import os

# 安裝 gdown（僅第一次執行需要）
try:
    import gdown
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "gdown"])
    import gdown

# 檔案 ID 與對應名稱
files = {
    "1UF4nIcL3PRJeQOQOPFFuGzj30v67rlNn": "ckpt/scr_210000.pth",
    "1XIY1QnEIKYmciFnxJ0r48f2LpS8KfZXh": "ckpt/unet.pth",
    "1-ywYwsfr8ryE86FgY9Xlub2uhPzZ_WWR": "ckpt/style_encoder.pth",
    "1xX-yTNXhniBNR9R5sc1v7-Ghd64HsKIo": "ckpt/content_encoder.pth",
}

# 下載檔案
for file_id, output_path in files.items():
    print(f"Downloading to {output_path} ...")
    gdown.download(id=file_id, output=output_path, quiet=False)
