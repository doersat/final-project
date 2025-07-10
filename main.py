# Бот-помощник по выбору профессии 🎓✨
import sqlite3
import telebot
from telebot import types

# Подключаем бота (как вкл телефон 📱)
bot = telebot.TeleBot("8050066037:AAGrBK-xrXjXWXB5AGJHk0oJaWP3oFtGodM")  # 👈 сюда токен бота вставить!

# База данных (как тетрадка 📒)
conn = sqlite3.connect('profession_helper.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблички (разделы в тетрадке 📝)
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   name TEXT,
                   direction TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS answers
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   question_num INTEGER,
                   answer INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS professions
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   direction TEXT,
                   result_type TEXT,
                   name TEXT,
                   description TEXT)''')

# Добавляем профессии (чтобы было из чего выбирать 💼)
professions_data = [
    ('Гуманитарий', 'Общительный', 'Журналист', 'Пишешь статьи и берешь интервью у интересных людей! '),
    ('Гуманитарий', 'Аналитик', 'Психолог', 'Помогаешь людям разбираться в их чувствах и проблемах '),
    ('Технарь', 'Логик', 'Программист', 'Создаешь приложения и сайты, как настоящий волшебник! '),
    ('Технарь', 'Творческий', 'Дизайнер', 'Придумываешь красивые сайты и приложения '),
    ('Естественник', 'Умник', 'Ученый', 'Проводишь опыты и делаешь открытия! '),
    ('Естественник', 'Помощник', 'Врач', 'Лечишь людей и спасаешь жизни! 👩')
]

# Проверяем, есть ли профессии в базе
if cursor.execute("SELECT COUNT(*) FROM professions").fetchone()[0] == 0:
    cursor.executemany("INSERT INTO professions (direction, result_type, name, description) VALUES (?, ?, ?, ?)", professions_data)
    conn.commit()

# Вопросы для теста (их 10) ❓
questions = [
    "1. Тебе нравится общаться с людьми? 💬",
    "2. Любишь решать сложные задачки? �",
    "3. Нравится помогать другим? 🤝",
    "4. Любишь что-то создавать своими руками? ✂️",
    "5. Тебе интересно как устроены вещи? 🔍",
    "6. Нравится организовывать мероприятия? 🎉",
    "7. Любишь писать сочинения? 📝",
    "8. Нравится работать с цифрами? 🔢",
    "9. Хочешь делать мир лучше? 🌍",
    "10. Мечтаешь о необычной профессии? 🚀"
]

# Кнопочки для ответов 🔘
def make_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('1 - Не про меня 🙅‍♀️'))
    markup.add(types.KeyboardButton('2 - Скорее нет 🙈'))
    markup.add(types.KeyboardButton('3 - Не знаю 🤷‍♀️'))
    markup.add(types.KeyboardButton('4 - Скорее да 👍'))
    markup.add(types.KeyboardButton('5 - Точно про меня! 💯'))
    return markup

# Кнопочки выбора направления 🗺️
def direction_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Гуманитарий 📚'))
    markup.add(types.KeyboardButton('Технарь 💻'))
    markup.add(types.KeyboardButton('Естественник 🔬'))
    return markup

# Начало работы с ботом 🏁
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 
                    f"Привет, {message.from_user.first_name}! 👋\n"
                    "Я помогу тебе выбрать профессию!\n"
                    "Сначала выбери направление:",
                    reply_markup=direction_buttons())
    
    # Запоминаем пользователя
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", 
                   (message.from_user.id, message.from_user.first_name))
    conn.commit()
    # Обработка выбора направления 🧭
@bot.message_handler(func=lambda m: m.text in ['Гуманитарий 📚', 'Технарь 💻', 'Естественник 🔬'])
def choose_direction(message):
    direction = message.text.split()[0]
    cursor.execute("UPDATE users SET direction = ? WHERE user_id = ?", 
                   (direction, message.from_user.id))
    conn.commit()
    
    # Удаляем предыдущие ответы если были
    cursor.execute("DELETE FROM answers WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    
    bot.send_message(message.chat.id, 
                    f"Отлично! Ты выбрал(а) {direction} направление! 🌟\n"
                    "Теперь ответь на 10 вопросов:\n\n"
                    + questions[0],
                    reply_markup=make_keyboard())

# Обработка ответов на вопросы 📝
user_answers = {}  # Здесь временно храним ответы

@bot.message_handler(func=lambda m: any(str(i) in m.text for i in range(1,6)))
def handle_answer(message):
    try:
        answer = int(message.text.split()[0])
        user_id = message.from_user.id
        
        # Узнаем сколько ответов уже дал пользователь
        cursor.execute("SELECT COUNT(*) FROM answers WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        
        if count < len(questions):
            # Запоминаем ответ
            cursor.execute("INSERT INTO answers (user_id, question_num, answer) VALUES (?, ?, ?)", 
                          (user_id, count+1, answer))
            conn.commit()
            
            # Следующий вопрос или результаты
            if count + 1 < len(questions):
                bot.send_message(message.chat.id, questions[count+1], reply_markup=make_keyboard())
            else:
                show_results(message)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так 😅 Давай попробуем еще раз!")
        bot.send_message(message.chat.id, questions[0], reply_markup=make_keyboard())

# Показываем результаты 🎯
def show_results(message):
    user_id = message.from_user.id
    
    # Получаем все ответы пользователя
    cursor.execute("SELECT answer FROM answers WHERE user_id = ? ORDER BY question_num", (user_id,))
    answers = [row[0] for row in cursor.fetchall()]
    
    # Получаем направление пользователя
    cursor.execute("SELECT direction FROM users WHERE user_id = ?", (user_id,))
    direction = cursor.fetchone()[0]
    
    # Считаем баллы
    social = answers[0] + answers[2] + answers[5] + answers[6]  # Общительность
    logic = answers[1] + answers[4] + answers[7] + answers[9]   # Логика
    creative = answers[3] + answers[6] + answers[8]             # Творчество
    
    # Определяем тип
    if social >= logic and social >= creative:
        result_type = 'Общительный'
    elif logic >= social and logic >= creative:
        result_type = 'Логик'
    else:
        result_type = 'Творческий'
    
    # Ищем подходящие профессии
    cursor.execute("SELECT name, description FROM professions WHERE direction = ? AND result_type = ?", 
                   (direction, result_type))
    professions = cursor.fetchall()
    
    # Формируем сообщение с результатами
    msg = f"Твой результат: {result_type}!\n\n" \
          f"Тебе подойдут эти профессии:\n\n"
    
    for prof in professions:
        msg += f"<b>{prof[0]}</b> - {prof[1]}\n\n"
    
    msg += "Хочешь попробовать еще раз? Нажми /start 🎲"
    
    bot.send_message(message.chat.id, msg, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

# Запускаем бота! 🚀
print("Бот запущен! Работаем! 💪")
bot.polling(none_stop=True)


