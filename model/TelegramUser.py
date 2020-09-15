from dataclasses import dataclass


@dataclass
class TelegramUser:
	username: str
	userid: int
	banned: int
