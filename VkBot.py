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

token = "c76dcb2f3b509f0e124a69d1425667dadba28228cf668ff4c98740b00f2dc24eaa5dd805764b496d1e181"

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
               "type":"text",
               "label":"Запись"
            },
            "color": "negative"
         },
		 {
            "action": {
               "type":"text",
               "label":"Рассылка"
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


	def start(self):
		while True:
			try:
				for event in self.longpoll.listen():
					if event.type == VkEventType.MESSAGE_NEW and event.to_me:
						id = event.user_id
						msg = event.text.lower()
						if msg == "запись":
							self.write_msg(id, "📰Чтобы опубликовать свой пост на стене введите: \" Пост <тут ваш пост> \". ")


						elif msg == "команды":
							self.write_msg(id, "⚙Список команд:")
							self.write_msg(id, "🕐Чтобы получать уведомления о начале пары введите: \"потоки\". ")
							self.write_msg(id, "📰Чтобы опубликовать свой пост на стене введите: \n \"Пост <тут ваш пост> \". ")


						elif msg == "рассылка":
							self.write_msg(id, "Чтобы получать уведомления о начале пары введите, напишите в личку данному сообществу https://vk.com/shg_bot")


						elif msg.startswith('пост '):
							post = msg.replace('пост ', '')
							try:
								self.write_msg(id, "Ваш пост отправлен на обработку модераторам. Ожидайте...")
								self.write_msg(271693414, "Вам предложили новый пост " + "vk.com/id" + str(id) + " \nСодержание поста: " + post)
								self.write_msg(478012162, "Вам предложили новый пост " + "vk.com/id" + str(id) + " \nСодержание поста: " + post)
							except:
								pass
							
						else:
							pass

			except Exception as ex:
				print("error (start):", ex)


	def __del__(self):
		connection.close()


if __name__ == "__main__":
	bot = Bot()
	bot.start()
