import customtkinter as ctk
import random
import string
import pyperclip  # Библиотека для копирования в буфер обмена

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PasswordGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Артем Password Pro")
        self.geometry("450x520")
        self.resizable(False, False)

        # --- Заголовок ---
        self.label = ctk.CTkLabel(self, text="ГЕНЕРАТОР ПАРОЛЕЙ", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(15, 5))

        # --- Поле вывода пароля ---
        self.entry_label = ctk.CTkLabel(self, text="Ваш новый пароль:", font=("Roboto", 12))
        self.entry_label.pack(pady=(10, 0))

        # --- Поле вывода пароля с подсказкой ---
        self.result_entry = ctk.CTkEntry(
            self,
            font=("Consolas", 20),
            justify="center",
            width=350,
            height=50,
            placeholder_text="Нажмите 'Сгенерировать'"  # <-- Вот эта магия!
        )
        self.result_entry.pack(pady=10)

        # --- Ползунок длины ---
        self.len_label = ctk.CTkLabel(self, text="Длина пароля: 12", font=("Roboto", 14))
        self.len_label.pack(pady=(10, 0))

        self.slider = ctk.CTkSlider(self, from_=4, to=30, number_of_steps=26, command=self.update_slider_label)
        self.slider.set(12)  # Значение по умолчанию
        self.slider.pack(pady=5)

        # --- Настройки (Чекбоксы) ---
        self.check_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.check_frame.pack(pady=5)

        self.use_digits = ctk.CTkCheckBox(self.check_frame, text="Цифры (0-9)")
        self.use_digits.select()  # Включено по умолчанию
        self.use_digits.pack(anchor="w", pady=5)

        self.use_low = ctk.CTkCheckBox(self.check_frame, text="Строчные буквы (a-z)")
        self.use_low.select()
        self.use_low.pack(anchor="w", pady=5)

        self.use_up = ctk.CTkCheckBox(self.check_frame, text="Прописные буквы (A-Z)")
        self.use_up.select()
        self.pack_pady = 5
        self.use_up.pack(anchor="w", pady=5)

        self.use_special = ctk.CTkCheckBox(self.check_frame, text="Спецсимволы (!#$%)")
        self.use_special.pack(anchor="w", pady=5)

        self.exclude_bad = ctk.CTkCheckBox(self.check_frame, text="Исключить сложные (il1Lo0O)")
        self.exclude_bad.pack(anchor="w", pady=5)

        # Кнопка СГЕНЕРИРОВАТЬ (яркая и заметная)
        self.gen_button = ctk.CTkButton(
            self,
            text="СГЕНЕРИРОВАТЬ",
            command=self.generate,
            font=("Roboto", 18, "bold"),  # Сделали шрифт чуть крупнее
            height=50,  # Сделали кнопку выше
            width=300,
            fg_color="#27AE60",  # Насыщенный зеленый (Emerald)
            hover_color="#2ECC71",  # Светло-зеленый при наведении
        )
        self.gen_button.pack(pady=10)

        # Кнопка КОПИРОВАТЬ (Широкая, жирная и солидная)
        self.copy_button = ctk.CTkButton(
            self,
            text="КОПИРОВАТЬ В БУФЕР",
            command=self.copy_to_clipboard,
            font=("Roboto", 16, "bold"),
            width=250,
            height=40,  # Установили четкую высоту 50!
            fg_color="transparent",
            border_width=2,
            border_color="#3498DB",
            hover_color="#2C3E50"
        )
        # Добавили большой отступ снизу (30), чтобы она не жалась к краю
        self.copy_button.pack(pady=(0, 15))

    def update_slider_label(self, value):
        self.len_label.configure(text=f"Длина пароля: {int(value)}")

    def generate(self):
        chars = ""
        if self.use_digits.get(): chars += string.digits
        if self.use_low.get(): chars += string.ascii_lowercase
        if self.use_up.get(): chars += string.ascii_uppercase
        if self.use_special.get(): chars += "!#$%&*+-=?@^_"

        if self.exclude_bad.get():
            for c in "il1Lo0O":
                chars = chars.replace(c, "")

        if not chars:
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, "Выберите настройки!")
            return

        length = int(self.slider.get())
        password = "".join(random.choices(chars, k=length))

        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, password)
        self.copy_button.configure(text="КОПИРОВАТЬ", text_color="white")

    def copy_to_clipboard(self):
        password = self.result_entry.get()
        if password and password != "Нажмите 'Сгенерировать'":
            pyperclip.copy(password)

            # Эффект успеха: кнопка становится зеленой
            self.copy_button.configure(
                text="УСПЕШНО СКОПИРОВАНО!",
                fg_color="#27AE60",
                border_color="#27AE60"
            )

            # Через 1.5 секунды возвращаем исходный синий стиль
            self.after(1500, lambda: self.copy_button.configure(
                text="КОПИРОВАТЬ В БУФЕР",
                fg_color="transparent",
                border_color="#3498DB"
            ))  # noqa

if __name__ == "__main__":
    app = PasswordGenerator()
    app.mainloop()
