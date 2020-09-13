from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Telegram(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Missing description
	"""

	@IntentHandler('MyIntentName')
	def dummyIntent(self, session: DialogSession, **_kwargs):
		pass
