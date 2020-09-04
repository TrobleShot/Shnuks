import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime #время
import threading #потоки
import time
import pymysql #бд
from pymysql.cursors import DictCursor
import wikipedia #википедия
import pyowm
import math #округлить число
from translate import Translator #переводчик 


class Mail:
	def __init__(self, hours: int, minutes: int, message: str):
		self.hours = hours
		self.minutes = minutes
		self.message = message
		self.send = True

#--------------------------------------------------------------------------------

mails = [Mail(8, 10, "Начало первой пары через 5 минут!"), #Часы\Минуты\Текст
		 Mail(8, 15, "Первая пара началась!"),
		 Mail(9, 20, "Начало второй пары через 5 минут!"),
	 	 Mail(9, 25, "Вторая пара началась!"),
		 Mail(10, 30, "Начало третьей пары через 5 минут!"),
		 Mail(10, 35, "Третья пара началась!")]

token = "663f6be35f8b95159a155b8534c52b28c2a6a1b6252b3f526c4b03788f73e6d1cc66d65fa978eddbea104"

connection = pymysql.connect(host='db4free.net',
						  	 user='vkrsbot',
						  	 password='89181449101',
						  	 db='vkrsbot',
						  	 charset='utf8mb4',
						  	 cursorclass=DictCursor)

keyboard = '''
{
   "one_time": false,
   "buttons": [
      [
         {
            "action": {
               "type": "text",
               "label": "Подписаться"
            },
            "color": "positive"
         },
         {
            "action": {
               "type":"text",
               "label":"Отписаться"
            },
            "color": "negative"
         },
		 {
            "action": {
               "type":"text",
               "label":"Команды"
            },
            "color": "primary"
		}
		 
      ]
   ]
}
'''

#--------------------------------------------------------------------------------

class Bot:
	def __init__(self):
		try:
			print("Подключение к бд...")
			print("Подключился!")
			print("Создание таблицы Users, если она не существует...")
			with connection.cursor() as cursor:
				cursor.execute("CREATE TABLE IF NOT EXISTS Users (user_id INT PRIMARY KEY);")
			print("Создал!")

			self.vk = vk_api.VkApi(token=token)
			self.longpoll = VkLongPoll(self.vk)

			print("Создаю поток...")
			thread = threading.Thread(target=self.check)
			thread.start()
			print("Создал!")

			print("Запускаю антисон...")
			self.antisleep()
			print("Запустил!")

			print("Запускаю вечный онлайн...")
			self.online()
			print("Запустил!")

			print("Бот запущен")


		except Exception as ex:
			print("error (__init__):", ex)


	def online(self): #Сообщество всегда онлайн
		try:
			while True:
				self.vk.method("groups.enableOnline", {"group_id": 193390774})
				time.sleep(600)
		except Exception as ex:
			print("error (online):", ex)


	def write_msg(self, user_id, message):
		try:
			self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': random.randint(0, 100000000)})
		except Exception as ex:
			print("error (write_msg, {0}, {1}):".format(user_id, message), ex)


	def check(self):
		while True:
			try:
				now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
				if now.isoweekday() not in [7]: # Если сегодня не суббота, воскресенье продолжай код... not in [6, 7]:
					for mail in mails:
						if now.hour == mail.hours and now.minute == mail.minutes:
							if mail.send:
								mail.send = False
								with connection.cursor() as cursor:
									cursor.execute("SELECT user_id FROM Users")
									for row in cursor:
										self.write_msg(row["user_id"], mail.message)
						else:
							mail.send = True

			except Exception as ex:
				print("error (check):", ex)


	def antisleep(self): #Чтобы не уснула бесплатная БД 
		try:
			threading.Timer(600, self.antisleep).start()
			with connection.cursor() as cursor:
				cursor.execute("SELECT * FROM Users")
		except Exception as ex:
			print("error (antisleep):", ex)

	
	def start(self):
		while True:
			try:
				for event in self.longpoll.listen():
					if event.type == VkEventType.MESSAGE_NEW and event.to_me:
						id = event.user_id
						msg = event.text.lower()
						if msg == "подписаться":
							with connection.cursor() as cursor:
								cursor.execute("INSERT IGNORE INTO Users (user_id) VALUES (%s)", id)
								if cursor.rowcount == 0:
									self.write_msg(id, "Вы уже подписаны!")
								else:
									self.write_msg(id, "Вы успешно подписались на рассылку\nВведите \"Отписаться\" чтобы отключить рассылку.")
								connection.commit()


						elif msg == "отписаться":
							with connection.cursor() as cursor:
								cursor.execute("DELETE FROM Users WHERE user_id = %s", id)
								if cursor.rowcount != 0:
									self.write_msg(id, "Вы отписались от рассылки")
								else:
									self.write_msg(id, "Вы не подписывались")
								connection.commit()


						elif msg == "команды":
							self.write_msg(id, "⚙Список команд:")
							self.write_msg(id, "🔍Для поиска в Википедии введите: \"Поиск <ваш запрос>\". ")
							self.write_msg(id, "🌦 Чтобы узнать погоду введите: \"Погода <город>\". ")
							self.write_msg(id, "🕐Чтобы получать уведомления о начале пары введите: \"Подписаться\". ")
							connection.commit()


						elif msg.startswith('поиск '):
							try:
								wikipedia.set_lang("ru")
								find = msg.replace('поиск ', '')
								self.write_msg(id, "Ищу результаты в википедии: " + find.title() + " ...")
								infor = wikipedia.summary(find, sentences=3)
								self.write_msg(id, str(infor))
							except:
								self.write_msg(id, "Результат не найден, попробуйте ещё раз.")
							
							connection.commit()
						

						elif msg.startswith('погода '):
							city = msg.replace('погода ', '')
							try:
								self.write_msg(id, "Измеряю погоду в городе " + city.title() + "...")
								owm = pyowm.OWM('523f5772a5e781cf832e2150a2b78b02', language = 'ru')
								observation = owm.weather_at_place(city)
								w = observation.get_weather()
								status = w.get_detailed_status()
								temperature = w.get_temperature('celsius')['temp']
								self.write_msg(id, "В городе " + city.title() + " " + str(math.ceil(temperature)) + "°. " + status.title())
							except:
								self.write_msg(id, "Город не найден, попробуйте ещё раз.")

							connection.commit()


						elif msg.startswith('rus eng '):
							trns = msg.replace('rus eng ', '')
							self.write_msg(id, "Перевожу текст с русского на английский...")
							translator= Translator(from_lang="russian",to_lang="english")
							self.write_msg(id, translator.translate(trns))


						elif msg.startswith('eng rus '):
							trns = msg.replace('eng rus', '')
							self.write_msg(id, "Перевожу текст с английского на русский...")
							translator= Translator(from_lang="english",to_lang="russian")
							self.write_msg(id, translator.translate(trns))

						else:
							self.write_msg(id, "Команда не найдена.")

			except Exception as ex:
				connection.connect_timeout = 10000000000000
				print("error (start):", ex)


	def __del__(self):
		connection.close()


if __name__ == "__main__":
	bot = Bot()
	bot.start()
