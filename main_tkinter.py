import os
from dotenv import load_dotenv
from notion_module import NotionManager
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageEnhance

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
    import unicodedata
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def display_question():
    global question_label, entry, attempts, current_question_index, correct_answers_mode
    if current_question_index < len(questions):
        question_label.config(text=f"What does '{questions[current_question_index]['French']}' mean?")
        entry.delete(0, tk.END)
        attempts = 0
        correct_answers_mode = False
    else:
        messagebox.showinfo("Done", "You have completed all questions!")
        root.destroy()

def check_answer(event=None):
    global attempts, questions, current_question_index, correct_answers_mode

    user_answer = entry.get().strip().lower()
    correct_answer = questions[current_question_index]['Vietnamese'].strip().lower()

    user_answer = remove_accents(user_answer)
    correct_answer = remove_accents(correct_answer)

    if user_answer == correct_answer:
        if correct_answers_mode:
            correct_answers_mode = False
            current_question_index += 1
            if current_question_index < len(questions):
                display_question()
            else:
                messagebox.showinfo("Correct", "Correct answer! You can use your computer.")
                root.after(500, root.destroy)
        else:
            current_question_index += 1
            if current_question_index < len(questions):
                display_question()
            else:
                messagebox.showinfo("Correct", "Correct answer! You can use your computer.")
                root.after(500, root.destroy)
    else:
        attempts += 1
        if attempts >= 3:
            messagebox.showinfo("Correct Answer", f"The correct answer is: {questions[current_question_index]['Vietnamese']}")
            entry.delete(0, tk.END)
            correct_answers_mode = True
        else:
            messagebox.showerror("Incorrect", "Incorrect. Try again. Please enter the correct answer.")

def create_interface():
    global entry, question_label, root, submit_button, questions, current_question_index, attempts, correct_answers_mode

    root = tk.Tk()
    root.title("French Learning App")
    root.attributes('-topmost', True)
    root.focus_force()
    root.geometry('+0+0')

    window_width = 400
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)

    image_path = "E:/Code/Project_learning_french/App_notion/flag.png"
    image = Image.open(image_path).convert("RGB")
    image = image.resize((window_width, window_height), Image.LANCZOS)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.5)
    background_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=background_image, anchor="nw")

    font_large = ('Helvetica', 16, 'bold')
    font_medium = ('Helvetica', 12)

    frame_top = tk.Frame(root, bg='lightgray', bd=2, relief='sunken')
    frame_middle = tk.Frame(root, bg='lightgray', bd=2, relief='sunken')
    frame_bottom = tk.Frame(root, bg='lightgray', bd=2, relief='sunken')

    canvas.create_window(200, 70, window=frame_top, width=350, height=70)
    canvas.create_window(200, 160, window=frame_middle, width=350, height=70)
    canvas.create_window(200, 250, window=frame_bottom, width=350, height=70)

    question_label = tk.Label(frame_top, font=font_large, wraplength=350, justify="center")
    question_label.pack(expand=True)

    entry = tk.Entry(frame_middle, font=font_medium, justify="center")
    entry.pack(expand=True)
    entry.bind("<Return>", check_answer)

    submit_button = tk.Button(frame_bottom, text="Submit", command=check_answer, font=font_medium)
    submit_button.pack(expand=True)

    current_question_index = 0
    attempts = 0
    correct_answers_mode = False

    if questions:
        display_question()
    else:
        messagebox.showinfo("No Questions", "No questions available.")
        root.destroy()

    root.mainloop()

if __name__ == '__main__':
    database_id = os.getenv("NOTION_DATABASE_ID")
    api_key = os.getenv("NOTION_API_KEY")

    notion_manager = NotionManager(database_id, api_key)
    data = notion_manager.get_notion_data()
    parsed_data = notion_manager.parse_notion_data(data)
    questions = select_random_words(parsed_data, 3, 2, 2, 2)

    create_interface()
