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

mails = [Mail(8, 40, "Начало первой пары через 5 минут!"), #Часы\Минуты\Текст
		 Mail(8, 45, "Первая пара началась!"),
		 Mail(10, 25, "Начало второй пары через 5 минут!"),
	 	 Mail(10, 30, "Вторая пара началась!"),
		 Mail(12, 10, "Начало третьей пары через 5 минут!"),
		 Mail(12, 15, "Третья пара началась!")]

token = "a0cd9c62cd844d73e9a841a1730746f11917476fd2e017f30882d3496e7b0c57596d4ddca0d8d80e8f820"

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
               "label":"Поток 2"
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
			print("Создание таблицы Users_Podslywka, если она не существует...")
			with connection.cursor() as cursor:
				cursor.execute("CREATE TABLE IF NOT EXISTS Users_Podslywka (user_id INT PRIMARY KEY);")
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
			
			today = datetime.datetime.today()
			print( today.strftime("Бот запушен. %d/%m/%Y") ) # '04/05/2017'
			

		except Exception as ex:
			print("error (__init__):", ex)


	def online(self): #Сообщество всегда онлайн
		try:
			while True:
				self.vk.method("groups.enableOnline", {"group_id": 194288350})
				time.sleep(120)
		except:
			pass


	def write_msg(self, user_id, message):
		try:
			self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': random.randint(0, 100000000)})
		except Exception as ex:
			print("error (write_msg, {0}, {1}):".format(user_id, message), ex)


	def check(self):
		while True:
			try:
				now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
				if now.isoweekday() not in [7]: # Если сегодня не суббота, воскресенье продолжай код...
					for mail in mails:
						if now.hour == mail.hours and now.minute == mail.minutes:
							if mail.send:
								mail.send = False
								with connection.cursor() as cursor:
									cursor.execute("SELECT user_id FROM Users_Podslywka")
									for row in cursor:
										self.write_msg(row["user_id"], mail.message)
						else:
							mail.send = True

			except Exception as ex:
				print("error (check):", ex)


	def antisleep(self): #Чтобы не уснула бесплатная БД 
		try:
			threading.Timer(200, self.antisleep).start()
			with connection.cursor() as cursor:
				cursor.execute("SELECT * FROM Users_Podslywka")
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
								cursor.execute("INSERT IGNORE INTO Users_Podslywka (user_id) VALUES (%s)", id)
								if cursor.rowcount == 0:
									self.write_msg(id, "Вы уже подписаны! ")
								else:
									self.write_msg(id, "Вы успешно подписались на рассылку четвертого потока.\nСоздатель бота: @xx69x69xx")
								connection.commit()


						elif msg == "отписаться":
							with connection.cursor() as cursor:
								cursor.execute("DELETE FROM Users_Podslywka WHERE user_id = %s", id)
								if cursor.rowcount != 0:
									self.write_msg(id, "Вы отписались от рассылки.")
								else:
									self.write_msg(id, "Вы не подписывались.")
								connection.commit()

							
						elif msg == "поток 2":
							self.write_msg(id, "Группа для второго потока: https://vk.com/scharagabot.\nСоздатель бота: @xx69x69xx")
							connection.commit()


						elif msg == "шнюкс" or "шнюс":
							self.write_msg(id, "Ожидайте, с вами свяжется Шнюк.")
							self.write_msg(289138746, "Покупатель хочет шнюкса! " + "vk.com/id" + str(id))
							connection.commit()


						elif msg.startswith('пост '):
							post = msg.replace('пост ', '')
							try:
								self.write_msg(id, "Ваш пост отправлен на обработку модераторам. Ожидайте...")
								self.write_msg(271693414, "Вам предложили новый пост " + "vk.com/id" + str(id) + " \nСодержание поста: " + post)
								self.write_msg(478012162, "Вам предложили новый пост " + "vk.com/id" + str(id) + " \nСодержание поста: " + post)
							except:
								pass
							
							connection.commit()

						else:
							self.write_msg(id, "Данной команды не существует.")
							

			except Exception as ex:
				connection.connect_timeout = 10000000000000
				print("error (start):", ex)


	def __del__(self):
		connection.close()


if __name__ == "__main__":
	bot = Bot()
	bot.start()
