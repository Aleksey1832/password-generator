import customtkinter as ctk
from tkinter import messagebox
from utils import RightClickMenu, resource_path, copy_with_animation, save_appearance_mode, load_appearance_mode
from PIL import Image
import backup_manager


class VaultWindow(ctk.CTkToplevel):
    """
    Класс для создания дочернего графического окна хранилища.
    Отвечает за отображение списка зашифрованных паролей,
    предоставляет интерфейс для просмотра и удаления сохраненных данных.
    Центрируется относительно главного окна приложения.
    """
    def __init__(self, master):
        super().__init__(master)

        # 1. --- Настройка окна ---
        self.title("Хранилище паролей")
        # 1.1 Указывает размеры окна хранилища
        window_width = 500
        window_height = 590

        # 1.2 Обновляет данные о размерах главного окна, чтобы расчет был точным
        self.master.update_idletasks()

        # 1.3 Получает текущие координаты и размеры главного окна (master)
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        # 1.4 Вычисляет координаты центра
        # (Координата X родителя + половина его ширины) - (половина ширины нового окна)
        x = master_x + (master_width // 2) - (window_width // 2)
        y = master_y + (master_height // 2) - (window_height // 2)

        # 1.5 Устанавливает геометрию
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 1.6 Настройки, чтобы окно было активным и сверху
        self.attributes("-topmost", True)
        self.focus_set()

        # 2. --- Устанавливает иконку окна (логотип) ---
        try:
            self.after(200, lambda: self.wm_iconbitmap(resource_path("logo.ico")))  # noqa
        except Exception:  # noqa
            pass  # Если иконка не найдена, игнорирует, чтобы не было ошибки

        # 2.1 Устанавливает иконку глазок
        self.eye_icon = ctk.CTkImage(
            light_image=Image.open(resource_path("eye_icon.png")),
            dark_image=Image.open(resource_path("eye_icon.png")),
            size=(20, 20)
        )
        # 2.2 Увеличенная иконка глазок для наведения
        self.eye_icon_large = ctk.CTkImage(
            light_image=Image.open(resource_path("eye_icon.png")),
            dark_image=Image.open(resource_path("eye_icon.png")),
            size=(23, 23)
        )

        # 3. --- Заголовок ---
        self.label = ctk.CTkLabel(self, text="ВАШИ ПАРОЛИ", font=("Roboto", 20, "bold"))
        self.label.pack(pady=(20, 10))

        # 4. --- Вместо self.textbox создает прокручиваемый контейнер ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=460, height=350)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 5. --- Блок кнопок поиска ---
        # 5.1 Поле поиска
        self.search_entry = ctk.CTkEntry(
            self,
            width=350,
            placeholder_text="Введите название..."
        )
        self.search_entry.pack(pady=5)

        # 5.2 ПРИВЯЗЫВАЕТ МЕНЮ (сразу после создания поля)
        RightClickMenu(self.search_entry)

        # 5.3 Привязка Enter к кнопке поиска
        self.search_entry.bind("<Return>", lambda e: self.load_passwords())

        # 5.4 Создает контейнер-фрейм
        self.btn_search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_search_frame.pack(pady=10, anchor="center")  # fill="x" растянет фрейм по ширине

        # 5.5 Кнопка НАЙТИ (внутри фрейма)
        self.search_button = ctk.CTkButton(
            self.btn_search_frame,
            text="НАЙТИ",
            width=130, height=27,
            fg_color=("#3498DB", "#2E4053"), hover_color=("#2980B9", "#34495E"),
            command=self.load_passwords
        )
        # pack внутри фрейма: прижимает влево и разрешает расширяться
        self.search_button.pack(side="left", padx=(0, 10))

        # 5.6 Кнопка ПОКАЗАТЬ ВСЕ (внутри фрейма)
        self.show_all_button = ctk.CTkButton(
            self.btn_search_frame,
            text="ПОКАЗАТЬ ВСЕ",
            width=130, height=27,
            fg_color=("#5D6D7E", "#3E3E3E"), hover_color=("#34495E", "#505050"),
            command=self.show_all_entries
        )
        # pack внутри фрейма: прижимает влево (встанет за первой кнопкой)
        self.show_all_button.pack(side="left", padx=(10, 0))

        self.load_passwords()

        # 6. --- Создает контейнер-фрейм для импорта экспорта ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(anchor="center", padx=20, pady=10)

        # 6.1 Кнопка Экспорта
        self.btn_export = ctk.CTkButton(
            self.top_frame, text="Экспорт", width=70, height=30,
            fg_color=("#E67E22", "#D35400"), hover_color=("#EB984E", "#A04000"),
            command=lambda: backup_manager.run_export(self)
        )
        self.btn_export.pack(side="left", padx=(0, 10))

        # 6.2 Переключатель темы оформления
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.top_frame,
            values=["Dark", "Light"],
            command=self.change_appearance_mode,
            width=100,
            height=30,
            fg_color=("#D6EAF8", "#34495E"),
            button_color=("#AED6F1", "#2C3E50"),
            button_hover_color=("#85C1E9", "#1B2631"),
            text_color=("#1B4F72", "white")
        )
        self.appearance_mode_optionemenu.pack(side="left", padx=10)
        # Устанавливает в меню актуальную тему из файла
        saved_theme = load_appearance_mode()
        self.appearance_mode_optionemenu.set(saved_theme)

        # 6.3 Кнопка Импорта
        self.btn_import = ctk.CTkButton(
            self.top_frame, text="Импорт", width=70, height=30,
            fg_color=("#16A085", "#16A085"), hover_color=("#1ABC9C", "#1ABC9C"),
            command=lambda: backup_manager.run_import(self)
        )
        self.btn_import.pack(side="right", padx=(10, 0))

    def show_all_entries(self):
        """Очищает поиск и показывает все записи."""
        self.search_entry.delete(0, 'end')
        self.load_passwords()

    def load_passwords(self):
        """
        Загружает список сохраненных паролей и отображает их в интерфейсе.

        Метод очищает текущий контейнер, считывает данные из хранилища
        и для каждой записи создает интерактивную карточку. В карточке
        реализованы кнопки быстрого копирования логина, пароля и названия
        сервиса с визуальной анимацией подтверждения.
        """
        # Очищает фрейм перед загрузкой
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Получает запрос (в нижнем регистре для точности)
        query = self.search_entry.get().lower().strip()
        entries = getattr(self.master, 'vault').get_all_entries()

        if not entries:
            ctk.CTkLabel(self.scroll_frame, text="Хранилище пусто").pack(pady=20)
            return

        # Фильтрует записи: если поле пустое — покажет всё, если нет — только совпадения
        filtered = [item for item in entries if query in item['service'].lower()]

        if not filtered:
            ctk.CTkLabel(self.scroll_frame, text="Ничего не найдено").pack(pady=20)
            return

        for item in filtered:
            # Создает карточку для одной записи
            card = ctk.CTkFrame(
                self.scroll_frame, fg_color=("#EAEAEA", "#2B2B2B"), corner_radius=10)
            card.pack(fill="x", pady=2, padx=5)

            # --- Строка заголовка карточки-сервиса (📍 + СЕРВИС + Кнопки) ---
            title_frame = ctk.CTkFrame(card, fg_color="transparent")
            title_frame.pack(fill="x", pady=(2, 2), padx=10)

            # 1. Цветной значок сервиса 📍
            icon_label = ctk.CTkLabel(
                title_frame,
                text="📍",
                font=("Roboto", 14),
                text_color="#E74C3C"
            )
            icon_label.pack(side="left")

            # 2. Отображение текста сервиса 📍
            service_label = ctk.CTkLabel(
                title_frame,
                text=f" {item['service'].upper()}",
                font=("Roboto", 14, "bold"),
                text_color="#3498DB"
            )
            service_label.pack(side="left", padx=(2, 0))

            # 3. Кнопка КОПИРОВАТЬ название (📋) сервиса 📍
            copy_label_btn = self.create_copy_button(title_frame, item['service'], "📄")
            copy_label_btn.pack(side="right", padx=(0, 5))

            # --- СТРОКА ЛОГИНА 👤 ---
            login_row = ctk.CTkFrame(card, fg_color="transparent")
            login_row.pack(fill="x", padx=10, pady=(2, 2))

            # 1. Цветная иконка логина 👤
            ctk.CTkLabel(
                login_row,
                text="👤",
                font=("Roboto", 14),
                # text_color="#27AE60"
                fg_color = ("#EAEAEA", "#2B2B2B"),
                text_color = ("#1A1A1A", "#FFFFFF"),
            ).pack(side="left")

            # 2. Отображение текста логина 👤
            ctk.CTkLabel(
                login_row, text=f" {item.get('login', '—')}",
                font=("Consolas", 14)).pack(side="left")

            # 3. Кнопка КОПИРОВАТЬ (📋) логин 👤
            copy_login_btn = self.create_copy_button(login_row, item.get('login', ''), "📄")
            copy_login_btn.pack(side="right", padx=(0, 5))

            # --- СТРОКА ПАРОЛЯ 🔑 ---
            pass_row = ctk.CTkFrame(card, fg_color="transparent", height=35)
            pass_row.pack(fill="x", padx=10, pady=(0, 2))
            pass_row.pack_propagate(False)

            # 1. Цветная иконка пароля 🔑
            ctk.CTkLabel(
                pass_row,
                text="🔑",
                font=("Roboto", 14),
                text_color="#F1C40F"
            ).pack(side="left")

            # 2. Создает Label для пароля (сначала скрытый) 🔑
            hidden_text = "*" * len(item['password'])
            password_display = ctk.CTkLabel(pass_row, text=f" {hidden_text}", font=("Consolas", 13))
            password_display.pack(side="left")

            # 3. Функция переключения видимости пароля 🔑
            def toggle_pass(lbl=password_display, p=item['password']):
                if lbl.cget("text") == f" {p}":
                    lbl.configure(text=f" {'*' * len(p)}")
                else:
                    lbl.configure(text=f" {p}")

            # 4. Кнопка КОПИРОВАТЬ (📋) пароль 🔑
            copy_password_btn = self.create_copy_button(pass_row, item['password'], "📄")
            copy_password_btn.pack(side="right", padx=(0, 5))

            # 5. ГЛАЗОК (Переключатель) пароля 🔑
            eye_btn = ctk.CTkButton(
                pass_row,
                text="",  # Убирает текст 👁️
                image=self.eye_icon,
                width=25,
                height=25,
                fg_color="transparent",
                hover_color=("#EAEAEA", "#2B2B2B"),
                command=toggle_pass
            )
            eye_btn.pack(side="right", padx=(0, 5))
            # Анимация иконки при наведении (с фиксацией текущей кнопки b)
            eye_btn.bind("<Enter>", lambda e, b=eye_btn: b.configure(image=self.eye_icon_large))
            eye_btn.bind("<Leave>", lambda e, b=eye_btn: b.configure(image=self.eye_icon))

            # --- БОЛЬШАЯ КНОПКА УДАЛЕНИЯ (внизу карточки) ---
            delete_btn = ctk.CTkButton(
                card,
                width=80, height=22,
                text="УДАЛИТЬ КАРТОЧКУ",
                fg_color=("#EC7063", "#7B241C"), hover_color=("#7B241C", "#922B21"),
                command=lambda s=item['service']: self.delete_item(s)
            )
            delete_btn.pack(pady=(3, 3), anchor="center")

            # --- Разделитель ---
            separator = ctk.CTkLabel(
                card,
                height=1,
                text="—" * 35,
                text_color="#808080",
                font=("Arial", 12, "bold")
            )
            separator.pack(pady=(0, 0), padx=10, anchor="w")

    def delete_item(self, service_name):
        """Удаляет запись напрямую по нажатию кнопки под карточкой."""
        # Проверка: если имя сервиса пустое, ничего не делает
        if not service_name:
            return

        # Запрос подтверждения у пользователя перед окончательным удалением
        if messagebox.askyesno(
                "Подтверждение",
                f"Внимание!\nВы действительно хотите безвозвратно удалить сервис '{service_name}',"
                f"а также связанные с ним логин и пароль?",
                parent=self):

            # Получает доступ к менеджеру паролей через главное окно
            vault = getattr(self.master, 'vault')
            # Выполняет удаление записи из базы данных
            success = vault.delete_entry_by_service(service_name)
            if success:
                # Обновляет интерфейс (перерисовываем список карточек)
                self.load_passwords()
                messagebox.showinfo(
                    "Готово", f"Записи для '{service_name}' удалены.", parent=self
                )
            else:
                # Сообщение на случай, если запись не удалось найти в базе
                messagebox.showwarning(
                    "Ошибка",
                    f"Сервис '{service_name}' не найден.",
                    parent=self
                )

    @staticmethod
    def change_appearance_mode(new_appearance_mode: str):
        """
        Переключает тему оформления (Dark, Light) для всех
        окон приложения одновременно.
        """
        # 1. Меняет тему в окне
        ctk.set_appearance_mode(new_appearance_mode)
        # 2. ЗАПИСЫВАЕТ В ФАЙЛ
        save_appearance_mode(new_appearance_mode)

    def create_copy_button(self, parent, value, text_icon):
        """Создает универсальную кнопку копирования с анимацией шрифта."""
        btn = ctk.CTkButton(
            parent, text=text_icon, width=37, height=22,
            font=("Arial", 14, "bold"),
            text_color=("#444444", "#CCCCCC"),  # "#00A8FF" - Значок синего цвета
            fg_color=("#EAEAEA", "#2B2B2B"),  # "#3E3E3E",
            hover_color=("#EAEAEA", "#2B2B2B"),  # "#505050",
            corner_radius=7,
            border_width=0,  # Убирает толщину рамки
            border_spacing=0  # Убирает внутренний отступ от рамки
        )
        # Привязывает копирование
        btn.configure(command=lambda: copy_with_animation(self, value, btn))

        # Привязывает изменение размера при наведении
        btn.bind("<Enter>", lambda e: btn.configure(font=("Arial", 16, "bold")))
        btn.bind("<Leave>", lambda e: btn.configure(font=("Arial", 14, "bold")))

        return btn
