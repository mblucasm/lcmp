import os
import subprocess
import venv

FILE = os.path.basename(__file__)
VENV_NAME = ".venv"
MAIN_FILE = "src/lcmp.py"
PACKAGE   = "pygame"

def get_venvs_python_path() -> str:
    if os.name == "nt":
        return os.path.join(VENV_NAME, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_NAME, "bin", "python")

def ensure_venv() -> None:
    if not os.path.exists(VENV_NAME):
        print(f"[{FILE}] Creating virtual enviroment (this will only happen once)")
        venv.create(VENV_NAME, with_pip = True)

def ensure_package(package: str) -> None:
    python = get_venvs_python_path()
    try:
        subprocess.check_output([python, "-c", f"import {package}"], stderr = subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"[{FILE}] Installing required package: {package} (this will only happen once)")
        subprocess.check_call([python, "-m", "pip", "install", package])

def run_app():
    python = get_venvs_python_path()
    subprocess.call([python, MAIN_FILE, "launched"])

if __name__ == "__main__":
    ensure_venv()
    ensure_package(PACKAGE)
    run_app()
