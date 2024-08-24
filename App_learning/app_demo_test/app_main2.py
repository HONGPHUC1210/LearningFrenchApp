import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, Label

from PIL import Image, ImageTk, ImageEnhance
import os
import unicodedata
from dotenv import load_dotenv
import sys
import random
import asyncio
from pathlib import Path

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
        self.correctly_answered_words = []  # Lưu các từ đã trả lời đúng

        # Lấy và phân tích dữ liệu từ Notion (bất đồng bộ)
        self.questions = asyncio.run(self.load_questions())

        # Tạo giao diện người dùng
        self.create_interface()

    async def parse_notion_data(self, notion_data):
        parsed_data = []
        for item in notion_data:
            properties = item.get('properties', {})
            page_id = item.get('id', '')

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

            # Trích xuất 'Number'
            number_property = properties.get('Number', {}).get('number', 0) or 0

            # Thêm dữ liệu đã trích xuất vào danh sách, bao gồm cả page_id
            parsed_data.append({
                'page_id': page_id,
                'French': french_word,
                'Vietnamese': vietnamese_word,
                'Tags': tags,
                'Exemple': exemples,
                'Number': number_property
            })

        return parsed_data

    async def select_random_words(self, data, num_verbs, num_nouns, num_adjvs, num_phrases):
        # Sắp xếp dữ liệu theo `Number` từ thấp đến cao
        data_sorted_by_number = sorted(data, key=lambda x: x['Number'])

        # Lọc các từ theo tag và ưu tiên `Number` thấp
        verbs = [item for item in data_sorted_by_number if 'Tags' in item and 'Verb' in item['Tags']]
        nouns = [item for item in data_sorted_by_number if 'Tags' in item and 'Nouns' in item['Tags']]
        adjvs = [item for item in data_sorted_by_number if 'Tags' in item and 'Adj/Adv' in item['Tags']]
        phrases = [item for item in data_sorted_by_number if 'Tags' in item and 'Cụm' in item['Tags']]

        # Chọn những từ có `Number` thấp nhất
        def select_min_number_words(word_list, num_words):
            min_number = word_list[0]['Number']
            min_number_words = [word for word in word_list if word['Number'] == min_number]
            return random.sample(min_number_words, min(num_words, len(min_number_words)))

        # Chọn ngẫu nhiên các từ từ những từ có `Number` thấp nhất
        selected_verbs = select_min_number_words(verbs, num_verbs)
        selected_nouns = select_min_number_words(nouns, num_nouns)
        selected_adjvs = select_min_number_words(adjvs, num_adjvs)
        selected_phrases = select_min_number_words(phrases, num_phrases)

        selected_words = selected_verbs + selected_nouns + selected_adjvs + selected_phrases
        random.shuffle(selected_words)
        return selected_words

    async def load_questions(self):
        # Lấy dữ liệu thô từ Notion (bất đồng bộ)
        raw_data = await self.notion_manager.get_data_async(self.database_id)
        
        # Phân tích dữ liệu thô thành dữ liệu có cấu trúc
        parsed_data = await self.parse_notion_data(raw_data)

        # Chọn từ ngẫu nhiên để tạo câu hỏi
        questions = await self.select_random_words(parsed_data, 5, 5, 5, 1)

        return questions

    def check_answer(self, event=None):
        user_answer = self.answer_entry.get().strip()
        
        half_questions = (len(self.questions) + 1) // 2

        def remove_accents(input_str):
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            without_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
            without_accents = without_accents.replace("'", "1").replace("‘", "1").replace("’", "1").replace("`", "1")
            without_accents = ''.join(e for e in without_accents if e.isalnum())
            return without_accents.lower()

        # Lấy từ đúng từ dict trong danh sách câu hỏi
        current_word = self.questions[self.current_question_index]

        # Xác định giá trị `Number` bé nhất trong danh sách từ được chọn
        min_number = min(word['Number'] for word in self.questions)

        # Xác định xem hiện tại đang hỏi từ tiếng Pháp hay từ tiếng Việt
        if self.current_question_index < half_questions:
            correct_answer = current_word['Vietnamese'].strip()
        else:
            correct_answer = current_word['French'].strip()

        # Chuẩn hóa cả user_answer và correct_answer
        user_answer = remove_accents(user_answer)
        correct_answer = remove_accents(correct_answer)

        # Kiểm tra câu trả lời
        if user_answer == correct_answer:
            # Chỉ tăng `Number` nếu nó không lớn hơn `min_number + 2`
            if self.attempts == 0 and current_word['Number'] <= min_number + 2:
                current_word['Number'] += 1
                self.correctly_answered_words.append(current_word)
            self.current_question_index += 1
            self.display_question()
        else:
            self.attempts += 1
            if self.attempts == 1 and current_word['Number'] > 0:
                current_word['Number'] -= 1

            if self.attempts >= 3:
                correct_answer_message = current_word['Vietnamese'] if self.current_question_index < half_questions else current_word['French']
                messagebox.showinfo("Correct Answer", f"The correct answer is: {correct_answer_message}")
                self.answer_entry.delete(0, tk.END)
                self.correct_answers_mode = True
            else:
                messagebox.showerror("Incorrect", "Incorrect. Try again. Please enter the correct answer.")

    def display_question(self):
        half_questions = (len(self.questions) + 1) // 2  # Nếu lẻ, phần tiếng Pháp sẽ nhiều hơn

        if self.current_question_index < len(self.questions):
            current_word = self.questions[self.current_question_index]

            if self.current_question_index < half_questions:
                # Hiển thị câu hỏi tiếng Pháp, yêu cầu người dùng trả lời nghĩa tiếng Việt
                self.question_label.config(text=f"What does '{current_word['French']}' mean?")
            else:
                # Hiển thị câu hỏi tiếng Việt, yêu cầu người dùng trả lời nghĩa tiếng Pháp
                self.question_label.config(text=f"What does '{current_word['Vietnamese']}' mean?")
            
            self.answer_entry.delete(0, tk.END)
            self.attempts = 0
            self.correct_answers_mode = False
        else:
            # Cập nhật các từ đã trả lời đúng vào Notion (bất đồng bộ)
            asyncio.run(self.update_correct_answers())
            
            # Hiển thị thông báo sau khi hoàn thành tất cả các câu hỏi
            messagebox.showinfo("Done", "You have completed all questions!")
            # Đóng cửa sổ chính trước khi hỏi về Exemple
            self.root.destroy()

            # Hỏi người dùng có muốn điền Exemple không
            response = messagebox.askyesno("Thời gian rảnh", "Bạn có thời gian để điền các Exemple không?")
            if response:
                asyncio.run(self.update_exemple())

    async def update_correct_answers(self):
        """Cập nhật các từ đã trả lời đúng lên Notion (bất đồng bộ)."""
        tasks = []
        for word in self.correctly_answered_words:
            task = self.notion_manager.update_page_async(word['page_id'], {"Number": {"number": word['Number']}})
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def update_exemple(self):
        """Hàm này xử lý việc thêm ví dụ (Exemple) cho các từ (bất đồng bộ)."""
        words_with_empty_exemples = [q for q in self.questions if not q.get('Exemple')]

        if words_with_empty_exemples:
            selected_words = random.sample(words_with_empty_exemples, min(5, len(words_with_empty_exemples)))
            
            for word in selected_words:
                exemple_text = simpledialog.askstring("Điền Exemple", f"Hãy điền Exemple cho từ '{word['French']}'")
                if exemple_text:
                    await self.notion_manager.update_page_async(word['page_id'], {"Exemple": {"rich_text": [{"text": {"content": exemple_text}}]}})
                else:
                    cancel = messagebox.askyesno("Hủy", "Bạn muốn hủy việc điền Exemple cho các từ còn lại không?")
                    if cancel:
                        break  # Thoát khỏi vòng lặp nếu người dùng chọn hủy
                    else:
                        messagebox.showwarning("Cảnh báo", f"Bạn chưa điền Exemple cho từ '{word['French']}'")

            messagebox.showinfo("Hoàn thành", "Các Exemple đã được cập nhật thành công!")
        else:
            messagebox.showinfo("Thông báo", "Không có từ nào cần điền Exemple.")

    def create_interface(self):
        # Thiết lập các thành phần giao diện ban đầu
        window_width = 608
        window_height = 416
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
        self.root.iconbitmap("E:/Code/Project_Learning_French_App/App_learning/assets/flag.ico")
        canvas = tk.Canvas(self.root, width=window_width, height=window_height,bd=0,relief='ridge')
        canvas.pack(fill="both", expand=True)

        image_path = "E:/Code/Project_Learning_French_App/App_learning/flag.png"
        image1_path = "E:/Code/Project_Learning_French_App/App_learning/assets/image_1.png"
        image2_path = "E:/Code/Project_Learning_French_App/App_learning/assets/image_2.png"
        image3_path = "E:/Code/Project_Learning_French_App/App_learning/assets/image_3.png"
        image_bg_path = "E:/Code/Project_Learning_French_App/App_learning/assets/bg.png"
        


        image_bg = Image.open(image_bg_path).convert("RGB")
        image_bg = image_bg.resize((window_width, window_height), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(image_bg)
        image_bg = enhancer.enhance(1)
        self.background_image = ImageTk.PhotoImage(image_bg)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")



        font_large = ('Helvetica', 16, 'bold')
        font_medium = ('Helvetica', 12)

        # image2 = Image.open(image2_path).convert("RGB")
        # # image2 = image2.resize((window_width, window_height), Image.LANCZOS)
        # enhancer2 = ImageEnhance.Brightness(image2)
        # image2 = enhancer2.enhance(0.7)
        # self.entry_bg = ImageTk.PhotoImage(image2)
        # canvas.create_image(38,120, image=self.entry_bg, anchor="nw")

        # Thêm Label để hiển thị câu hỏi
        self.question_label = Label(
            root,
            # text="What does '...' mean?",  # Đây là nơi hiển thị câu hỏi
            font=font_large,
            bg="#B7BFD0",
            # bg="#FFFFFF",

            fg="#000716"
        )
        self.question_label.place(
            x=82.0,
            y=133.0,
            width=446.0,
            height=50.0
        )

        # Thêm Entry để người dùng nhập câu trả lời
        self.answer_entry = Entry(
            root,
            bd=0,
            font= font_medium,
            bg="#B7BFD0",
            # bg="#FFFFFF",

            fg="#000716",
            highlightthickness=0,
            justify="center"
        )
        self.answer_entry.insert(0, 'Entry here....')  # Thiết lập placeholder ban đầu
        self.answer_entry.place(
            x=82.0,
            y=228,
            width=446.0,
            height=50
        )
        self.answer_entry.bind("<Return>", self.check_answer)

        # self.submit_button = tk.Button(frame_bottom, text="Submit", command=self.check_answer, )
        # self.submit_button.pack(expand=True)





        
        # Thêm Button để gửi câu trả lời
        submit_button = Button(
            root,
            text="Submit",
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            font=font_medium,
            bg="#B7BFD0",
            # bg="#FFFFFF",
            command=self.check_answer  # Thay bằng chức năng kiểm tra câu trả lời
        )
        submit_button.place(
            x=248,
            y=316,
            # width=113.0,
            # height=33.0
            width=102,
            height= 32.5
        )
        # Hiển thị câu hỏi đầu tiên
        self.display_question()



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
