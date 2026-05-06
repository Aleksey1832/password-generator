import zipfile
import os
from tkinter import filedialog, messagebox


def run_export(parent_window):
    """Создает резервную копию базы данных и ключа шифрования."""
    # Файлы, необходимые для восстановления данных
    files_to_backup = ["passwords.dat", "internal.key"]

    # Проверяет, существуют ли они (если база еще пустая, копировать нечего)
    if not all(os.path.exists(f) for f in files_to_backup):
        messagebox.showwarning("Внимание", "База данных пуста или не создана!", parent=parent_window)
        return

    # Открывает диалог сохранения
    save_path = filedialog.asksaveasfilename(
        parent=parent_window,
        title="Сохранить резервную копию",
        defaultextension=".pback",
        filetypes=[("Password Backup", "*.pback")]
    )

    if save_path:
        try:
            with zipfile.ZipFile(save_path, 'w') as zipf:
                for file in files_to_backup:
                    zipf.write(file)
            messagebox.showinfo("Успех", "Резервная копия создана!", parent=parent_window)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать экспорт: {e}", parent=parent_window)


def run_import(parent_window):
    """Импортирует данные из файла резервной копии."""
    import_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Выберите файл резервной копии",
        filetypes=[("Password Backup", "*.pback")]
    )

    if import_path:
        # Предупреждает, что текущие данные на этом ПК будут заменены
        confirm = messagebox.askyesno(
            "Внимание",
            "Импорт заменит текущие пароли и ключи! Продолжить?",
            parent=parent_window
        )
        if confirm:
            try:
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    zipf.extractall()
                messagebox.showinfo("Успех", "Данные импортированы!\nПриложение будет закрыто для обновления.",
                                    parent=parent_window)
                os._exit(0)  # Жесткое закрытие для перезагрузки ключей
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}", parent=parent_window)
