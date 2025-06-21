from dataclasses import dataclass, asdict
from enum import Enum

class AnswerType(Enum):
    NONE = "NONE"
    NUMBER = "NUMBER"
    MCQ = "MCQ"

@dataclass
class Question:
    id: int
    question: str
    answer: str
    images: list[str]
    mcq_options: list[str]
    timer: int
    expected_answer_type: AnswerType = AnswerType.NONE

    def to_json(self):
        question_dict = asdict(self)
        question_dict['expected_answer_type'] = self.expected_answer_type.value
        return question_dict
