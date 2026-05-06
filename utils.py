import os
import sys
import pyperclip
from tkinter import messagebox
from tkinter import Menu


def resource_path(relative_path):
    """
    Получает абсолютный путь к ресурсам (иконкам, картинкам),
    работая и в коде, и в скомпилированном .exe
    """
    # Использует getattr, чтобы редактор кода не видел прямой ссылки на sys._MEIPASS
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def handle_hotkeys(event, root):
    """
    Универсальный обработчик горячих клавиш для работы с текстом.
    Позволяет использовать стандартные комбинации (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A)
    даже при включенной русской раскладке клавиатуры. Использует скан-коды
    клавиш для обхода ограничений системных событий в разных языковых режимах.
    Принимает root (окно), чтобы знать, где искать фокус.
    """
    widget = root.focus_get()
    if not widget or not hasattr(widget, "event_generate"):
        return None

    # Проверяет Ctrl
    if event.state & 0x4:
        # Если keysym — обычная буква (a, v, c, x), значит раскладка английская.
        if event.keysym.lower() in ['v', 'c', 'x', 'a']:
            return None

        # Если здесь, значит раскладка НЕ английская (русская или иная)
        # Использует скан-коды (keycode) для принудительного вызова команд
        if event.keycode == 67:  # C
            widget.event_generate("<<Copy>>")
            return "break"
        elif event.keycode == 86:  # V
            widget.event_generate("<<Paste>>")
            return "break"
        elif event.keycode == 88:  # X
            widget.event_generate("<<Cut>>")
            return "break"
        elif event.keycode == 65:  # A
            widget.event_generate("<<SelectAll>>")
            return "break"
    return None

class RightClickMenu:
    """
    Класс для реализации контекстного меню правой кнопки мыши.
    Обеспечивает стандартные операции редактирования (копирование, вставка,
    вырезание и выделение всего текста) для виджетов ввода.
    Корректно работает с буфером обмена системы независимо от текущей
    языковой раскладки клавиатуры.
    """
    def __init__(self, widget):
        self.widget = widget
        self.menu = Menu(widget, tearoff=0)
        self.menu.add_command(label="Копировать", command=self.copy)
        self.menu.add_command(label="Вставить", command=self.paste)
        self.menu.add_command(label="Вырезать", command=self.cut)
        self.menu.add_separator()
        self.menu.add_command(label="Выделить всё", command=self.select_all)

        # Привязывает ко всем возможным кнопкам (Windows, Linux, Mac)
        self.widget.bind("<Button-3>", self.show_menu)
        self.widget.bind("<Button-2>", self.show_menu)

    def show_menu(self, event):
        """
        Отображает контекстное меню в месте нажатия правой кнопки мыши.
        Использует абсолютные координаты курсора (x_root, y_root) для точного
        позиционирования всплывающего окна меню относительно экрана.
        """
        self.menu.tk_popup(event.x_root, event.y_root)

    def copy(self):
        """Копирует выделенный текст в буфер обмена."""
        try:
            # Получает выделенный текст
            text = self.widget.selection_get()
            pyperclip.copy(text)
        except Exception:  # noqa
            pass  # Если ничего не выделено

    def paste(self):
        """Вставляет текст из буфера обмена в текущую позицию курсора."""
        text = pyperclip.paste()
        # Если это CTkEntry
        if hasattr(self.widget, "insert"):
            # Если есть выделение, удаляет его перед вставкой
            try:
                self.widget.delete("sel.first", "sel.last")
            except Exception:  # noqa
                pass

            # Вставляет текст из буфера в текущую позицию курсора
            index = self.widget.index("insert")
            self.widget.insert(index, text)

    def cut(self):
        """Копирует выделенный текст в буфер и удаляет его из поля."""
        self.copy()
        try:
            self.widget.delete("sel.first", "sel.last")
        except Exception:  # noqa
            pass

    def select_all(self):
        """Выделяет весь текст в активном виджете."""
        # Для CTkEntry
        if hasattr(self.widget, "select_range"):
            self.widget.select_range(0, 'end')
            self.widget.icursor('end')
        # Для CTkTextbox
        else:
            self.widget.tag_add("sel", "1.0", "end")


def copy_with_animation(root, value, button):
    """Вспомогательный метод для копирования"""
    if value and value.strip() not in ["", "—"]:  # Проверяет, что есть что копировать
        pyperclip.copy(value)
        # Выводит окно подтверждения
        # messagebox.showinfo("Копирование", "Данные успешно скопированы в буфер обмена!", parent=self)

        # Сохраняет старые параметры кнопки
        old_text = button.cget("text")
        old_fg = button.cget("fg_color")
        old_text_color = button.cget("text_color")
        old_font = button.cget("font")

        # Меняет на "зеленую ОК"
        button.configure(
            text="ОК",
            text_color="white",
            font=("Roboto", 12, "bold"),
            fg_color="#1E8449",
            state="disabled"
        )

        # Через 2000 мс (2 сек) возвращает кнопку в нормальное состояние
        root.after(2000, lambda: button.configure(
            text=old_text,
            text_color=old_text_color,
            fg_color=old_fg,
            font=old_font,
            state="normal"
        ))  # noqa

        # Очищает буфер обмена через 60 секунд для безопасности.
        # Передает само значение, чтобы проверить его перед удалением
        root.after(60000, lambda: clear_clipboard(value))

    else:
        # Если данных нет, уведомляет об ошибке
        messagebox.showwarning(
            "Внимание",
            "Нет данных для копирования!",
            parent=root
        )

def clear_clipboard(last_copied_value):
    """Удаляет пароль из буфера, если он там всё еще лежит."""
    try:
        # Проверяет: если в буфере всё еще то самое значение, которое копировали
        if pyperclip.paste() == last_copied_value:
            pyperclip.copy("")  # Стирает
    except Exception:  # noqa
        pass  # На случай, если доступ к буферу заблокирован

def save_appearance_mode(mode):
    """Сохраняет выбранную тему (Dark или Light)."""
    import json
    try:
        with open("settings.json", "w") as f:
            json.dump({"appearance_mode": mode}, f)
    except Exception:  # noqa
        pass

def load_appearance_mode():
    """Загружает тему. Если файла нет — возвращает 'Dark'."""
    import json
    import os
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                return data.get("appearance_mode", "Dark")
        except Exception:  # noqa
            return "Dark"
    return "Dark"


# def check_password_strength(password):
#     """Оценивает сложность пароля и возвращает (прогресс, цвет)."""
#     if not password:
#         return 0, "#3E3E3E"  # Серый (пусто)
#
#     score = 0
#     length = len(password)
#
#     # 1. Длина
#     if length >= 8:
#         score += 0.3
#     elif length >= 4:
#         score += 0.1
#
#     # 2. Наличие цифр
#     if any(char.isdigit() for char in password): score += 0.2
#
#     # 3. Наличие букв разных регистров
#     if any(char.islower() for char in password) and any(char.isupper() for char in password):
#         score += 0.3
#
#     # 4. Спецсимволы
#     if any(not char.isalnum() for char in password): score += 0.2
#
#     # Определяем цвет
#     if score <= 0.3: return score, "#E74C3C"  # Красный (слабый)
#     if score <= 0.6: return score, "#F1C40F"  # Желтый (средний)
#     return score, "#27AE60"  # Зеленый (надежный)
