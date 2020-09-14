import json
from datetime import datetime, timezone
from typing import List

import telepot
from paho.mqtt.client import MQTTMessage
from telepot.loop import MessageLoop

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.base.model.Intent import Intent
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession


class Telegram(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Chat with Alice directly from your mobile device with the `privacy first` app Telegram
	"""

	DATABASE = {
		'users': [
			'id integer PRIMARY KEY',
			'userId INTEGER NOT NULL',
			'userName TEXT NOT NULL',
			'userLastName TEXT',
			'accessLevel TEXT DEFAULT user',
			'blacklisted INTEGER DEFAULT 0'
		]
	}

	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)

	def __init__(self):

		self._INTENTS = [
			self._INTENT_ANSWER_YES_OR_NO
		]

		self._bot = None
		self._me = None
		self._loop = None
		self._chats: List = list()
		self._users = dict()

		self._INTENT_ANSWER_YES_OR_NO.dialogMapping = {
			'askingToAddNewTelegramUser': self.answerYesOrNo
		}

		super().__init__(self._INTENTS, self.DATABASE)


	def onStart(self):
		super().onStart()

		if not self.getConfig('token'):
			raise SkillStartingFailed(skillName=self._name, error='Please provide your bot token in the skill settings')

		self._bot = telepot.Bot(self.getConfig('token'))

		try:
			self._me = self._bot.getMe()
		except:
			raise SkillStartingFailed(skillName=self._name, error='Your token seems incorrect')

		self.loadUsers()
		self.logInfo(f'Loaded {len(self._users)} user', plural='user')


	def loadUsers(self):
		users = self.databaseFetch(tableName='users', query='SELECT * FROM :__table__', method='all')
		self._users = {user['userId']: user for user in users if users}


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


	def answerYesOrNo(self, session: DialogSession):
		if self.Commons.isYes(session):
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='okAdded')
			)
			self.databaseInsert(
				tableName='users',
				values={
					'userId': session.customData['userId'],
					'userName': session.customData['fromName'],
					'userLastName': session.customData['fromLastName'],
					'blacklisted': 0
				}
			)
			self.loadUsers()
			self.sendMessage(chatId=session.customData['userId'], message=self.randomTalk(text='whitelisted', replace=[session.customData['fromName']]))
		else:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='okNotAdded')
			)
			self.databaseInsert(
				tableName='users',
				values={
					'userId': session.customData['userId'],
					'userName': session.customData['fromName'],
					'userLastName': session.customData['fromLastName'],
					'blacklisted': 1
				}
			)
			self.loadUsers()
			self.sendMessage(chatId=session.customData['userId'], message=self.randomTalk(text='blacklisted', replace=[session.customData['fromName']]))


	def incomingMessage(self, message: dict):
		self.logDebug(f'Incoming message: {message}')

		chatId = message['chat']['id']
		fromName = message['from']['first_name']
		fromLastName = message['from']['last_name']
		date = message['date']

		# Drop too old messages in case Alice was offline
		timestamp = int(datetime.now(timezone.utc).timestamp())
		if date <= timestamp - 5:
			self.logInfo(f'Dropped old message from {fromName}: {message["text"]}')
			return

		# noinspection SqlResolve
		user = self.databaseFetch(tableName='users', query='SELECT * FROM :__table__ WHERE userId = :userId', values={'userId': chatId})
		if not user:
			self.logWarning(f'An unknown user texted me! His name and id: {fromName}/{chatId}')
			if not self.getAliceConfig('disableSoundAndMic'):
				self.ask(
					text=self.randomTalk(text='unknownUser', replace=[fromName]),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					currentDialogState='askingToAddNewTelegramUser',
					customData={
						'userId': chatId,
						'fromName': fromName,
						'fromLastName': fromLastName
					}
				)
			return

		if user['blacklisted'] == 1:
			self.logWarning(f'Blacklisted user texting: {fromName}/{chatId}')
			return

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
			self.sendMessage(session.siteId, session.payload['text'])


	def onEndSession(self, session: DialogSession, reason: str = 'nominal'):
		if session.siteId not in self._chats:
			return
		self._chats.remove(session.siteId)

		if reason != 'nominal':
			self.sendMessage(session.siteId, self.randomTalk(text='error', skill='system'))
		else:
			if session.payload.get('text', None):
				self.sendMessage(session.siteId, session.payload['text'])


	def sendMessage(self, chatId: str, message: str):
		self._bot.sendMessage(chat_id=chatId, text=message)
