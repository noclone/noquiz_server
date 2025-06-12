import csv
import json

from data_types.question import Question, AnswerType

class QuestionsHandler:
    def __init__(self):
        self.questions_categories = []

        with open('data/questions/questions.json', mode='r') as file:
            data = json.load(file)
            self.questions_categories = {category: [] for category in data.keys()}
            for category in self.questions_categories:
                with open("data/questions/" + data[category], mode='r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    for row in reader:
                        self.questions_categories[category].append(
                            Question(
                                id=len(self.questions_categories[category]),
                                question=row[0],
                                answer=row[1],
                                expected_answer_type=AnswerType(row[2]),
                                image=row[3] if len(row) > 3 else "",
                            )
                        )

        with open('data/themes/themes.json', 'r') as file:
            data = json.load(file)
            self.themes = {theme: [] for theme in data.keys()}
            for theme in self.themes:
                with open("data/themes/" + data[theme], mode='r', encoding='utf-8') as csvfile:
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

    def get_questions_categories(self):
        return list(self.questions_categories.keys())

    def get_category_questions(self, category):
        return self.questions_categories[category]

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