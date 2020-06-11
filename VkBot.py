import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import threading
import time

#--------------------------------------------------------------------------------

mails = [(8, 25, "Начало первой пары через 5 минут!"), #первое число - часы, второе - минуты, строка - текст сообщения
		 (10, 15, "Начало второй пары через 5 минут!"),
		 (12, 5, "Начало третьей пары через 5 минут!"),
		 (21, 50, "ТЕСТ 19:55"),
		 (13, 55, "Начало четвертой пары через 5 минут!")]

#--------------------------------------------------------------------------------

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

def write_msg(user_id, message):
	vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': random.randint(0, 100000000)})

def check():
	while True:
		now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
		for i in mails:
			if now.hour == i[0] and now.minute == i[1]:
				for id in mailingIds:
					try:
						write_msg(id, i[2])
					except Exception as ex:
						print("error:", ex)
				time.sleep(100)
				break

def save():
	with open("users.txt", "w") as file:
		file.writelines([str(x) + "\n" for x in mailingIds])
		

token = "663f6be35f8b95159a155b8534c52b28c2a6a1b6252b3f526c4b03788f73e6d1cc66d65fa978eddbea104"

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

print("Бот запущен")

mailingIds = []
with open("users.txt", "r") as file:
	mailingIds = [int(x) for x in file.readlines()]

thread = threading.Thread(target=check)
thread.start()

while True:
	try:
		for event in longpoll.listen():
			if event.type == VkEventType.MESSAGE_NEW:
				if event.to_me:
					id = event.user_id
					if event.text.lower() == "подписаться":
						if id in mailingIds:
							write_msg(id, "Вы уже подписаны!")
						else:
							mailingIds.append(id)
							write_msg(id, "Вы успешно подписались на рассылку")
							save()

					elif event.text.lower() == "отписаться":
						if id in mailingIds:
							mailingIds.remove(id)
							write_msg(id, "Вы отписались от рассылки")
							save()
						else:
							write_msg(id, "Вы не подписывались")

					else:
						write_msg(id, "Привет! Чтобы получать уведомления о начале пары, нажми кнопку \"Подписаться\"")
	except Exception as ex:
		print("error:", ex)

