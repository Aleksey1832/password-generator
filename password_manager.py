import os
import json
from cryptography.fernet import Fernet


class Vault:
    """Класс для безопасного хранения паролей."""
    def __init__(self, key_file="key.key", data_file="passwords.dat"):
        self.key_file = key_file
        self.data_file = data_file
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        """Загружает ключ из файла или создает новый, если файла нет."""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        return open(self.key_file, "rb").read()

    def save_entry(self, service, login, password):
        """Шифрует и сохраняет новую запись."""
        data = self.get_all_entries()
        data.append({"service": service, "login": login, "password": password})

        # Превращает список в JSON, затем в байты и шифруем
        encrypted_data = self.fernet.encrypt(json.dumps(data).encode())
        with open(self.data_file, "wb") as f:
            f.write(encrypted_data)

    def get_all_entries(self):
        """Расшифровывает и возвращает все записи."""
        if not os.path.exists(self.data_file):
            return []

        try:
            with open(self.data_file, "rb") as f:
                encrypted_content = f.read()
                if not encrypted_content:
                    return []
                decrypted_content = self.fernet.decrypt(encrypted_content)
                return json.loads(decrypted_content.decode())
        except Exception:  # noqa
            # Если ключ не подходит или файл поврежден
            return []

    def delete_entry_by_service(self, service_name):
        """Удаляет все записи с указанным названием сервиса."""
        data = self.get_all_entries()
        # Создает новый список без указанного сервиса
        new_data = [item for item in data if item['service'].lower() != service_name.lower()]

        if len(data) == len(new_data):
            return False  # Ничего не нашли

        # Шифрует и сохраняет обновленный список
        encrypted_data = self.fernet.encrypt(json.dumps(new_data).encode())
        with open(self.data_file, "wb") as f:
            f.write(encrypted_data)
        return True
