
import tkinter as tk
from tkinter import Canvas, Frame, Label, Entry, Button, Tk
from PIL import Image, ImageTk,ImageEnhance
from tkinter import messagebox
import asyncio
import os
from dotenv import load_dotenv
from notion_manage_app import NotionManage  # Import từ module notion_module
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
        self.root.title("Language Learning App")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_interface()

    async def load_questions(self):
        # Lấy dữ liệu thô từ Notion (bất đồng bộ)
        raw_data = await self.notion_manager.get_data_async(self.database_id)
        # Phân tích dữ liệu thô thành dữ liệu có cấu trúc
        parsed_data = await self.notion_manager.parse_notion_data(raw_data)
        # Chọn từ ngẫu nhiên để tạo câu hỏi
        questions = await self.notion_manager.select_random_words(parsed_data, 3, 3, 3, 1)
        return questions
    
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

        # Tạo canvas và hình nền
        canvas = Canvas(self.root, width=window_width, height=window_height, bd=0, relief='ridge')
        canvas.pack(fill="both", expand=True)

        image_bg_path = "E:/Code/Project_Learning_French_App/App_learning/assets/bg.png"
        image_bg = Image.open(image_bg_path).convert("RGB")
        image_bg = image_bg.resize((window_width, window_height), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(image_bg)
        image_bg = enhancer.enhance(1)
        self.background_image = ImageTk.PhotoImage(image_bg)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        #Cài đặt font chữ và các màu
        self.placeholder_color = '#868383'  # Màu xám nhạt để làm mờ placeholder
        self.normal_text_color = '#000716'  # Màu văn bản thông thường
        self.bg_color = "#B7BFD0"
        self.fg_color = "#000716"
        font_large = ('Helvetica', 18, 'bold')
        font_medium = ('Helvetica', 14)

        # Thêm Label để hiển thị câu hỏi
        self.question_label = Label(
            self.root,
            font=font_large,
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.question_label.place(
            x=82.0,
            y=133.0,
            width=446.0,
            height=50.0
        )
        self.placeholder_text = 'Entry here....'
        # Thêm Entry để người dùng nhập câu trả lời
        self.answer_entry = Entry(
            self.root,
            bd=0,
            font=font_medium,
            bg=self.bg_color,
            fg= self.placeholder_color,
            justify="center"
        )
        self.answer_entry.insert(0, self.placeholder_text)  # Thiết lập placeholder ban đầu
        self.answer_entry.place(
            x=82.0,
            y=228,
            width=446.0,
            height=50
        )
        self.answer_entry.bind("<Return>", lambda event: self.handle_submit())

        # Thêm Button để gửi câu trả lời
        submit_button = Button(
            self.root,
            text="Submit",
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            font=font_medium,
            bg=self.bg_color,
            fg=self.fg_color,
            command=self.handle_submit
        )
        submit_button.place(
            x=248,
            y=316,
            width=102,
            height=32.5
        )
        # Ràng buộc sự kiện focus để xóa placeholder khi nhấp vào Entry
        self.answer_entry.bind("<FocusIn>", self.clear_placeholder)
        # Ràng buộc sự kiện focus ra ngoài để khôi phục placeholder nếu trống
        self.answer_entry.bind("<FocusOut>", self.add_placeholder)
        # Hiển thị câu hỏi đầu tiên
        self.show_question()
        self.root.mainloop()

    def on_closing(self):
            # Hiển thị hộp thoại xác nhận khi đóng cửa sổ
            if messagebox.askokcancel("Quit", "Bạn có muốn dừng lại không?"):
                asyncio.run(self.finish())  # Cập nhật dữ liệu trước khi đóng
                # self.root.destroy()
    def clear_placeholder(self, event):
        if self.answer_entry.get() == self.placeholder_text:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.config(fg=self.normal_text_color)  # Đặt lại màu văn bản thông thường

    def add_placeholder(self, event):
        if self.answer_entry.get() == '':
            self.answer_entry.insert(0, self.placeholder_text)
            self.answer_entry.config(fg=self.placeholder_color)  # Đặt lại màu mờ cho placeholder

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
