from notion_manage_app import NotionManage  # Import from your module
import json
import os
import asyncio
from dotenv import load_dotenv

def save_data_to_json(data, file_path="out_put.json"):
    """Save parsed Notion data to a JSON file."""
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    return file_path

def find_empty_tags(data):
    """Hàm kiểm tra những từ nào có 'Tags' rỗng."""
    empty_tag_items = [item for item in data if not item.get('Tags')]
    return empty_tag_items
import re

def normalize_answer(answer):
    # Chuyển thành chữ thường
    answer = answer.lower()
    # Chuyển dấu nháy cong ‘ ’ thành dấu nháy thẳng '
    answer = re.sub(r"[‘’]", "'", answer)
    # Xoá khoảng trắng ở đầu và cuối
    answer = answer.strip()
    return answer

async def main():
    load_dotenv()
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    test = NotionManage(api_key)
    
    # Await the asynchronous method to get raw data
    raw_data = await test.get_data_async(database_id)
    
    # Parse the data
    data = await test.parse_notion_data(raw_data)
    select_word = await test.select_random_words(data,5,5,5,5) 
    # Save the parsed data to a JSON file
    save_data_to_json(select_word)

    # Tìm các từ có 'Tags' rỗng
    items_with_empty_tags = find_empty_tags(data)
    
    # In kết quả nếu có từ với 'Tags' rỗng
    if items_with_empty_tags:
        print("Các từ có 'Tags' rỗng:")
        for item in items_with_empty_tags:
            print(f"French: {item['French']}, Vietnamese: {item['Vietnamese']}, page_id: {item['page_id']}")
    else:
        print("Không có từ nào có 'Tags' rỗng.")

# Run the asynchronous main function
# asyncio.run(main())
text = "L’angoisse"
text_correct = "l'angoisse"
print(normalize_answer(text) == text_correct )