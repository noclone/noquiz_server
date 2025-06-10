import csv
import json

from data_types.question import Question, AnswerType

class QuestionsHandler:
    def __init__(self):
        self.questions = []
        self.current_question = 0

        with open('data/questions.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                self.questions.append(
                    Question(
                        id=len(self.questions),
                        question=row[0],
                        answer=row[1],
                        expected_answer_type=AnswerType(row[2]),
                        image=row[3] if len(row) > 3 else "",
                    )
                )

        with open('data/themes.json', 'r') as file:
            data = json.load(file)
            self.themes = {theme: [] for theme in data.keys()}
            for theme in self.themes:
                with open("data/" + data[theme], mode='r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    for row in reader:
                        self.themes[theme].append(
                            Question(
                                id=len(self.themes[theme]),
                                question=row[0],
                                answer=row[1],
                                image=row[2] if len(row) > 2 else "",
                            )
                        )

        with open('data/right_order.json', 'r') as file:
            data = json.load(file)
            self.right_order = data
            self.current_right_order = 0


    def get_next_question(self) -> Question | None:
        if self.current_question >= len(self.questions):
            return None
        question = self.questions[self.current_question]
        self.current_question += 1
        return question

    def get_themes(self):
        return list(self.themes.keys())

    def get_theme_questions(self, theme):
        return self.themes[theme]

    def get_next_right_order(self):
        if self.current_right_order >= len(self.right_order):
            return None
        right_order = self.right_order[self.current_right_order]
        self.current_right_order += 1
        return right_order