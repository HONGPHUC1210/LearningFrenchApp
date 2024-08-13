import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

from PIL import Image, ImageTk, ImageEnhance
import os
import unicodedata
from dotenv import load_dotenv
import sys
import random
import json  # Về sau có thể xoá

# Thêm đường dẫn tới module notion_module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from notion_module import NotionManage  # Import từ module notion_module

class FrenchLearningApp:
    def __init__(self, root, notion_manager, database_id):
        self.root = root
        self.notion_manager = notion_manager
        self.database_id = database_id
        self.root.title("French Learning App")
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.geometry('+0+0')

        # Khởi tạo các biến cần thiết
        self.current_question_index = 0
        self.attempts = 0
        self.correct_answers_mode = False

        # Lấy và phân tích dữ liệu từ Notion
        self.questions = self.load_questions()

        # Tạo giao diện người dùng
        self.create_interface()




    def parse_notion_data(self, notion_data):
        parsed_data = []
        for item in notion_data:
            properties = item.get('properties', {})
            page_id = item.get('id', '')  # Lấy page_id từ item

            # Trích xuất 'French'
            french_property = properties.get('French', {}).get('title', [])
            french_word = french_property[0]['text']['content'] if french_property else ""

            # Trích xuất 'Vietnam'
            vietnamese_property = properties.get('Vietnam', {}).get('rich_text', [])
            vietnamese_word = vietnamese_property[0]['text']['content'] if vietnamese_property else ""

            # Trích xuất 'Tags'
            tags_property = properties.get('Tags', {}).get('select', {})
            tags = [tags_property['name']] if tags_property else []

            # Trích xuất 'Exemple'
            exemples_property = properties.get('Exemple', {}).get('rich_text', [])
            exemples = exemples_property[0]['text']['content'] if exemples_property else ""

            # Thêm dữ liệu đã trích xuất vào danh sách, bao gồm cả page_id
            parsed_data.append({
                'page_id': page_id,  # Đảm bảo rằng page_id được lưu trữ
                'French': french_word,
                'Vietnamese': vietnamese_word,
                'Tags': tags,
                'Exemple': exemples
            })

        return parsed_data


    def select_random_words(self, data, num_verbs, num_nouns, num_adjvs, num_phrases):
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

    def check_answer(self, event=None):
        # Lấy câu trả lời từ người dùng và chuẩn hóa
        user_answer = self.entry.get().strip().lower()

        # Chọn câu trả lời đúng dựa trên chỉ số câu hỏi ( 5 câu tiếng pháp và 5 câu tiếng Việt)
        if self.current_question_index < 5:
            correct_answer = self.questions[self.current_question_index]['Vietnamese'].strip().lower()
        else:
            correct_answer = self.questions[self.current_question_index]['French'].strip().lower()

        # Tích hợp logic remove_accents
        def remove_accents(input_str):
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            return ''.join([c for c in nfkd_form if not unicodedata.combining(c) or c == "'"])

        # Loại bỏ dấu khỏi câu trả lời của người dùng và câu trả lời đúng
        user_answer = remove_accents(user_answer)
        correct_answer = remove_accents(correct_answer)

        # Kiểm tra xem câu trả lời có đúng không
        if user_answer == correct_answer:
            # Nếu đúng, chuyển sang câu hỏi tiếp theo
            self.current_question_index += 1
            self.display_question()
        else:
            # Nếu sai, hiển thị thông báo lỗi
            self.attempts += 1
            if self.attempts >= 3:
                if self.current_question_index < 5:
                    correct_answer_message = self.questions[self.current_question_index]['Vietnamese']
                else:
                    correct_answer_message = self.questions[self.current_question_index]['French']
                messagebox.showinfo("Correct Answer", f"The correct answer is: {correct_answer_message}")
                self.entry.delete(0, tk.END)
                self.correct_answers_mode = True
            else:
                messagebox.showerror("Incorrect", "Incorrect. Try again. Please enter the correct answer.")
    
    def load_questions(self):
        # Lấy dữ liệu thô từ Notion
        raw_data = self.notion_manager.get_data(self.database_id)
        
        # Phân tích dữ liệu thô thành dữ liệu có cấu trúc
        parsed_data = self.parse_notion_data(raw_data)

        # Chọn từ ngẫu nhiên để tạo câu hỏi
        questions = self.select_random_words(parsed_data, 1,0,0,0)

        return questions
    
    def display_question(self):
        if self.current_question_index < len(self.questions):
            if self.current_question_index < 5:
                self.question_label.config(text=f"What does '{self.questions[self.current_question_index]['French']}' mean?")
            else:
                self.question_label.config(text=f"What does '{self.questions[self.current_question_index]['Vietnamese']}' mean?")
            self.entry.delete(0, tk.END)
            self.attempts = 0
            self.correct_answers_mode = False
        else:
            # Hiển thị thông báo sau khi hoàn thành tất cả các câu hỏi
            messagebox.showinfo("Done", "You have completed all questions!")
            # Đóng cửa sổ chính trước khi hỏi về Exemple
            self.root.destroy()


            # #  Tạo một cửa sổ mới cho phần hỏi Exemple
            # self.root = tk.Tk()
            # self.root.title("Fill in Examples")
            # self.root.geometry("400x200")


            # Hỏi người dùng có muốn điền Exemple không
            response = messagebox.askyesno("Thời gian rảnh", "Bạn có thời gian để điền các Exemple không?")
            if response:
                # Lọc ra các từ chưa có 'Exemple'
                words_with_empty_exemples = [q for q in self.questions if not q.get('Exemple')]

                if words_with_empty_exemples:
                    selected_words = random.sample(words_with_empty_exemples, min(5, len(words_with_empty_exemples)))

                    for word in selected_words:
                        exemple_text = simpledialog.askstring("Điền Exemple", f"Hãy điền Exemple cho từ '{word['French']}'")
                        if exemple_text:
                            # Gọi hàm update_page từ NotionManage để cập nhật 'Exemple' lên Notion
                            self.notion_manager.update_page(word['page_id'], {"Exemple": {"rich_text": [{"text": {"content": exemple_text}}]}})
                        else:
                            messagebox.showwarning("Cảnh báo", f"Bạn chưa điền Exemple cho từ '{word['French']}'")

                    messagebox.showinfo("Hoàn thành", "Các Exemple đã được cập nhật thành công!")
                else:
                    messagebox.showinfo("Thông báo", "Không có từ nào cần điền Exemple.")
            







    def create_interface(self):
    # Thiết lập các thành phần giao diện ban đầu (như hiện tại bạn đã làm)
        window_width = 400
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        canvas = tk.Canvas(self.root, width=window_width, height=window_height)
        canvas.pack(fill="both", expand=True)

        image_path = "E:/Code/Project_learning_french/App_notion/App_learning/flag.png"

        image = Image.open(image_path).convert("RGB")
        image = image.resize((window_width, window_height), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.5)
        self.background_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        font_large = ('Helvetica', 16, 'bold')
        font_medium = ('Helvetica', 12)

        frame_top = tk.Frame(self.root, bg='lightgray', bd=2, relief='sunken')
        frame_middle = tk.Frame(self.root, bg='lightgray', bd=2, relief='sunken')
        frame_bottom = tk.Frame(self.root, bg='lightgray', bd=2, relief='sunken')

        canvas.create_window(200, 70, window=frame_top, width=350, height=70)
        canvas.create_window(200, 160, window=frame_middle, width=350, height=70)
        canvas.create_window(200, 250, window=frame_bottom, width=350, height=70)

        self.question_label = tk.Label(frame_top, font=font_large, wraplength=350, justify="center")
        self.question_label.pack(expand=True)

        self.entry = tk.Entry(frame_middle, font=font_medium, justify="center")
        self.entry.pack(expand=True)
        self.entry.bind("<Return>", self.check_answer)

        self.submit_button = tk.Button(frame_bottom, text="Submit", command=self.check_answer, font=font_medium)
        self.submit_button.pack(expand=True)

        # Hiển thị câu hỏi đầu tiên
        self.display_question()



def save_notion_data_to_json(notion_data, output_file):
    # Chuyển đổi dữ liệu sang định dạng JSON và lưu vào file
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(notion_data, json_file, ensure_ascii=False, indent=4)
    
    print(f"Dữ liệu đã được lưu vào file {output_file}")






if __name__ == "__main__":
    # Tải biến môi trường từ file .env
    load_dotenv()

    # Lấy API key và Database ID từ biến môi trường
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    # Khởi tạo đối tượng NotionManage
    notion_manager = NotionManage(api_key)

    # Tạo cửa sổ Tkinter
    root = tk.Tk()

    # Khởi tạo đối tượng FrenchLearningApp với các tham số cần thiết
    app = FrenchLearningApp(root, notion_manager, database_id)

    # Chạy vòng lặp chính của Tkinter để hiển thị giao diện người dùng
    root.mainloop()

