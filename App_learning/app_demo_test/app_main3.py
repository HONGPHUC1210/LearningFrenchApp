
import tkinter as tk
from tkinter import Canvas, Frame, Label, Entry, Button, Tk
import time
from PIL import Image, ImageTk,ImageEnhance
from tkinter import messagebox
import asyncio
import os
from dotenv import load_dotenv
from notion_manage_app import NotionManage  # Import từ module notion_module
import json 
class LanguageLearningApp:
    def __init__(self, api_key, database_id):
        self.notion_manager = NotionManage(api_key)
        self.database_id = database_id
        self.words = asyncio.run(self.load_questions())
        self.current_word_index = 0
        self.submit_dict = {}
        self.attempts = 0
        self.in_example_mode = False  # Biến này để xác định chế độ nhập ví dụ
        self.root = tk.Tk()  # Use `tk.Tk()` instead of `CTk()`
        self.create_interface()

    async def load_questions(self):
        # Lấy dữ liệu thô từ Notion (bất đồng bộ)
        raw_data = await self.notion_manager.get_data_async(self.database_id)
        # Phân tích dữ liệu thô thành dữ liệu có cấu trúc
        parsed_data = await self.notion_manager.parse_notion_data(raw_data)
        # Chọn từ ngẫu nhiên để tạo câu hỏi
        questions = await self.notion_manager.select_random_words(parsed_data, 1, 1, 0, 0)
        return questions
    
    def create_interface(self):
        # Thiết lập các thành phần giao diện ban đầu
        window_width = 400
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Cải thiện giao diện với gradient nền
        canvas = Canvas(self.root, width=window_width, height=window_height)
        canvas.pack(fill="both", expand=True)
        gradient = canvas.create_rectangle(0, 0, window_width, window_height, outline="", fill="#888888")

        # Cải thiện hình ảnh nền
        image_path = "E:/Code/Project_Learning_French_App/App_learning/assets/flag.png"
        image = Image.open(image_path).convert("RGB")
        image = image.resize((window_width, window_height), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.4)
        self.background_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        # Thiết lập phông chữ
        font_large = ('Helvetica', 16, 'bold')
        font_medium = ('Helvetica', 12)

        # Sử dụng khung với viền bo tròn và đổ bóng
        frame_top = Frame(self.root, bg='#E8E8E8', bd=2, relief='raised', highlightthickness=1, highlightbackground='#888888')
        frame_middle = Frame(self.root, bg='#E8E8E8', bd=2, relief='raised', highlightthickness=1, highlightbackground='#888888')
        frame_bottom = Frame(self.root, bg='#E8E8E8', bd=2, relief='raised', highlightthickness=1, highlightbackground='#888888')

        canvas.create_window(200, 70, window=frame_top, width=350, height=70)
        canvas.create_window(200, 160, window=frame_middle, width=350, height=70)
        canvas.create_window(200, 250, window=frame_bottom, width=350, height=70)

        self.question_label = Label(frame_top, font=font_large, wraplength=350, justify="center", bg='white')
        self.question_label.pack(expand=True)

        self.answer_entry = Entry(frame_middle, font=font_medium, justify="center", relief='flat', highlightthickness=2, highlightbackground='#888888')
        self.answer_entry.pack(expand=True)
        self.answer_entry.bind("<Return>", lambda event: self.handle_submit())

        self.submit_button = Button(frame_bottom, text="Submit", command=self.handle_submit, font=font_medium, bg='#ffffff', fg='black')
        self.submit_button.pack(expand=True)

        # Hiển thị câu hỏi đầu tiên
        self.show_question()

        # Chạy ứng dụng
        self.root.mainloop()

    def handle_submit(self):
        # Dựa trên ngữ cảnh, gọi hàm phù hợp
        if self.in_example_mode:
            self.submit_example()
        else:
            self.submit_answer()
    def show_question(self):
        self.attempts = 0
        if self.current_word_index < len(self.words):
            word = self.words[self.current_word_index]
            if self.current_word_index % 2 == 0:
                self.question_label.configure(text=f"What does '{word['French']}' mean?")
            else:
                self.question_label.configure(text=f"What does '{word['Vietnamese']}' mean?")
        else:
            self.ask_for_examples()
    def submit_answer(self):
        word = self.words[self.current_word_index]
        correct_answer = word['Vietnamese'] if self.current_word_index % 2 == 0 else word['French']
        user_answer = self.answer_entry.get()

        # Kiểm tra nếu `Number` là rỗng thì hiểu là 0
        current_number = word.get("Number", 0) or 0

        # Trường hợp người dùng trả lời đúng ngay lần đầu tiên
        if self.attempts == 0 and user_answer.lower() == correct_answer.lower():
            word['Number'] = current_number + 1
            self.submit_dict[word['page_id']] = word
            self.current_word_index += 1
            self.answer_entry.delete(0, 'end')
            self.show_question()
        else:
            if user_answer.lower() == correct_answer.lower():
                # Không tăng `Number` nếu không đúng ngay lần đầu tiên
                self.submit_dict[word['page_id']] = word
                self.current_word_index += 1
                self.answer_entry.delete(0, 'end')
                self.show_question()
            else:
                self.attempts += 1
                if self.attempts >= 3:
                    messagebox.showinfo("Incorrect", f"The correct answer is '{correct_answer}'")
                else:
                    messagebox.showinfo("Incorrect", "Incorrect answer. Try again!")
    def ask_for_examples(self):
        result = messagebox.askyesno("Examples", "Would you like to provide examples for the words?")
        if result:
            self.in_example_mode = True  # Chuyển sang chế độ nhập ví dụ
            empty_example_words = [word for word in self.words if not word['Exemple']]
            if empty_example_words:
                self.current_word_index = 0
                self.words = empty_example_words
                self.show_example_question()
            else:
                # self.finish()
                asyncio.run(self.finish())
        else:
            # self.finish()
            asyncio.run(self.finish())
    def show_example_question(self):
        if self.current_word_index < len(self.words):
            word = self.words[self.current_word_index]
            self.question_label.configure(text=f"Provide an example for '{word['French']}'")
        else:
            # self.finish()
            asyncio.run(self.finish())
    def submit_example(self):
        word = self.words[self.current_word_index]
        user_example = self.answer_entry.get()

        if user_example:
            # Lưu ví dụ vào submit_dict ngay lập tức mà không kiểm tra đúng/sai
            word['Exemple'] = user_example
            self.submit_dict[word['page_id']] = word
            
            # Chuyển sang từ tiếp theo hoặc kết thúc nếu đã hoàn thành
            self.current_word_index += 1
            self.answer_entry.delete(0, 'end')
            if self.current_word_index < len(self.words):
                self.show_example_question()
            else:
                # self.finish()
                asyncio.run(self.finish())
        else:
            messagebox.showinfo("Empty input", "Please provide an example")

    async def finish(self):
        print("Completed. Submitting results to Notion...")

        tasks = []
        for page_id, word in self.submit_dict.items():
            properties = {
                "Number": {"number": word["Number"]},
                "Exemple": {"rich_text": [{"type": "text", "text": {"content": word["Exemple"]}}]}
            }
            # Tạo và thêm tác vụ bất đồng bộ vào danh sách
            tasks.append(self.notion_manager.update_page_async(page_id, properties))

        # Chờ tất cả các tác vụ hoàn thành
        await asyncio.gather(*tasks)
        print("Results submitted to Notion successfully.")
        self.root.destroy()

    # def finish(self):
    #     print("Completed. Writing results to output.json...")
    #     output_data = []

    #     for page_id, word in self.submit_dict.items():
    #         output_data.append({
    #             "page_id": page_id,
    #             "French": word["French"],
    #             "Vietnamese": word["Vietnamese"],
    #             "Tags": word["Tags"],
    #             "Exemple": word["Exemple"],
    #             "Number": word["Number"]
    #         })

    #     with open("output.json", "w", encoding="utf-8") as json_file:
    #         json.dump(output_data, json_file, ensure_ascii=False, indent=4)

    #     print("Results written to output.json successfully.")
    #     self.root.destroy()

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    LanguageLearningApp(api_key, database_id)
