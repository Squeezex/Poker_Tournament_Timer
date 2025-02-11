from flask import Flask, render_template, request, jsonify
import time
import threading

app = Flask(__name__)

blinds = [(10, 20), (20, 40), (30, 60), (40, 80), (50, 100)]  # Пример уровней блайндов
time_interval = 15 * 60  # Интервал в секундах (15 минут)
break_time = 15 * 60  # Время перерыва (15 минут)
current_blind_index = 0
players = 20  # Начальное количество игроков
is_break = False
remaining_time = time_interval

def blind_timer():
    global current_blind_index, is_break, remaining_time
    while current_blind_index < len(blinds) - 1:
        while remaining_time > 0:
            time.sleep(1)
            remaining_time -= 1
        if is_break:
            remaining_time = time_interval
            is_break = False
        else:
            current_blind_index += 1
            remaining_time = time_interval

# Запускаем таймер в отдельном потоке
threading.Thread(target=blind_timer, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html', current_blinds=blinds[current_blind_index], 
                           next_blinds=blinds[current_blind_index + 1] if current_blind_index + 1 < len(blinds) else None,
                           players=players, remaining_time=remaining_time, is_break=is_break)

@app.route('/eliminate', methods=['POST'])
def eliminate_player():
    global players
    if players > 0:
        players -= 1
    return jsonify({'players': players})

@app.route('/break', methods=['POST'])
def start_break():
    global is_break, remaining_time
    if not is_break:
        is_break = True
        remaining_time = break_time
    return jsonify({'is_break': is_break, 'remaining_time': remaining_time})

if __name__ == '__main__':
    app.run(debug=True)
