import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import threading
import time
import pymysql
from pymysql.cursors import DictCursor
from bs4 import BeautifulSoup
import requests


class Mail:
	def __init__(self, hours: int, minutes: int, message: str):
		self.hours = hours
		self.minutes = minutes
		self.message = message
		self.send = True

#--------------------------------------------------------------------------------

mails = [Mail(8, 25, "Начало первой пары через 5 минут!"), #первое число - часы, второе - минуты, строка - текст сообщения
		 Mail(8, 30, "Первая пара началась!"),
		 Mail(13, 55, "Тестовое оповещение"),
		 Mail(10, 15, "Начало второй пары через 5 минут!"),
	 	 Mail(10, 20, "Вторая пара началась!"),
		 Mail(12, 5, "Начало третьей пары через 5 минут!"),
		 Mail(12, 10, "Третья пара началась!"),
	 	 Mail(12, 10, "Начало четвертой пары через 5 минут!"),
		 Mail(14, 0, "Четвертая пара началась!")]

token = "663f6be35f8b95159a155b8534c52b28c2a6a1b6252b3f526c4b03788f73e6d1cc66d65fa978eddbea104"

connection = pymysql.connect(host='sql7.freesqldatabase.com',
						  	 user='sql7347793',
						  	 password='IghqNH1JGK',
						  	 db='sql7347793',
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
			print("Запускаю \"антисон\"...")
			self.antisleep()
			print("Запустил!")
			print("Бот запущен")

		except Exception as ex:
			print("error (__init__):", ex)


	def write_msg(self, user_id, message):
		try:
			self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': random.randint(0, 100000000)})
		except Exception as ex:
			print("error (write_msg, {0}, {1}):".format(user_id, message), ex)


	def check(self):
		while True:
			try:
				now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
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
	
	
	def antisleep(self):
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
					if event.type == VkEventType.MESSAGE_NEW:
						if event.to_me:
							id = event.user_id
							if event.text.lower() == "подписаться":
								with connection.cursor() as cursor:
									cursor.execute("INSERT IGNORE INTO Users (user_id) VALUES (%s)", id)
									if cursor.rowcount == 0:
										self.write_msg(id, "Вы уже подписаны!")
									else:
										self.write_msg(id, "Вы успешно подписались на рассылку")
									connection.commit()

							elif event.text.lower() == "отписаться":
								with connection.cursor() as cursor:
									cursor.execute("DELETE FROM Users WHERE user_id = %s", id)
									if cursor.rowcount != 0:
										self.write_msg(id, "Вы отписались от рассылки")
									else:
										self.write_msg(id, "Вы не подписывались")
									connection.commit()
							elif msg.startswith('вики, '):
								response = requests.get('https://ru.wikipedia.org/wiki/' + msg.replace('Вики, ', ''))
								soup = BeautifulSoup(response.text, 'html.parser')
								tag = soup.find('div', {'class': 'mw-parser-output'})
								self.write_msg(id, '\n'.join([e.text.replace('[править | править код]', '') for e in tag.children if e.name in ('p', 'h2')][:20]))


							else:
								self.write_msg(id, "Привет! Чтобы подписаться на рассылку, нажми кнопку \"Подписаться\"")

			except Exception as ex:
				print("error (start):", ex)


	def __del__(self):
		connection.close()


if __name__ == "__main__":
	bot = Bot()
	bot.start()

