import tkinter as tk
import time
import threading
from tkinter import simpledialog

class PokerTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Tournament Timer")
        
        # Устанавливаем размер окна (ширина x высота)
        self.root.geometry("500x600")
        
        # Шрифт для всех элементов
        self.font = ("Arial", 14)
        
        # Начальные настройки времени
        self.blind_time_default = 20 * 60  # 20 минут
        self.break_time_default = 15 * 60  # 15 минут
        self.time_interval = self.blind_time_default  # Время на блайнды
        self.break_time_remaining = self.break_time_default  # Время на перерыв
        self.current_blind_index = 0
        self.players = 20
        self.total_chips = 2000 * self.players
        self.blind_time_remaining = self.time_interval
        self.in_break = False
        self.tournament_started = False
        self.timer_thread = None
        self.thread_running = False
        
        self.blinds = [
            (5, 10, 0), (15, 30, 0), (25, 50, 0), (50, 100, 0),
            ('Break',),
            (75, 150, 0), (100, 200, 25), (150, 300, 50), (200, 400, 75),
            ('Break',),
            (300, 600, 100), (400, 800, 100), (500, 1000, 150), (600, 1200, 200),
            (800, 1600, 200), (1000, 2000, 200)
        ]
        
        self.create_widgets()
    
    def create_widgets(self):
        self.level_label = tk.Label(self.root, text=f"Level: {self.current_blind_index + 1}", font=self.font)
        self.level_label.pack()
        
        self.blinds_label = tk.Label(self.root, text=self.get_blind_text(), font=self.font)
        self.blinds_label.pack()
        
        self.timer_label = tk.Label(self.root, text=f"Time: {self.format_time(self.blind_time_remaining)}", font=self.font)
        self.timer_label.pack()
        
        self.players_label = tk.Label(self.root, text=f"Players: {self.players} out of 20", font=self.font)
        self.players_label.pack()
        
        self.avg_stack_label = tk.Label(self.root, text=f"Average Stack: {self.average_stack()}", font=self.font)
        self.avg_stack_label.pack()
        
        # Кнопки, размещаем внизу
        self.start_button = tk.Button(self.root, text="Start Tournament", command=self.start_tournament, font=self.font)
        self.start_button.pack(side="bottom", pady=5)
        
        self.reset_button = tk.Button(self.root, text="Reset Tournament", command=self.reset_tournament, font=self.font)
        self.reset_button.pack(side="bottom", pady=5)
        
        self.eliminate_button = tk.Button(self.root, text="Eliminate Player", command=self.eliminate_player, font=self.font)
        self.eliminate_button.pack(side="bottom", pady=5)
        
        self.break_button = tk.Button(self.root, text="Start Break", command=self.start_break_thread, font=self.font)
        self.break_button.pack(side="bottom", pady=5)
        
        self.settings_button = tk.Button(self.root, text="Settings", command=self.open_settings, font=self.font)
        self.settings_button.pack(side="bottom", pady=5)
    
    def get_blind_text(self):
        current_blind = self.blinds[self.current_blind_index]
        if current_blind == ('Break',):
            return "Break Time"
        
        next_blind = self.blinds[self.current_blind_index + 1] if self.current_blind_index + 1 < len(self.blinds) else None
        
        next_blind_text = f"{next_blind[0]}/{next_blind[1]}" if next_blind else "None"
        return f"Blinds: {current_blind[0]}/{current_blind[1]}, Ante: {current_blind[2]}\nNext: {next_blind_text}"
    
    def format_time(self, seconds):
        return f"{seconds // 60}:{seconds % 60:02d}"
    
    def start_tournament(self):
        if not self.tournament_started:
            self.tournament_started = True
            # Запускаем таймер на блайнды с текущими настройками
            self.thread_running = True
            self.timer_thread = threading.Thread(target=self.blind_timer, daemon=True)
            self.timer_thread.start()
    
    def reset_tournament(self):
        # Останавливаем турнир, если он был запущен
        self.tournament_started = False
        self.thread_running = False
        self.current_blind_index = 0
        self.blind_time_remaining = self.time_interval
        self.break_time_remaining = self.break_time_default
        self.players = 20
        self.total_chips = 2000 * self.players
        self.in_break = False
        
        # Останавливаем текущий поток, если турнир запущен
        if self.timer_thread and self.thread_running:
            self.thread_running = False  # Останавливаем поток
            self.timer_thread.join()  # Ждем завершения потока
        
        # Обновляем интерфейс
        self.update_display()
    
    def open_settings(self):
        # Открываем окно с настройками для ввода времени на блайнды и перерыв
        blind_time = simpledialog.askinteger("Settings", "Enter blind time in minutes:", parent=self.root, minvalue=1, maxvalue=60, initialvalue=self.time_interval // 60)
        break_time = simpledialog.askinteger("Settings", "Enter break time in minutes:", parent=self.root, minvalue=1, maxvalue=60, initialvalue=self.break_time_remaining // 60)
        
        if blind_time is not None and break_time is not None:
            self.time_interval = blind_time * 60
            self.break_time_remaining = break_time * 60
            # Обновляем интерфейс с новыми значениями
            self.update_display()
    
    def blind_timer(self):
        while self.current_blind_index < len(self.blinds) - 1 and self.thread_running:
            while self.blind_time_remaining > 0 and not self.in_break and self.thread_running:
                time.sleep(1)
                self.blind_time_remaining -= 1
                self.update_display()
            if not self.in_break:
                self.current_blind_index += 1
                if self.blinds[self.current_blind_index] == ('Break',):
                    self.start_break()
                else:
                    self.blind_time_remaining = self.time_interval
                self.update_display()
    
    def start_break_thread(self):
        threading.Thread(target=self.start_break, daemon=True).start()
    
    def start_break(self):
        self.in_break = True
        self.timer_label.config(fg="red")  # Изменяем цвет таймера на красный
        while self.break_time_remaining > 0 and self.thread_running:
            time.sleep(1)
            self.break_time_remaining -= 1
            self.update_display()
        self.in_break = False
        self.blind_time_remaining = self.time_interval
        self.timer_label.config(fg="black")  # Возвращаем цвет таймера в черный
        self.update_display()
    
    def eliminate_player(self):
        if self.players > 0:
            self.players -= 1
            self.update_display()
    
    def average_stack(self):
        return self.total_chips // self.players if self.players > 0 else 0
    
    def update_display(self):
        self.level_label.config(text=f"Level: {self.current_blind_index + 1}")
        self.blinds_label.config(text=self.get_blind_text())
        if self.in_break:
            self.timer_label.config(text=f"Break: {self.format_time(self.break_time_remaining)}")
        else:
            self.timer_label.config(text=f"Time: {self.format_time(self.blind_time_remaining)}")
        self.players_label.config(text=f"Players: {self.players} out of 20")
        self.avg_stack_label.config(text=f"Average Stack: {self.average_stack()}")
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTournament(root)
    root.mainloop()
