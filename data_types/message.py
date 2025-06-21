import json
from dataclasses import dataclass
from enum import Enum


class Subject(Enum):
    PLAYER_INIT = "PLAYER_INIT"
    PLAYER_NAME = "PLAYER_NAME"
    GAME_STATE = "GAME_STATE"
    BUZZER = "BUZZER"
    PLAYER_ANSWER = "PLAYER_ANSWER"
    RIGHT_ORDER = "RIGHT_ORDER"
    TIMER = "TIMER"
    PLAYER_SCORE = "PLAYER_SCORE"
    QUESTION = "QUESTION"
    BOARD = "BOARD"
    THEMES = "THEMES"

@dataclass
class Message:
    subject: Subject
    action: str
    content: dict

    def to_json(self):
        return {
            "SUBJECT": self.subject.value,
            "ACTION": self.action,
            "CONTENT": self.content
        }

def create_message(data: dict):
    subject = Subject(data['SUBJECT'])
    action = data['ACTION']
    content = json.loads(data['CONTENT'])
    return Message(subject, action, content)
