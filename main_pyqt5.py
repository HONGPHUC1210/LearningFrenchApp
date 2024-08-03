import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QFrame
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from notion_module import NotionManager
import random
import unicodedata

load_dotenv()

def select_random_words(data, num_verbs, num_nouns, num_adjvs, num_phrases):
    verbs = [item for item in data if 'Tags' in item and 'Verb' in item['Tags']]
    nouns = [item for item in data if 'Tags' in item and 'Nouns' in item['Tags']]
    adjvs = [item for item in data if 'Tags' in item and 'Adj/Adv' in item['Tags']]
    phrases = [item for item in data if 'Tags' in item and 'Cụm' in item['Tags']]

    selected_verbs = random.sample(verbs, min(num_verbs, len(verbs)))
    selected_nouns = random.sample(nouns, min(num_nouns, len(nouns)))
    selected_adjvs = random.sample(adjvs, min(num_adjvs, len(adjvs)))
    selected_phrases = random.sample(phrases, min(num_phrases, len(phrases)))

    selected_words = selected_verbs + selected_nouns + selected_adjvs + selected_phrases
    random.shuffle(selected_words)
    return selected_words

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

class FrenchLearningApp(QWidget):
    def __init__(self, questions):
        super().__init__()
        self.questions = questions
        self.current_question_index = 0
        self.attempts = 0
        self.correct_answers_mode = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle('French Learning App')
        self.setGeometry(100, 100, 500, 300)
        self.setWindowIcon(QIcon('path/to/icon.png'))  # Thay bằng đường dẫn tới biểu tượng của bạn

        main_layout = QVBoxLayout()

        # Frame cho câu hỏi
        question_frame = QFrame()
        question_layout = QVBoxLayout()

        self.question_label = QLabel('', self)
        self.question_label.setFont(QFont('Arial', 16))
        self.question_label.setAlignment(Qt.AlignCenter)
        question_layout.addWidget(self.question_label)

        question_frame.setLayout(question_layout)
        question_frame.setFrameShape(QFrame.StyledPanel)
        main_layout.addWidget(question_frame)

        # Frame cho câu trả lời
        answer_frame = QFrame()
        answer_layout = QHBoxLayout()

        self.entry = QLineEdit(self)
        self.entry.setFont(QFont('Arial', 14))
        self.entry.returnPressed.connect(self.check_answer)
        answer_layout.addWidget(self.entry)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setFont(QFont('Arial', 14))
        self.submit_button.clicked.connect(self.check_answer)
        answer_layout.addWidget(self.submit_button)

        answer_frame.setLayout(answer_layout)
        answer_frame.setFrameShape(QFrame.StyledPanel)
        main_layout.addWidget(answer_frame)

        # Tạo phong cách cho các thành phần
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 5px;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        self.setLayout(main_layout)

        if self.questions:
            self.display_question()
        else:
            QMessageBox.information(self, 'No Questions', 'No questions available.')
            self.close()

    def display_question(self):
        self.question_label.setText(f"What does '{self.questions[self.current_question_index]['French']}' mean?")
        self.entry.clear()
        self.attempts = 0
        self.correct_answers_mode = False

    def check_answer(self):
        user_answer = self.entry.text().strip().lower()
        correct_answer = self.questions[self.current_question_index]['Vietnamese'].strip().lower()

        user_answer = remove_accents(user_answer)
        correct_answer = remove_accents(correct_answer)

        if user_answer == correct_answer:
            if self.correct_answers_mode:
                self.correct_answers_mode = False
                self.current_question_index += 1
                if self.current_question_index < len(self.questions):
                    self.display_question()
                else:
                    QMessageBox.information(self, 'Correct', 'Correct answer! You can use your computer.')
                    self.close()
            else:
                self.current_question_index += 1
                if self.current_question_index < len(self.questions):
                    self.display_question()
                else:
                    QMessageBox.information(self, 'Correct', 'Correct answer! You can use your computer.')
                    self.close()
        else:
            self.attempts += 1
            if self.attempts >= 3:
                QMessageBox.information(self, 'Correct Answer', f"The correct answer is: {self.questions[self.current_question_index]['Vietnamese']}")
                self.entry.clear()
                self.correct_answers_mode = True
            else:
                QMessageBox.critical(self, 'Incorrect', 'Incorrect. Try again. Please enter the correct answer.')

if __name__ == '__main__':
    database_id = os.getenv("NOTION_DATABASE_ID")
    api_key = os.getenv("NOTION_API_KEY")

    notion_manager = NotionManager(database_id, api_key)
    data = notion_manager.get_notion_data()
    parsed_data = notion_manager.parse_notion_data(data)
    questions = select_random_words(parsed_data, 3, 2, 2, 2)

    app = QApplication(sys.argv)
    ex = FrenchLearningApp(questions)
    ex.show()
    sys.exit(app.exec_())
