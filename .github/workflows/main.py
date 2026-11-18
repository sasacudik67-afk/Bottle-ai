import os
import json
import random
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


DATA_FILE = "bottle_ai_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.setdefault("profile", {})
            data["profile"].setdefault("name", "Саша")
            data["profile"].setdefault("id", "owner")
            data["profile"].setdefault("created", "")

            data.setdefault("memory", [])
            data.setdefault("learned", {})

            data.setdefault("settings", {})
            data["settings"].setdefault("bot_name", "Бутылка ИИ")

            return data
        except Exception:
            pass

    data = {
        "profile": {
            "name": "Саша",
            "id": "owner",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "memory": [],
        "learned": {},
        "settings": {
            "bot_name": "Бутылка ИИ"
        }
    }

    save_data(data)
    return data


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Ошибка сохранения:", e)


data = load_data()


# ==========================================
# ОТВЕТЫ БОТА
# ==========================================

def generate_answer(message):
    text = message.strip()
    lower = text.lower()

    # Проверяем то, чему Бутылку научили
    if lower in data["learned"]:
        return data["learned"][lower]

    if lower in ["привет", "здравствуй", "хай", "hello", "hi"]:
        return random.choice([
            "Привет!",
            "Привет! Я Бутылка ИИ.",
            "Здравствуй!",
            "Привет, рад тебя видеть!"
        ])

    if "как дела" in lower:
        return "У меня всё хорошо! Я пока ещё учусь."

    if "как тебя зовут" in lower:
        return "Меня зовут " + data["settings"]["bot_name"] + "."

    if "кто ты" in lower:
        return (
            "Я " + data["settings"]["bot_name"] +
            ". Пока я простая версия ИИ, но меня можно обучать."
        )

    if "как меня зовут" in lower:
        return "Тебя зовут " + data["profile"]["name"] + "."

    if "спасибо" in lower:
        return "Пожалуйста!"

    if "пока" in lower:
        return "Пока!"

    return (
        "Я пока не знаю, что ответить.\n"
        "Ты можешь научить меня командой:\n\n"
        "/R вопрос = ответ"
    )


# ==========================================
# КОМАНДЫ
# ==========================================

def process_command(text):
    parts = text.strip().split(maxsplit=1)

    command = parts[0].lower()

    argument = ""
    if len(parts) > 1:
        argument = parts[1].strip()

    # /H — HELP
    if command == "/h":
        return (
            "Команды Бутылки ИИ:\n\n"
            "/H — помощь\n"
            "/P — профиль\n"
            "/N имя — изменить твоё имя\n"
            "/R текст — запомнить\n"
            "/R вопрос = ответ — обучить ответу\n"
            "/M — показать память\n"
            "/F номер — забыть запись\n"
            "/C — очистить память\n"
            "/B имя — изменить имя Бутылки\n"
            "/T — время"
        )

    # /P — PROFILE
    if command == "/p":
        return (
            "Профиль:\n\n"
            "Имя: " + data["profile"]["name"] + "\n"
            "ID: " + data["profile"]["id"] + "\n"
            "Записей памяти: " + str(len(data["memory"])) + "\n"
            "Обученных ответов: " + str(len(data["learned"]))
        )

    # /N — NAME
    if command == "/n":
        if not argument:
            return "Напиши имя после /N."

        data["profile"]["name"] = argument
        save_data(data)

        return "Хорошо. Теперь твоё имя — " + argument + "."

    # /R — REMEMBER + LEARN
    if command == "/r":

        if not argument:
            return (
                "Использование:\n\n"
                "/R текст\n\n"
                "или\n\n"
                "/R вопрос = ответ"
            )

        # Обучение через =
        if "=" in argument:
            question, answer = argument.split("=", 1)

            question = question.strip()
            answer = answer.strip()

            if not question:
                return "Ты не указал вопрос."

            if not answer:
                return "Ты не указал ответ."

            data["learned"][question.lower()] = answer
            save_data(data)

            return (
                "Готово! Я научился.\n\n"
                "Если ты напишешь:\n"
                + question +
                "\n\nЯ отвечу:\n"
                + answer
            )

        # Обычная память
        data["memory"].append(argument)
        save_data(data)

        return "Запомнил: " + argument

    # /M — MEMORY
    if command == "/m":

        if not data["memory"] and not data["learned"]:
            return "Моя память пока пустая."

        result = "Моя память:\n\n"

        if data["memory"]:
            result += "Обычная память:\n"

            for i, item in enumerate(data["memory"], 1):
                result += str(i) + ". " + item + "\n"

            result += "\n"

        if data["learned"]:
            result += "Обученные ответы:\n"

            for question, answer in data["learned"].items():
                result += (
                    "«" + question +
                    "» → «" + answer + "»\n"
                )

        return result.strip()

    # /F — FORGET
    if command == "/f":

        if not argument:
            return "Напиши номер записи. Например: /F 1"

        try:
            number = int(argument)
        except ValueError:
            return "Номер должен быть числом."

        if number < 1 or number > len(data["memory"]):
            return "Такой записи нет."

        removed = data["memory"].pop(number - 1)
        save_data(data)

        return "Забыл: " + removed

    # /C — CLEAR
    if command == "/c":
        data["memory"].clear()
        save_data(data)

        return "Обычная память очищена."

    # /B — BOT NAME
    if command == "/b":

        if not argument:
            return "Напиши новое имя после /B."

        data["settings"]["bot_name"] = argument
        save_data(data)

        return "Теперь меня зовут " + argument + "."

    # /T — TIME
    if command == "/t":
        return "Сейчас: " + datetime.now().strftime("%H:%M:%S")

    return "Неизвестная команда. Напиши /H."


# ==========================================
# СООБЩЕНИЕ
# ==========================================

class ChatMessage(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.text_size = (Window.width - dp(35), None)
        self.padding = (dp(8), dp(8))

        self.bind(texture_size=self.update_height)

    def update_height(self, *args):
        self.height = self.texture_size[1] + dp(10)


# ==========================================
# ПРИЛОЖЕНИЕ
# ==========================================

class BottleAI(App):

    def build(self):

        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass

        root = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        # Заголовок
        self.header = Label(
            text=data["settings"]["bot_name"],
            font_size=dp(23),
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )

        root.add_widget(self.header)

        # ==================================
        # ЧАТ
        # ==================================

        self.scroll = ScrollView(
            do_scroll_x=False
        )

        self.chat = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(4),
            size_hint_y=None
        )

        self.chat.bind(
            minimum_height=self.chat.setter("height")
        )

        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        # ==================================
        # ПАНЕЛЬ КОМАНД
        # ==================================

        command_scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            size_hint_y=None,
            height=dp(45),
            bar_width=dp(0)
        )

        self.command_bar = BoxLayout(
            orientation="horizontal",
            spacing=dp(4),
            padding=(dp(2), dp(2)),
            size_hint_x=None
        )

        self.command_bar.bind(
            minimum_width=self.command_bar.setter("width")
        )

        commands = [
            "/H",
            "/P",
            "/N",
            "/R",
            "/M",
            "/F",
            "/C",
            "/B",
            "/T"
        ]

        for command in commands:

            button = Button(
                text=command,
                size_hint_x=None,
                width=dp(65),
                font_size=dp(12)
            )

            button.bind(
                on_release=lambda instance, cmd=command:
                self.insert_command(cmd)
            )

            self.command_bar.add_widget(button)

        command_scroll.add_widget(self.command_bar)
        root.add_widget(command_scroll)

        # ==================================
        # ПОЛЕ ВВОДА
        # ==================================

        bottom = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(55)
        )

        self.input = TextInput(
            hint_text="Написать сообщение...",
            multiline=False,
            font_size=dp(17),
            padding=(dp(10), dp(10))
        )

        send_button = Button(
            text="➤",
            font_size=dp(24),
            size_hint_x=None,
            width=dp(58)
        )

        send_button.bind(
            on_release=self.send_message
        )

        self.input.bind(
            on_text_validate=self.send_message
        )

        bottom.add_widget(self.input)
        bottom.add_widget(send_button)

        root.add_widget(bottom)

        # ==================================
        # ПРИВЕТСТВИЕ
        # ==================================

        self.add_message(
            data["settings"]["bot_name"],
            "Привет! Я Бутылка ИИ.\n"
            "Ты можешь разговаривать со мной "
            "или обучать меня командой /R."
        )

        return root

    # ==================================
    # ВСТАВКА КОМАНДЫ
    # ==================================

    def insert_command(self, command):

        self.input.text = command + " "

        # Правильный формат курсора для Kivy
        self.input.cursor = (len(self.input.text), 0)

        self.input.focus = True

    # ==================================
    # ДОБАВЛЕНИЕ СООБЩЕНИЯ
    # ==================================

    def add_message(self, sender, message):

        label = ChatMessage(
            text=sender + ":\n" + message,
            font_size=dp(16),
            halign="left",
            valign="top"
        )

        self.chat.add_widget(label)

        Clock.schedule_once(
            lambda dt: setattr(
                self.scroll,
                "scroll_y",
                0
            ),
            0.05
        )

    # ==================================
    # ОТПРАВКА
    # ==================================

    def send_message(self, *args):

        text = self.input.text.strip()

        if not text:
            return

        self.input.text = ""

        # Сообщение пользователя
        self.add_message(
            "Ты",
            text
        )

        # Команда
        if text.startswith("/"):
            answer = process_command(text)

            self.header.text = data["settings"]["bot_name"]

        # Обычный текст
        else:
            answer = generate_answer(text)

        # Ответ Бутылки
        self.add_message(
            data["settings"]["bot_name"],
            answer
        )


# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == "__main__":
    BottleAI().run()