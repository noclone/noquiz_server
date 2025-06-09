import csv
from data_types.question import Question, AnswerType

class QuestionsHandler:
    def __init__(self):
        self.questions = []
        self.current_question = 0

        with open('data/questions.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                self.questions.append(Question(len(self.questions), row[0], row[1], AnswerType(row[2])))

    def get_question(self, question_id: int) -> Question:
        return self.questions[question_id]

    def get_next_question(self) -> Question | None:
        if self.current_question >= len(self.questions):
            return None
        question = self.questions[self.current_question]
        self.current_question += 1
        return question

    def get_all_questions(self) -> list[Question]:
        return self.questions
