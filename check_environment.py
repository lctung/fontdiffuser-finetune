import os
import sys
import subprocess
import importlib
import re


# ============================================================
# 設定
# ============================================================

# requirements.txt 的位置
REQUIREMENTS_FILE = "requirements.txt"

# 預訓練模型
CHECKPOINTS = {
    "scr_210000.pth": "ckpt/scr_210000.pth",
    "unet.pth": "ckpt/unet.pth",
    "style_encoder.pth": "ckpt/style_encoder.pth",
    "content_encoder.pth": "ckpt/content_encoder.pth",
}

# PyTorch 指定版本
EXPECTED_TORCH = "2.0.1"
EXPECTED_TORCHVISION = "0.15.2"
EXPECTED_TORCHAUDIO = "2.0.2"

# requirements.txt 中的套件名稱
# 用 import name 對應 pip package name
PACKAGE_IMPORT_NAMES = {
    "accelerate": "accelerate",
    "aiofiles": "aiofiles",
    "altair": "altair",
    "annotated-types": "annotated_types",
    "anyio": "anyio",
    "attrs": "attrs",
    "certifi": "certifi",
    "charset-normalizer": "charset_normalizer",
    "click": "click",
    "colorama": "colorama",
    "contourpy": "contourpy",
    "cycler": "cycler",
    "diffusers": "diffusers",
    "einops": "einops",
    "exceptiongroup": "exceptiongroup",
    "fastapi": "fastapi",
    "ffmpy": "ffmpy",
    "filelock": "filelock",
    "fonttools": "fontTools",
    "fsspec": "fsspec",
    "gradio": "gradio",
    "gradio_client": "gradio_client",
    "h11": "h11",
    "hjson": "hjson",
    "httpcore": "httpcore",
    "httpx": "httpx",
    "huggingface-hub": "huggingface_hub",
    "idna": "idna",
    "importlib_metadata": "importlib_metadata",
    "importlib_resources": "importlib_resources",
    "info-nce-pytorch": "info_nce_pytorch",
    "Jinja2": "jinja2",
    "jsonschema": "jsonschema",
    "jsonschema-specifications": "jsonschema_specifications",
    "kiwisolver": "kiwisolver",
    "kornia": "kornia",
    "kornia_rs": "kornia_rs",
    "markdown-it-py": "markdown_it",
    "MarkupSafe": "markupsafe",
    "matplotlib": "matplotlib",
    "mdurl": "mdurl",
    "mpmath": "mpmath",
    "msgpack": "msgpack",
    "narwhals": "narwhals",
    "networkx": "networkx",
    "ninja": "ninja",
    "numpy": "numpy",
    "opencv-python": "cv2",
    "orjson": "orjson",
    "packaging": "packaging",
    "pandas": "pandas",
    "pillow": "PIL",
    "psutil": "psutil",
    "py-cpuinfo": "cpuinfo",
    "pydantic": "pydantic",
    "pydantic_core": "pydantic_core",
    "pydub": "pydub",
    "pygame": "pygame",
    "Pygments": "pygments",
    "pyparsing": "pyparsing",
    "python-dateutil": "dateutil",
    "python-multipart": "multipart",
    "pytz": "pytz",
    "PyYAML": "yaml",
    "referencing": "referencing",
    "regex": "regex",
    "requests": "requests",
    "rich": "rich",
    "rpds-py": "rpds",
    "safetensors": "safetensors",
    "semantic-version": "semantic_version",
    "shellingham": "shellingham",
    "six": "six",
    "sniffio": "sniffio",
    "starlette": "starlette",
    "sympy": "sympy",
    "tokenizers": "tokenizers",
    "tomlkit": "tomlkit",
    "tqdm": "tqdm",
    "transformers": "transformers",
    "typer": "typer",
    "typing_extensions": "typing_extensions",
    "tzdata": "tzdata",
    "urllib3": "urllib3",
    "uvicorn": "uvicorn",
    "websockets": "websockets",
    "zipp": "zipp",
}


# ============================================================
# 顏色
# ============================================================

USE_COLOR = sys.stdout.isatty()


def green(text):
    return f"\033[92m{text}\033[0m" if USE_COLOR else text


def red(text):
    return f"\033[91m{text}\033[0m" if USE_COLOR else text


def yellow(text):
    return f"\033[93m{text}\033[0m" if USE_COLOR else text


def cyan(text):
    return f"\033[96m{text}\033[0m" if USE_COLOR else text


# ============================================================
# 工具函式
# ============================================================

results = []


def ok(message):
    print(f"[OK]   {message}")
    results.append(True)


def fail(message):
    print(f"[FAIL] {message}")
    results.append(False)


def warn(message):
    print(f"[WARN] {message}")


def get_installed_version(package_name):
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()

    except Exception:
        pass

    return None

# ============================================================
# 1. Python
# ============================================================

def check_python():
    print("\n" + "=" * 60)
    print("1. Python")
    print("=" * 60)

    version = sys.version.split()[0]

    print(f"Python version: {version}")

    # 不強制指定 Python 版本，只顯示
    ok(f"Python {version}")


# ============================================================
# 2. requirements.txt
# ============================================================

def parse_requirements():
    requirements = {}

    if not os.path.exists(REQUIREMENTS_FILE):
        fail(f"{REQUIREMENTS_FILE} not found")
        return requirements

    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # 跳過空白與註解
            if not line or line.startswith("#"):
                continue

            # 只處理 == 版本
            if "==" not in line:
                continue

            package, version = line.split("==", 1)

            package = package.strip()
            version = version.strip()

            requirements[package] = version

    return requirements


def check_requirements():
    print("\n" + "=" * 60)
    print("2. requirements.txt")
    print("=" * 60)

    requirements = parse_requirements()

    if not requirements:
        return

    total = len(requirements)
    passed = 0

    print(f"Found {total} required packages.\n")

    for package, expected_version in requirements.items():

        installed_version = get_installed_version(package)

        if installed_version is None:
            print(
                f"[FAIL] {package:<25} "
                f"NOT INSTALLED"
            )
            continue

        if installed_version == expected_version:
            print(
                f"[OK]   {package:<25} "
                f"{installed_version}"
            )
            passed += 1
        else:
            print(
                f"[FAIL] {package:<25} "
                f"expected {expected_version}, "
                f"found {installed_version}"
            )

    print()
    print(f"requirements.txt: {passed}/{total} packages OK")

    if passed == total:
        ok("All requirements.txt packages are correct")
    else:
        fail("Some requirements.txt packages are missing or have wrong versions")


# ============================================================
# 3. PyTorch
# ============================================================

def check_pytorch():
    print("\n" + "=" * 60)
    print("3. PyTorch")
    print("=" * 60)

    try:
        import torch
    except ImportError:
        fail("torch is not installed")
        return None

    torch_version = torch.__version__.split("+")[0]

    print(f"torch version:       {torch.__version__}")

    if torch_version == EXPECTED_TORCH:
        ok(f"torch {EXPECTED_TORCH}")
    else:
        fail(
            f"torch version mismatch "
            f"(expected {EXPECTED_TORCH}, found {torch_version})"
        )

    # torchvision
    try:
        import torchvision

        torchvision_version = torchvision.__version__.split("+")[0]

        print(f"torchvision version: {torchvision.__version__}")

        if torchvision_version == EXPECTED_TORCHVISION:
            ok(f"torchvision {EXPECTED_TORCHVISION}")
        else:
            fail(
                f"torchvision version mismatch "
                f"(expected {EXPECTED_TORCHVISION}, "
                f"found {torchvision_version})"
            )

    except ImportError:
        fail("torchvision is not installed")

    return torch


# ============================================================
# 4. CUDA / GPU
# ============================================================

def check_cuda(torch):
    print("\n" + "=" * 60)
    print("4. CUDA / GPU")
    print("=" * 60)

    if torch is None:
        fail("Cannot check CUDA because PyTorch is unavailable")
        return

    print(f"PyTorch CUDA version: {torch.version.cuda}")

    if torch.version.cuda is None:
        fail("PyTorch was installed without CUDA support")
    else:
        ok(f"PyTorch CUDA support detected: {torch.version.cuda}")

    cuda_available = torch.cuda.is_available()

    print(f"CUDA available:      {cuda_available}")

    if not cuda_available:
        fail("CUDA is NOT available")
        return

    ok("CUDA is available")

    gpu_count = torch.cuda.device_count()

    print(f"GPU count:           {gpu_count}")

    for i in range(gpu_count):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"GPU {i}:              {gpu_name}")


# ============================================================
# 5. CUDA 實際運算測試
# ============================================================

def check_cuda_tensor(torch):
    print("\n" + "=" * 60)
    print("5. CUDA Tensor Test")
    print("=" * 60)

    if torch is None:
        fail("Cannot run CUDA Tensor test")
        return

    if not torch.cuda.is_available():
        fail("CUDA is not available, skipping Tensor test")
        return

    try:
        # 非常小的測試，不涉及模型、不涉及訓練
        x = torch.randn(10, 10, device="cuda")
        y = torch.randn(10, 10, device="cuda")

        z = x @ y

        # 強制等待 GPU 完成
        torch.cuda.synchronize()

        if z.shape == (10, 10):
            ok("CUDA Tensor computation successful")
        else:
            fail("CUDA Tensor computation produced unexpected result")

    except Exception as e:
        fail(f"CUDA Tensor computation failed: {e}")


# ============================================================
# 6. Checkpoint
# ============================================================

def check_checkpoints():
    print("\n" + "=" * 60)
    print("6. Pretrained Checkpoints")
    print("=" * 60)

    all_exist = True

    for name, path in CHECKPOINTS.items():

        if os.path.isfile(path):

            size_bytes = os.path.getsize(path)
            size_mb = size_bytes / (1024 * 1024)

            print(
                f"[OK]   {path:<35} "
                f"{size_mb:.2f} MB"
            )

        else:

            print(
                f"[FAIL] {path:<35} "
                f"NOT FOUND"
            )

            all_exist = False

    if all_exist:
        ok("All pretrained checkpoints are present")
    else:
        fail("Some pretrained checkpoints are missing")


# ============================================================
# 7. Summary
# ============================================================

def summary():
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Checks passed : {passed}")
    print(f"Checks failed : {failed}")

    print()

    if failed == 0:
        print(green("========================================"))
        print(green("       ENVIRONMENT OK"))
        print(green("========================================"))
        print()
        print("Everything looks ready.")
        return 0

    else:
        print(red("========================================"))
        print(red("       ENVIRONMENT ERROR"))
        print(red("========================================"))
        print()
        print("Please fix the failed items above.")
        return 1


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print("        PROJECT ENVIRONMENT CHECK")
    print("=" * 60)
    print()
    print("This program ONLY checks the environment.")
    print("It does NOT train or run the model.")
    print("It does NOT download checkpoints.")
    print()

    check_python()

    check_requirements()

    torch = check_pytorch()

    check_cuda(torch)

    check_cuda_tensor(torch)

    check_checkpoints()

    return summary()


if __name__ == "__main__":
    sys.exit(main())