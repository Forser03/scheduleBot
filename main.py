import telebot
from telebot import types
import psycopg2
from datetime import date

bot = telebot.TeleBot(open("D:/PythonWorks/API_keys/m_bin2311_bot.txt").readline())
connection = psycopg2.connect(database="schedule",
                              user="postgres",
                              password="12345678",
                              host="localhost", port="5432")
cursor = connection.cursor()


class UserNowIn:
    def __init__(self, sl_week_even):
        self.weekEven = sl_week_even


usersDict = {}


def is_even():
    today = date.today()
    delta = date(today.year, today.month, today.day) - date(2023, 8, 28)
    return (delta.days // 7 + 1) % 2 == 0


def start(message_id):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add("Расписание")
    keyboard.add("Помощь")
    keyboard.add("Перезапуск")
    bot.send_message(message_id, 'Здравствуйте! Выберите необходимое действие с помощью кнопок внизу. '
                     'Если кнопки не отображаются, используйте команду /start',
                     reply_markup=keyboard)


def restart(message_id):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add("Расписание")
    keyboard.add("Помощь")
    keyboard.add("Перезапуск")
    bot.send_message(message_id, 'Вы вернулись в главное меню. Если кнопки не отображаются, используйте команду /start',
                     reply_markup=keyboard)


def help_msg(message_id):
    bot.send_message(message_id, """Этот бот создан для отображения расписания ВУЗа МТУСИ. Доступные комманды:
/start - перезапуск бота
/help - отображение этого сообщения
/week - отображение чётности текущей недели
/mtuci - ссылка на сайт МТУСИ
Большенство действий удобно выполнять при помощи кнопок под полем ввода сообщения""")


def error_enter(message_id):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add("Расписание")
    keyboard.add("Помощь")
    keyboard.add("Перезапуск")
    bot.send_message(message_id, 'Неверный ввод! Вы вернулись в главное меню. '
                                 'Если кнопки не отображаются, используйте команду /start', reply_markup=keyboard)


@bot.message_handler(commands=["start"])
def startcom(message):
    start(message.chat.id)
    return


@bot.message_handler(commands=["mtuci"])
def mtuci(message):
    bot.send_message(message.chat.id, "https://mtuci.ru/")


@bot.message_handler(commands=["week"])
def week(message):
    bot.send_message(message.chat.id, f"Сейчас {'чётная' if is_even() else 'нечётная'} неделя")


@bot.message_handler(commands=["help"])
def helpcom(message):
    help_msg(message.chat.id)


@bot.message_handler(content_types=["text"])
def answer(message):
    if message.text.lower() == "перезапуск":
        start(message.chat.id)
        return

    if message.text.lower() == "помощь":
        help_msg(message.chat.id)
        return

    if message.text.lower() == "расписание":
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add("Текущая неделя")
        keyboard.add("Следующая неделя")
        keyboard.add("Вернуться в главное меню")
        msg = bot.send_message(message.chat.id, f"Сейчас {'чётная' if is_even else 'нечётная'} неделя. "
                                                f"На какую неделю Вы хотите увидеть расписание: ",
                                                reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_week)
        return

    else:
        error_enter(message.chat.id)
        return


def process_week(message):
    if message.text.lower() in ["текущая неделя", "следующая неделя"]:
        usersDict[message.chat.id] = UserNowIn((is_even() if message.text.lower() == "текущая неделя" else not is_even()))
        keyboard = types.ReplyKeyboardMarkup()
        for i in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Вернуться в главное меню"]:
            keyboard.add(i)
        msg = bot.send_message(message.chat.id, f"На какой день Вы хотите увидеть расписание: ", reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_day)
        return
    if message.text.lower() == "вернуться в главное меню":
        restart(message.chat.id)
        return
    else:
        error_enter(message.chat.id)
        return


def process_day(message):
    if message.text.lower() in ["понедельник", "вторник", "среда", "четверг", "пятница"]:
        cursor.execute("SELECT subjects.name, timetable.room_numb, timetable.start_time, teachers.full_name "
                       "FROM timetable, subjects, teachers "
                       "WHERE timetable.subject = subjects.id AND "
                       "(timetable.subject = teachers.subject1 OR timetable.subject = teachers.subject2) AND "
                       "timetable.week_is_even = %s AND timetable.day=%s ORDER BY timetable.start_time",
                       (str(usersDict[message.chat.id].weekEven).upper(), str(message.text.title())))
        records = list(cursor.fetchall())
        to_send = f"{message.text.title()}\n{'_'*65}\n"
        for i in range(len(records)):
            to_send += f"{i+1}: {records[i][0]} - {records[i][1]} - {records[i][2]} - {records[i][3]}\n"
        to_send += '_'*65
        bot.send_message(message.chat.id, to_send)
        restart(message.chat.id)
        return
    if message.text.lower() == "вернуться в главное меню":
        restart(message.chat.id)
        return
    else:
        error_enter(message.chat.id)
        return


bot.polling()
