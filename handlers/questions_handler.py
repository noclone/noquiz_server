import json

from data_types.question import Question, AnswerType

selected_quiz = "quiz2"


def get_question_from_data(data: dict, question_id: int):
    return Question(
        id=question_id,
        question=data["question"] if "question" in data else "",
        answer=data["answer"],
        expected_answer_type=AnswerType(data["expected_answer_type"]),
        images=data["images"] if "images" in data else [],
        mcq_options=data["mcq_options"] + [data["answer"]] if "mcq_options" in data else [],
    )

def get_questions_from_json(category: str):
    with open(f'data/{selected_quiz}/{category}/{category}.json', mode='r') as file:
        data = json.load(file)
        res = {subject: [] for subject in data.keys()}
        for subject in res:
            with open(f'data/{selected_quiz}/{category}/' + data[subject], mode='r', encoding='utf-8') as data_file:
                content = json.load(data_file)
                for elem in content:
                    res[subject].append(
                        get_question_from_data(elem, len(res[subject]))
                    )
    return res

class QuestionsHandler:
    def __init__(self):
        self.questions_categories = get_questions_from_json("questions")
        self.themes = get_questions_from_json("themes")

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
                    mcq_options=[]
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
