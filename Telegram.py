import json
from typing import Dict, List, Optional

import telepot
from paho.mqtt.client import MQTTMessage
from telepot.loop import MessageLoop

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession


class Telegram(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Chat with Alice directly from your mobile device with the `privacy first` app Telegram
	"""


	def __init__(self):
		super().__init__()
		self._bot: Optional[telepot.Bot] = None
		self._me: Optional[Dict] = None
		self._loop: Optional[MessageLoop] = None
		self._chats: List = list()


	def onStart(self):
		if not self.getConfig('token'):
			raise SkillStartingFailed(skillName=self._name, error='Please provide your bot token in the skill settings')

		self._bot = telepot.Bot(self.getConfig('token'))
		self._bot.deleteWebhook()

		try:
			self._me = self._bot.getMe()
		except:
			raise SkillStartingFailed(skillName=self._name, error='Your token seems incorrect')


	def onBooted(self) -> bool:
		if not self._bot:
			return False

		self._loop = MessageLoop(self._bot, self.incomingMessage).run_as_thread()

		return super().onBooted()


	def onStop(self):
		super().onStop()
		if not self._bot:
			return

		try:
			# noinspection PyProtectedMember
			self._bot._scheduler.join(timeout=1)
		except:
			pass  # The bot's thread needs to be stopped if the skill is reloaded, not when Alice goes down


	def incomingMessage(self, message: dict):
		self.logDebug(f'Incoming message: {message}')

		chatId = message['chat']['id']
		fromName = message['from']['first_name']
		siteId = str(chatId)
		self._chats.append(siteId)

		session = self.DialogManager.newSession(siteId=siteId, user=fromName)
		session.textOnly = True

		mqttMessage = MQTTMessage()
		mqttMessage.payload = json.dumps({'sessionId': session.sessionId, 'siteId': siteId, 'text': message['text']})
		session.extend(message=mqttMessage)

		self.MqttManager.publish(topic=constants.TOPIC_NLU_QUERY, payload={
			'input'    : message['text'],
			'sessionId': session.sessionId
		})


	def onContinueSession(self, session: DialogSession):
		if session.siteId not in self._chats:
			return

		if session.payload.get('text', None):
			self._bot.sendMessage(chat_id=session.siteId, text=session.payload['text'])


	def onEndSession(self, session: DialogSession, reason: str = 'nominal'):
		if session.siteId not in self._chats:
			return
		self._chats.remove(session.siteId)

		if reason != 'nominal':
			self._bot.sendMessage(chat_id=session.siteId, text='Error, sorry....')
		else:
			if session.payload.get('text', None):
				self._bot.sendMessage(chat_id=session.siteId, text=session.payload['text'])
