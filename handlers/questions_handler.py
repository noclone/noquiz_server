import csv
import json

from data_types.question import Question, AnswerType

selected_quiz = "quiz1"

class QuestionsHandler:
    def __init__(self):
        self.questions_categories = []

        with open(f'data/{selected_quiz}/questions/questions.json', mode='r') as file:
            data = json.load(file)
            self.questions_categories = {category: [] for category in data.keys()}
            for category in self.questions_categories:
                with open(f'data/{selected_quiz}/questions/' + data[category], mode='r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    for row in reader:
                        self.questions_categories[category].append(
                            Question(
                                id=len(self.questions_categories[category]),
                                question=row[0],
                                answer=row[1],
                                expected_answer_type=AnswerType(row[2]),
                                images=[image for image in row[3:]] if len(row) > 3 else [],
                            )
                        )

        with open(f'data/{selected_quiz}/themes/themes.json', 'r') as file:
            data = json.load(file)
            self.themes = {theme: [] for theme in data.keys()}
            for theme in self.themes:
                with open(f'data/{selected_quiz}/themes/' + data[theme], mode='r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    for row in reader:
                        self.themes[theme].append(
                            Question(
                                id=len(self.themes[theme]),
                                question=row[0],
                                answer=row[1],
                                images=[image for image in row[2:]] if len(row) > 2 else [],
                            )
                        )

        with open(f'data/{selected_quiz}/right_order.json', mode='r', encoding='utf-8') as file:
            data = json.load(file)
            self.right_order = data

        with open(f'data/{selected_quiz}/board.json', mode='r', encoding='utf-8') as file:
            board = json.load(file)
            self.board = []
            for question in board:
                board_element = Question(
                    id=len(self.board),
                    question=question['question'],
                    answer=question['answer'],
                    expected_answer_type=AnswerType.NONE,
                    images=question['images'],
                ).to_json()
                board_element['difficulty'] = question['difficulty']
                board_element['thumbnail'] = question['thumbnail']
                self.board.append(board_element)

    def get_board(self):
        return self.board

    def get_questions_categories(self):
        return list(self.questions_categories.keys())

    def get_category_questions(self, category):
        return self.questions_categories[category]

    def get_themes(self):
        return list(self.themes.keys())

    def get_theme_questions(self, theme):
        return self.themes[theme]

    def get_right_order(self):
        return self.right_order