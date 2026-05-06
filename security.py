def start_bruteforce_lock(root, seconds, button, entry, label):
    """
    Запускает блокировку интерфейса при подборе пароля.
    root - окно, seconds - время, button - кнопка, entry - поле ввода, label - подсказка.
    """
    def update_status(remaining):
        if remaining > 0:
            button.configure(text=f"БЛОКИРОВКА ({remaining}s)")
            # Запускает следующий тик через 1 секунду
            root.after(1000, lambda: update_status(remaining - 1))
        else:
            # Разблокировка
            button.configure(state="normal", text="ВОЙТИ")
            entry.configure(state="normal")
            label.configure(text="Введите мастер-пароль:", text_color="white")
            entry.delete(0, 'end')
            entry.focus()
            # Сбрасываем счетчик в самом объекте окна
            root.failed_attempts = 0
            root.lock_time_remaining = 0

    # Сама блокировка
    button.configure(state="disabled")
    entry.configure(state="disabled")
    update_status(seconds)

class InactivityTracker:
    """Класс-помощник для отслеживания бездействия."""
    def __init__(self, root, timeout=300000):
        self.root = root
        self.timeout = timeout
        self.inactivity_job = None

    def start(self):
        """Запуск отслеживания."""
        self.root.bind_all("<Any-KeyPress>", self.reset_timer)
        self.root.bind_all("<Any-ButtonPress>", self.reset_timer)
        self.root.bind_all("<Motion>", self.reset_timer)
        self.reset_timer()

    def reset_timer(self, event=None):
        """Сброс и перезапуск таймера."""
        _ = event  # Говорим редактору, что мы в курсе про event
        if self.inactivity_job:
            self.root.after_cancel(self.inactivity_job)
        self.inactivity_job = self.root.after(self.timeout, self.lock)

    def lock(self):
        """Логика блокировки."""
        # Закрываем дочерние окна, если они есть у главного окна
        if hasattr(self.root, 'vault_window') and self.root.vault_window:
            self.root.vault_window.destroy()

        print("Автоблокировка активирована.")
        self.root.destroy()
