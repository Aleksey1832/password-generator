import os
import sys
from password_manager import Vault
import customtkinter as ctk
import random
import string
import pyperclip  # Библиотека для копирования в буфер обмена
from PIL import Image
from tkinter import messagebox


def resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсам (иконкам, картинкам),
    работая и в коде, и в скомпилированном .exe
    """
    # Используем getattr, чтобы редактор кода не видел прямой ссылки на sys._MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PasswordGenerator(ctk.CTk):
    """
    Класс для создания графического интерфейса генератора безопасных паролей.
    Наследуется от ctk.CTk для использования современных виджетов CustomTkinter.
    """
    def __init__(self):
        """
        Инициализирует главное окно приложения, настраивает геометрию,
        создает все виджеты (кнопки, чекбоксы, слайдеры) и задает начальные значения.
        """
        super().__init__()

        self.vault = Vault()
        self.title("Password Generator Pro")

        # ---Указываем размеры окна---
        window_width = 450
        window_height = 620

        # Получаем размеры экрана
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Вычисляем координаты центра
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # Устанавливаем геометрию с координатами
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.resizable(False, False)

        # ---Иконка---
        self.wm_iconbitmap(resource_path("logo.ico"))

        # --- Заголовок ---
        self.label = ctk.CTkLabel(self, text="ГЕНЕРАТОР ПАРОЛЕЙ", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(5, 5))

        # --- Поле вывода пароля ---
        self.entry_label = ctk.CTkLabel(self, text="Ваш новый пароль:", font=("Roboto", 12))
        self.entry_label.pack(pady=(5, 0))

        # Загружаем иконку
        self.copy_icon = ctk.CTkImage(
            light_image=Image.open(resource_path("copy_icon.png")),
            dark_image=Image.open(resource_path("copy_icon.png")),
            size=(20, 20)  # Размер иконки внутри кнопки
        )

        # --- Контейнер для поля и кнопки (ровняем по центру) ---
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.pack(pady=10, fill="x", padx=40)  # Растягиваем по горизонтали

        # Поле вывода
        self.result_entry = ctk.CTkEntry(
            self.entry_frame,
            font=("Consolas", 16),
            justify="center",
            width=300,  # Фиксированная ширина
            height=50,
            placeholder_text="Нажмите 'Сгенерировать'"
        )
        self.result_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Кнопка с иконкой
        self.copy_button = ctk.CTkButton(
            self.entry_frame,
            text="",
            image=self.copy_icon,
            width=35,
            height=35,
            command=self.copy_to_clipboard,
            fg_color="transparent",
            border_width=2,
            border_color="#3498DB",
            hover_color="#2C3E50"
        )
        self.copy_button.pack(side="right")

        # --- Ползунок длины ---
        self.len_label = ctk.CTkLabel(self, text="Длина пароля: 12", font=("Roboto", 14))
        self.len_label.pack(pady=(2, 0))

        self.slider = ctk.CTkSlider(self, from_=4, to=30, number_of_steps=26, command=self.update_slider_label)
        self.slider.set(12)  # Значение по умолчанию
        self.slider.pack(pady=5)

        # --- Настройки (Чекбоксы) ---
        self.check_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.check_frame.pack(pady=4)

        self.use_digits = ctk.CTkCheckBox(self.check_frame, text="Цифры (0-9)")
        self.use_digits.select()  # Включено по умолчанию
        self.use_digits.pack(anchor="w", pady=4)

        self.use_low = ctk.CTkCheckBox(self.check_frame, text="Строчные буквы (a-z)")
        self.use_low.select()
        self.use_low.pack(anchor="w", pady=4)

        self.use_up = ctk.CTkCheckBox(self.check_frame, text="Прописные буквы (A-Z)")
        self.use_up.select()
        self.pack_pady = 5
        self.use_up.pack(anchor="w", pady=4)

        self.use_special = ctk.CTkCheckBox(self.check_frame, text="Спецсимволы (!#$%)")
        self.use_special.pack(anchor="w", pady=4)

        self.exclude_bad = ctk.CTkCheckBox(self.check_frame, text="Исключить сложные (il1Lo0O)")
        self.exclude_bad.pack(anchor="w", pady=4)

        # ---Кнопка СГЕНЕРИРОВАТЬ---
        self.gen_button = ctk.CTkButton(
            self,
            text="СГЕНЕРИРОВАТЬ",
            command=self.generate,
            font=("Roboto", 20, "bold"),  # Размер шрифта
            height=43,  # Высота кнопки
            width=300,  # Ширина кнопки
            fg_color="#27AE60",  # Насыщенный зеленый (Emerald)
            hover_color="#2ECC71",  # Светло-зеленый при наведении
        )
        self.gen_button.pack(pady=10)

        # --- Поле ввода сервиса (для связи пароля с почтой/сайтом) ---
        self.service_label = ctk.CTkLabel(self, text="Название сервиса (сайт/почта):", font=("Roboto", 12))
        self.service_label.pack(pady=(5, 0))

        self.service_entry = ctk.CTkEntry(
            self,
            placeholder_text="Например: google.com",
            width=350
        )
        self.service_entry.pack(pady=(0, 10))

        # --- Кнопка СОХРАНИТЬ ---
        self.save_button = ctk.CTkButton(
            self,
            text="ЗАШИФРОВАТЬ И СОХРАНИТЬ",
            command=self.save_encrypted_password,  # Метод, который мы создали
            font=("Roboto", 15, "bold"),
            width=220,
            height=35,
            fg_color="#8E44AD",  # Фиолетовый цвет, чтобы отличалась от генерации
            hover_color="#9B59B6"
        )

        self.save_button.pack(pady=10)

    def update_slider_label(self, value):
        """
        Обновляет текстовую метку над ползунком при его перемещении.

        Args:
            value (float): Текущее значение слайдера (передается автоматически
                          библиотекой customtkinter при сдвиге).
        """
        self.len_label.configure(text=f"Длина пароля: {int(value)}")

    def generate(self):
        """
        Основной метод генерации пароля.
        Формирует набор доступных символов на основе выбранных чекбоксов,
        проверяет исключения, считывает длину со слайдера и выводит
        результат в текстовое поле.
        """
        chars = ""
        # 1. Сборка символов
        if self.use_digits.get(): chars += string.digits
        if self.use_low.get(): chars += string.ascii_lowercase
        if self.use_up.get(): chars += string.ascii_uppercase
        if self.use_special.get(): chars += "!#$%&*+-=?@^_"

        if self.exclude_bad.get():
            for c in "il1Lo0O":
                chars = chars.replace(c, "")

        # 2. ПРОВЕРКА: Если ничего не выбрано (блок)
        if not chars:
            self.result_entry.configure(state="normal")  # Разблокировали
            self.result_entry.delete(0, "end")
            self.result_entry.insert(0, "Выберите настройки!")
            self.result_entry.configure(state="readonly")  # Заблокировали обратно
            return  # ВЫХОДИМ из функции, чтобы код ниже не упал с ошибкой

        # 3. САМА ГЕНЕРАЦИЯ (если chars не пустой)
        length = int(self.slider.get())
        password = "".join(random.choices(chars, k=length))

        # 4. ВЫВОД РЕЗУЛЬТАТА
        self.result_entry.configure(state="normal")  # Разблокировали
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, password)
        self.result_entry.configure(state="readonly")  # Заблокировали обратно

    def copy_to_clipboard(self):
        """
        Копирует текущий текст из поля вывода в буфер обмена системы.
        При успешном копировании временно изменяет цвет и текст кнопки
        для визуального подтверждения действия пользователю.
        """
        password = self.result_entry.get()

        # Список системных сообщений, которые НЕ надо копировать
        bad_values = ["Выберите настройки!", "Нажмите 'Сгенерировать'"]

        if password and password not in bad_values:
            pyperclip.copy(password)

            # Эффект успеха: кнопка становится зеленой
            self.copy_button.configure(
                fg_color="#27AE60",  # Зеленый фон
                border_color="#27AE60",  # Зеленая рамка
                hover_color="#27AE60"  # Чтобы при наведении не менялась
            )

            # Через 1.2 секунды возвращаем всё как было
            self.after(1200, self.reset_copy_button)  # noqa

            # Всплывающее уведомление
            messagebox.showinfo(
                "Успех",
                "Пароль успешно скопирован в буфер обмена!",
                parent=self  # Привязка окна к координатам программы
            )

    def reset_copy_button(self):
        """Возвращает иконку и исходный стиль кнопке копирования"""
        self.copy_button.configure(
            fg_color="transparent",
            border_color="#3498DB",
            hover_color="#2C3E50"
        )

    def show_toast(self, message):
        """Создает всплывающее уведомление внизу окна"""
        toast = ctk.CTkLabel(
            self,
            text=message,
            fg_color="#2ECC71",  # Яркий зеленый
            text_color="black",  # Черный текст для контраста
            corner_radius=10,
            font=("Roboto", 14, "bold"),
            width=250,
            height=35
        )
        # Размещаем внизу окна по центру
        toast.place(relx=0.5, rely=0.24, anchor="center")

        # Удаляем через 2 секунды
        self.after(2000, toast.destroy)

    def save_encrypted_password(self):
        service = self.service_entry.get()
        password = self.result_entry.get()

        # Проверка на пустые значения
        bad_values = ["Выберите настройки!", "Нажмите 'Сгенерировать'", ""]
        if service == "" or password in bad_values:
            return

        # Используем наш новый менеджер
        self.vault.save_entry(service, password)

        # Визуальный отклик (зеленая кнопка)
        self.save_button.configure(text="СОХРАНЕНО!", fg_color="#27AE60")
        self.after(1500, lambda: self.save_button.configure(
            text="ЗАШИФРОВАТЬ И СОХРАНИТЬ",
            fg_color="#8E44AD"
        ))  # noqa

if __name__ == "__main__":
    app = PasswordGenerator()
    app.mainloop()
