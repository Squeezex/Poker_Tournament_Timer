import tkinter as tk
import time
import threading

class PokerTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Tournament Timer")
        
        # Размер окна
        self.root.geometry("800x600")
        
        # Шрифт для всех элементов
        self.font = ("Arial", 24)
        
        # Начальные настройки времени в секундах
        self.blind_time_default = 20 # Время блайндов указывается в секундах
        self.break_time_default = 15  # Время перерыва указывается в секундах
        self.time_interval = self.blind_time_default  # Время на блайнды
        self.break_time_remaining = self.break_time_default  # Время на перерыв
        self.current_blind_index = 0
        self.players = 20 # Кол-во игроков
        self.total_chips = 2000 * self.players # Стек
        self.blind_time_remaining = self.time_interval
        self.in_break = False  # Флаг, который показывает, что сейчас перерыв
        self.tournament_started = False
        self.timer_thread = None
        self.break_thread = None
        self.thread_running = False
        
        # Блайнды, (бб,сб,анте) 14 уровней
        self.blinds = [
            (5, 10, 0), (15, 30, 0), (25, 50, 0), (50, 100, 0),
            (75, 150, 0), (100, 200, 25), (150, 300, 50), (200, 400, 75),
            (300, 600, 100), (400, 800, 100), (500, 1000, 150), (600, 1200, 200),
            (800, 1600, 200), (1000, 2000, 200)
        ]
        
        self.create_widgets()
    
    def create_widgets(self):
        # Создаем основной Frame для левого и правого блоков
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Левый блок для уровня и блайндов и таймера
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", padx=20, pady=10, anchor="w")
        
        self.level_label = tk.Label(left_frame, text=f"Level: {self.current_blind_index + 1}", font=self.font)
        self.level_label.pack()
        
        self.blinds_label = tk.Label(left_frame, text=self.get_blind_text(), font=self.font)
        self.blinds_label.pack()
        
        self.timer_label = tk.Label(left_frame, text=f"Time: {self.format_time(self.blind_time_remaining)}", font=self.font)
        self.timer_label.pack()
        
        # Правый блок для оставшихся игроков и среднего стэка
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", padx=20, pady=10, anchor="e")
        
        self.players_label = tk.Label(right_frame, text=f"Players: {self.players} out of 20", font=self.font)
        self.players_label.pack()
        
        self.avg_stack_label = tk.Label(right_frame, text=f"Average Stack: {self.average_stack()}", font=self.font)
        self.avg_stack_label.pack()
        
        # Кнопки в одной строке старт, выкинуть игрока, перерыв
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(side="bottom", fill="x", pady=10)

        self.start_button = tk.Button(buttons_frame, text="Start Tournament", command=self.start_tournament, font=self.font)
        self.start_button.pack(side="left", padx=10)

        self.eliminate_button = tk.Button(buttons_frame, text="Eliminate Player", command=self.eliminate_player, font=self.font)
        self.eliminate_button.pack(side="left", padx=10)

        self.break_button = tk.Button(buttons_frame, text="Start Break", command=self.start_break, font=self.font)
        self.break_button.pack(side="left", padx=10)
    
    def get_blind_text(self):
        current_blind = self.blinds[self.current_blind_index]
    
    # Текущие блайнды
        if self.current_blind_index >= len(self.blinds) - 1:
        # Если последний уровень, показываем "This is Last Level"
            next_blind_text = "This is Last Level"
        else:
            next_blind = self.blinds[self.current_blind_index + 1]
            next_blind_text = f"{next_blind[0]}/{next_blind[1]}" if len(next_blind) > 1 else "None"
    
        return f"Blinds: {current_blind[0]}/{current_blind[1]}, Ante: {current_blind[2]}\nNext: {next_blind_text}"
    
    def format_time(self, seconds):
        return f"{seconds // 60}:{seconds % 60:02d}"
    
    def start_tournament(self):
        if not self.tournament_started:
            self.tournament_started = True
            # Запускаем таймер на блайнды
            self.thread_running = True
            self.timer_thread = threading.Thread(target=self.blind_timer, daemon=True)
            self.timer_thread.start()
    
    def start_break(self):
        if not self.in_break:  # Если не перерыв, запускаем
            # Останавливаем таймер блайндов
            self.thread_running = False
            self.in_break = True
            self.break_time_remaining = self.break_time_default * 1  # переводим минуты в секунды если нужно, сейчас не переводится
            # Запускаем таймер для перерыва в отдельном потоке
            self.break_thread = threading.Thread(target=self.break_timer, daemon=True)
            self.break_thread.start()
    
    def break_timer(self):
        while self.break_time_remaining > 0 and self.in_break:
            time.sleep(1)
            self.break_time_remaining -= 1
            self.update_display()
        
        # Перерыв завершен, восстанавливаем таймер блайндов
        self.in_break = False
        self.blind_time_remaining = self.time_interval  # Возвращаем стандартное время на блайнды
        self.thread_running = True  # Разрешаем таймеру блайндов продолжиться
        self.update_display()
        # Запускаем таймер блайндов, если еще не завершился турнир
        self.timer_thread = threading.Thread(target=self.blind_timer, daemon=True)
        self.timer_thread.start()
    
    def blind_timer(self):
        while self.current_blind_index < len(self.blinds) - 1 and self.thread_running:
            while self.blind_time_remaining > 0 and not self.in_break and self.thread_running:
                time.sleep(1)
                self.blind_time_remaining -= 1
                self.update_display()
            
            # Если достигли последнего уровня, останавливаем таймер
            if self.current_blind_index >= len(self.blinds) - 1:
                self.blind_time_remaining = 0  # Останавливаем таймер на последнем уровне
                self.update_display()
                break
            
            if not self.in_break:
                self.current_blind_index += 1
                self.blind_time_remaining = self.time_interval  # Сбрасываем время на блайнды для следующего уровня
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
    
    # Если это последний уровень, скрываем таймер
        if self.current_blind_index >= len(self.blinds) - 1:
           self.timer_label.config(text="", fg="black")  # Скрываем таймер, текс просто заменяется пустым
        else:
        # Меняем цвет таймера на красный, если идет перерыв
            if self.in_break:
               self.timer_label.config(text=f"Break: {self.format_time(self.break_time_remaining)}", fg="red")
            else:
               self.timer_label.config(text=f"Time: {self.format_time(self.blind_time_remaining)}", fg="black")
    
        self.players_label.config(text=f"Players: {self.players} out of 20") # нужно поменять кол-во игроков здесь если надо
        self.avg_stack_label.config(text=f"Average Stack: {self.average_stack()}")
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTournament(root)
    root.mainloop()

# Чтобы сбилдить клиент .exe нужно запустить в папке cmd "pyinstaller --onefile --windowed poker_timer.py"