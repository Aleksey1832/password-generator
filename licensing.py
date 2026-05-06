import subprocess
import hashlib
import os
from settings import SECRET_SALT


def get_hwid():
    """Получает уникальный ID железа через PowerShell"""
    try:
        # 1. Пробует серийник материнки
        cmd = "powershell (Get-CimInstance -ClassName Win32_BaseBoard).SerialNumber"
        serial = subprocess.check_output(cmd, shell=True).decode('cp866').strip()

        # Если серийник не подходит, берет UUID системы
        if not serial or any(bad in serial.lower() for bad in ["to be filled", "default", "none"]):
            cmd_uuid = "powershell (Get-CimInstance -ClassName Win32_ComputerSystemProduct).UUID"
            serial = subprocess.check_output(cmd_uuid, shell=True).decode('cp866').strip()

        return serial
    except Exception:  # noqa
        return os.environ.get('COMPUTERNAME', 'UNKNOWN_ID')

def verify_key(user_key):
    """Сверяет введенный ключ с эталоном на основе HWID"""
    try:
        hwid = get_hwid()
        # СЕКРЕТ
        raw_string = f"{hwid}-{SECRET_SALT}"

        # Генерация правильного хэша (первые 16 символов)
        correct_hash = hashlib.sha256(raw_string.encode()).hexdigest()[:16].upper()

        # Очищает ввод пользователя
        clean_user_key = str(user_key).strip().replace("-", "").upper()

        return clean_user_key == correct_hash
    except Exception:  # noqa
        return False

def save_license(key):
    """Сохраняет очищенный от пробелов ключ в файл"""
    try:
        with open("license.lic", "w", encoding="utf-8") as f:
            f.write(key.strip())
        return True
    except Exception:  # noqa
        return False

def is_activated():
    """Проверяет, активирована ли программа на этом ПК"""
    if not os.path.exists("license.lic"):
        return False
    try:
        with open("license.lic", "r") as f:
            saved_key = f.read().strip()
        return verify_key(saved_key)  # Функция проверки
    except Exception:  # noqa
        return False
