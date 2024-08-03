@echo off
set /p option="Enter your choice (1 - Clean Data, 2 - Update Grouping Column, 3 - Sort Data): "

python "E:\Code\Project_learning_french\App_notion\main_clean.py" %option%

pause
