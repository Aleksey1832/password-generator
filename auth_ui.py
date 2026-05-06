import customtkinter as ctk
import os
from tkinter import messagebox
from utils import resource_path, RightClickMenu, copy_with_animation, handle_hotkeys
from cryptography.fernet import Fernet
import licensing
from security import start_bruteforce_lock


class AuthWindow(ctk.CTk):
    """
    Окно авторизации и начальной настройки приложения.

    Этот класс реализует интерфейс для создания мастер-пароля при первом запуске
    и последующей проверки доступа. Использует библиотеку CustomTkinter для
    современного UI и шифрование для безопасного хранения учетных данных.

    Атрибуты:
        authorized (bool): Флаг, указывающий на успешное прохождение проверки.
        is_first_run (bool): Определяет, создается ли пароль или вводится существующий.
    """
    def __init__(self):
        super().__init__()
        # Инициализирует атрибуты заранее, чтобы IDE не ругалась.
        # Объявляет атрибуты здесь, чтобы IDE знала о них заранее
        self.title_label = None
        self.desc_label = None
        self.pass_entry = None
        self.btn_action = None
        self.copy_id_btn = None
        self.license_entry = None
        self.authorized = False
        self.copy_id_btn = None
        self.license_entry = None
        self.pass_entry = None
        self.lock_time_remaining = 0  # Чтобы кнопка знала, что она НЕ заблокирована
        self.failed_attempts = 0  # Чтобы счетчик ошибок начался с нуля

        # 1. Базовые настройки окна (общие для обоих экранов)
        self.title("Password Generator")

        self.resizable(False, False)
        self.authorized = False

        # Привязка к раскладке
        self.bind_all("<Key>", lambda e: handle_hotkeys(e, self))

        # Данные для мастер-пароля
        self.pass_file = "master.key"
        self.secret_key_file = "internal.key"  # Ключ для шифрования мастер-пароля

        # Установка иконки
        try:
            # Задержка в 200мс дает окну время родиться, после чего ставим иконку
            self.after(200, lambda: self.wm_iconbitmap(resource_path("logo.ico")))  # noqa
        except Exception:  # noqa
            pass  # Если иконка не найдена, просто игнорирует

        # 2. Проверка лицензии и выбор экрана
        self.is_licensed = licensing.is_activated()
        # Если не активирована — показывает экран лицензии
        if not self.is_licensed:
            self.setup_license_screen()
            return
        else:
            # Проверка: если это первый запуск, определяет флаг для экрана входа
            self.is_first_run = not (os.path.exists(self.pass_file) and os.path.exists(self.secret_key_file))
            self.setup_auth_screen()

        # Определяет режим: Регистрация или Вход
        self.is_first_run = not os.path.exists(self.pass_file)

        # Переменные для защиты от подбора пароля (Brute-force protection)
        self.failed_attempts = 0  # Счетчик ошибок
        self.lock_time_remaining = 0  # Флаг и таймер временной блокировки интерфейса

    def setup_license_screen(self):
        """Интерфейс для ввода лицензионного ключа."""
        # Очищает окно
        for widget in self.winfo_children():
            widget.destroy()

        self.title("Password Pro - Активация")
        # Центрирование для окна активации (380x350)
        self.geometry("380x350")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        # 190 = 380/2, 175 = 350/2
        self.geometry(f"+{int(sw / 2 - 190)}+{int(sh / 2 - 175)}")


        # Текст предупреждения
        ctk.CTkLabel(self, text="ПРОГРАММА НЕ АКТИВИРОВАНА",
                     font=("Roboto", 16, "bold"), text_color="#E74C3C").pack(pady=(20, 10))

        # Блок HWID
        hwid = licensing.get_hwid()
        ctk.CTkLabel(self, text="Ваш уникальный ID (отправьте админу):", font=("Roboto", 12)).pack()

        hwid_entry = ctk.CTkEntry(self, width=300, justify="center",
                                  fg_color=("#EAEAEA", "#2B2B2B"), text_color=("#1A1A1A", "#FFFFFF"))
        hwid_entry.insert(0, hwid)
        hwid_entry.configure(state="readonly")
        hwid_entry.pack(pady=5)

        # 1. СОЗДАЕТ объект кнопки копирования ID (использует универсальную функцию из utils)
        self.copy_id_btn = ctk.CTkButton(
            self,
            text="КОПИРОВАТЬ ID",
            width=140,
            height=28,
        )
        # 3. ПАКУЕТ отдельной строкой
        self.copy_id_btn.pack(pady=5)
        # 2. Настраивает команду (теперь self.copy_id_btn — это кнопка, а не None)
        self.copy_id_btn.configure(
            command=lambda b=self.copy_id_btn: copy_with_animation(self, hwid, b)
        )

        # Поле ключа
        ctk.CTkLabel(
            self,
            text="Введите лицензионный ключ:",
            font=("Roboto", 12)
        ).pack(pady=(15, 0))
        self.license_entry = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            justify="center"
        )
        self.license_entry.pack(pady=5)

        # Контекстное меню для вставки ключа
        RightClickMenu(self.license_entry)

        # Кнопка активации
        ctk.CTkButton(
            self, text="АКТИВИРОВАТЬ",
            fg_color="#1E8449",
            hover_color="#2ECC71",
            command=self.activate_program
        ).pack(pady=10)

        # Текст предупреждения
        ctk.CTkLabel(self, text="ПРОГРАММА НЕ АКТИВИРОВАНА",
                     font=("Roboto", 16, "bold"), text_color="#E74C3C").pack(pady=(15, 10))

    def setup_auth_screen(self):
        """
        Интерфейс для входа в систему (авторизация/регистрация).
        Очищает окно и рисует поля для мастер-пароля.
        """
        # 1. Полная очистка окна от предыдущего экрана (лицензии)
        for widget in self.winfo_children():
            widget.destroy()

        # 2. Определение режима: первый запуск (регистрация) или обычный вход.
        # Проверяет наличие файлов ключей мастер-пароля
        self.is_first_run = not (os.path.exists(self.pass_file) and os.path.exists(self.secret_key_file))

        # 3. Настройка заголовка и геометрии
        self.title("Password Pro – Авторизация")

        # Центрирование для окна авторизации (350x280)
        self.geometry("350x280")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{int(sw / 2 - 175)}+{int(sh / 2 - 140)}")

        # Заголовок
        title_text = "УСТАНОВКА" if self.is_first_run else "АВТОРИЗАЦИЯ"
        self.title_label = ctk.CTkLabel(self, text=title_text, font=("Roboto", 18, "bold"))
        self.title_label.pack(pady=(15, 5))

        # Отдельная яркая метка для предупреждения и текст придумать пароль
        if self.is_first_run:
            ctk.CTkLabel(
                self,
                text="⚠ ВНИМАНИЕ: СОХРАНИТЕ ПАРОЛЬ!\n"
                     "ПАРОЛЬ НЕВОЗМОЖНО ВОССТАНОВИТЬ!",
                text_color="#E74C3C",
                font=("Consolas", 13, "bold"),
                wraplength=300  # Чтобы текст красиво переносился
            ).pack(pady=(10, 5))

            desc_text = "Придумайте мастер-пароль (4-8 символов):"
        else:
            desc_text = "Введите мастер-пароль:"
        self.desc_label = ctk.CTkLabel(self, text=desc_text, font=("Roboto", 12))
        self.desc_label.pack(pady=5)

        # 4. Поле ввода пароля
        self.pass_entry = ctk.CTkEntry(self, show="*", width=250, height=40, justify="center")
        self.pass_entry.pack(pady=10)
        self.pass_entry.focus()

        # Подключает контекстное меню (из utils)
        RightClickMenu(self.pass_entry)

        # 5. Кнопка действия (Установить/Войти)
        btn_text = "УСТАНОВИТЬ" if self.is_first_run else "ВОЙТИ"
        self.btn_action = ctk.CTkButton(
            self,
            text=btn_text,
            width=200,
            height=40,
            command=lambda: self.handle_action()
        )
        self.btn_action.pack(pady=15)

        # 6. Привязка клавиши Enter
        self.bind("<Return>", lambda e: self.handle_action())

    def get_cipher(self):
        """Создает или загружает ключ для шифрования самого мастер-пароля."""
        if not os.path.exists(self.secret_key_file):
            key = Fernet.generate_key()
            with open(self.secret_key_file, "wb") as f:
                f.write(key)
        else:
            key = open(self.secret_key_file, "rb").read()
        return Fernet(key)

    def handle_action(self, event=None):
        """
        Управляет логикой авторизации и регистрации.

        В режиме первого запуска (is_first_run): шифрует и сохраняет новый
        мастер-пароль, после чего переключает интерфейс в режим входа.
        В обычном режиме: проверяет введенный пароль на соответствие
        сохраненному. При успехе устанавливает флаг authorized и закрывает окно.

        Args:
            event: Объект события Tkinter (передается при нажатии Enter),
                   по умолчанию None для вызова через кнопку.
        """
        _ = event
        # Если кнопка заблокирована - ничего не делает
        if self.lock_time_remaining > 0:
            return

        password = self.pass_entry.get().strip()

        cipher = self.get_cipher()

        if self.is_first_run:
            # --- ЛОГИКА РЕГИСТРАЦИИ ---
            if 4 <= len(password) <= 8:
                # 1. Шифрует и сохраняет
                encrypted_pass = cipher.encrypt(password.encode())
                with open(self.pass_file, "wb") as f:
                    f.write(encrypted_pass)

                # 2. Показывает окно об успехе
                messagebox.showinfo("Успех", "Мастер-пароль успешно создан!", parent=self)

                # 3. Переключает окно в режим ВХОДА
                self.is_first_run = False
                self.setup_auth_screen()

                self.title("Password Pro – Вход")
                # self.desc_label.configure(text="Введите созданный мастер-пароль:", text_color="white")
                self.title_label.configure(text="АВТОРИЗАЦИЯ")  # <-- Меняет заголовок здесь
                self.desc_label.configure(
                    text="Теперь введите ваш пароль для входа:", text_color=("#1A1A1A", "#FFFFFF"))

                self.pass_entry.delete(0, 'end')
                self.btn_action.configure(text="ВОЙТИ", command=lambda: self.handle_action())
            else:
                self.pass_entry.configure(border_color="red")
                self.desc_label.configure(text="ОШИБКА: Длина 4-8 символов!", text_color="red")

        else:
            # --- ЛОГИКА ВХОДА ---
            try:
                # Чтение и расшифровка эталонного пароля из файла
                with open(self.pass_file, "rb") as f:
                    stored_pass = cipher.decrypt(f.read()).decode()

                # Сценарий: Пароль введен верно
                if password == stored_pass:
                    self.failed_attempts = 0  # Сбрасывает счетчик при успехе
                    self.authorized = True    # Установка флага успешного входа
                    self.withdraw()           # Скрытие окна авторизации
                    self.quit()               # Остановка цикла mainloop для перехода в программу

                # Сценарий: Ошибка ввода пароля
                else:
                    # 2. Увеличивает счетчик ошибок
                    self.failed_attempts += 1

                    # Проверка лимита ошибок (Брутфорс-защита)
                    if self.failed_attempts >= 3:
                        # Сначала меняем текст уведомления
                        self.desc_label.configure(
                            text="ДОСТУП ВРЕМЕННО ЗАБЛОКИРОВАН!",
                            text_color="red"
                        )
                        # Если 3 ошибки — запускает блокировку на 30 секунд
                        self.lock_time_remaining = 30 # Ставит флаг, чтобы нажатия игнорировались
                        # Вызов внешней функции из security.py для блокировки интерфейса и таймера
                        start_bruteforce_lock(
                            self,
                            30,
                            self.btn_action,
                            self.pass_entry,
                            self.desc_label
                        )
                    else:
                        # Обычная индикация ошибки, если попытки еще остались
                        self.pass_entry.configure(border_color="red")
                        self.pass_entry.delete(0, 'end')
                        attempts_left = 3 - self.failed_attempts
                        self.desc_label.configure(
                            text=f"НЕВЕРНЫЙ ПАРОЛЬ! (Осталось: {attempts_left})",
                            text_color="red"
                        )

            # Обработка системных ошибок (отсутствие файла, проблемы с ключом расшифровки)
            except Exception:  # noqa
                self.desc_label.configure(text="Ошибка доступа к ключу!", text_color="red")

    def activate_program(self):
        """Проверяет ключ и активирует программу."""
        # Получает ключ из поля ввода
        user_key = self.license_entry.get().strip()

        if not user_key:
            messagebox.showwarning("Внимание", "Поле ключа не может быть пустым!", parent=self)
            return

        # Проверяет ключ через модуль licensing
        try:
            is_valid = licensing.verify_key(user_key)

            if is_valid:
                # Сохраняет и переходит
                licensing.save_license(user_key)
                messagebox.showinfo("Успех", "Программа успешно активирована!", parent=self)
                self.setup_auth_screen()  # Переходим к окну входа
            else:
                messagebox.showerror("Ошибка", "Неверный лицензионный код!", parent=self)
                self.license_entry.configure(border_color="red")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошел технический сбой: {e}", parent=self)
