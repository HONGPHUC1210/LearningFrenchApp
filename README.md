# 🇫🇷 LearningFrenchApp

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Notion API](https://img.shields.io/badge/Notion-API-success) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> 🧠 A lightweight desktop app to practice your French vocabulary using the Notion API — automatically when you open your laptop!

---

## 🚀 Features
- Automatically launches when your computer starts.
- Quizzes you on vocab saved in your Notion workspace.
- Lightweight, simple, and highly customizable.

---

## 📥 Setup Instructions

### 1. Download the Project
- Click **[Code > Download ZIP]**, or clone the repository:

```bash
git clone https://github.com/yourusername/yourrepo.git 
```

Unzip (if needed) and navigate into the project directory.

### 2. Install Required Libraries
- Make sure you have Python 3.8+ installed.

- Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

⚡ Tip: It's best to use a virtual environment to keep dependencies clean.

### 3. Configure Notion API Connection
- Create an Integration on Notion.

- Share your Notion database with the integration.

- Update the App_learning/config.py file:

```bash
NOTION_TOKEN = 'your-integration-token'
DATABASE_ID = 'your-database-id'
```


### 4. Run the App
- You can now launch the app easily by double-clicking: ` run_app.bat `
---
## 🔧 (Optional) Additional Recommendations
- Auto-start on boot
- Copy the shortcut of run_app.bat into your Windows startup folder:

```bash
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```
- Convert to executable (.exe)
If you prefer, you can convert the app to a standalone executable:

```bash

pip install pyinstaller
pyinstaller --onefile App_learning/app_main.py
```
- Then use the generated .exe file inside the dist/ folder.
---
🖼️ Screenshots

Save vocabulary in Notion	App running



| Vocabulary saved in Notion | App running |
| :---------------------: | :---------: |
| ![image1](https://github.com/user-attachments/assets/146840cf-8b14-466f-848d-ee703fd48719) | ![image2](https://github.com/user-attachments/assets/f1039940-4cc4-461e-b535-994bd1b15024) |

