import os
import sys
import asyncio
from collections import defaultdict
from dotenv import load_dotenv

# Nạp biến môi trường từ tệp .env
load_dotenv()

# Thêm đường dẫn tới module notion_module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from notion_module import NotionManage  # Import từ module notion_module

def capitalize(text):
    """Viết hoa chữ cái đầu của chuỗi."""
    if text:
        return text.capitalize()
    return text

async def clean_notion_database(notion_manager, database_id):
    """
    Hàm làm sạch dữ liệu Notion.

    :param notion_manage: Đối tượng NotionManage để quản lý Notion.
    :param database_id: ID của cơ sở dữ liệu Notion.
    """
    notion_data = await notion_manager.get_data_async(database_id)  # Sử dụng await để chờ kết quả
    if not notion_data:
        return

    vietnam_dict = defaultdict(list)
    french_set = set()
    pages_to_delete = []
    
    remaining_pages = 0  # Biến để đếm số lượng hàng còn lại sau khi làm sạch

    for page in notion_data:
        page_id = page['id']
        properties = page['properties']

        # Lấy nội dung của cột French
        french_content = properties.get('French', {}).get('title', [])
        french_text = french_content[0]['plain_text'].strip() if french_content else None

        # Lấy nội dung của cột Vietnam
        vietnam_content = properties.get('Vietnam', {}).get('rich_text', [])
        vietnam_text = vietnam_content[0]['plain_text'].strip() if vietnam_content else None

        # Lấy nội dung của cột English
        english_content = properties.get('English', {}).get('rich_text', [])
        english_text = english_content[0]['plain_text'].strip() if english_content else None

        # Lấy nội dung của cột Exemple
        exemple_content = properties.get('Exemple', {}).get('rich_text', [])
        exemple_text = exemple_content[0]['plain_text'].strip() if exemple_content else None

        # Viết hoa chữ cái đầu
        if french_text:
            french_text = capitalize(french_text)
        if vietnam_text:
            vietnam_text = capitalize(vietnam_text)
        if exemple_text:
            exemple_text = capitalize(exemple_text)
        if english_text:
            english_text = capitalize(english_text)

        # Kiểm tra và đánh dấu trang cần xóa
        if not french_text and not vietnam_text and not exemple_text and not english_text:
            pages_to_delete.append(page_id)
            continue

        # Kiểm tra trùng lặp ở cột French
        if french_text in french_set:
            pages_to_delete.append(page_id)
            continue
        else:
            french_set.add(french_text)

        # Ghi lại các trang có trùng lặp ở cột Vietnam
        if vietnam_text:
            vietnam_dict[vietnam_text].append(page_id)

        # Cập nhật lại nội dung viết hoa cho French, Vietnam, và Exemple
        updated_properties = {}
        if french_text:
            updated_properties['French'] = {'title': [{'text': {'content': french_text}}]}
        if vietnam_text:
            updated_properties['Vietnam'] = {'rich_text': [{'text': {'content': vietnam_text}}]}
        if exemple_text:
            updated_properties['Exemple'] = {'rich_text': [{'text': {'content': exemple_text}}]}
        if english_text:
            updated_properties['Exemple'] = {'rich_text': [{'text': {'content': english_text}}]}

        # Cập nhật trang trên Notion
        if updated_properties:
            await notion_manager.update_page_async(page_id, updated_properties)  # Sử dụng await để chờ kết quả

        # Tăng số lượng hàng còn lại
        remaining_pages += 1

    # In ra các trang có nội dung trùng lặp ở cột Vietnam
    print("Các trang có nội dung trùng lặp ở cột Vietnam:")
    for vietnam, ids in vietnam_dict.items():
        if len(ids) > 1:
            print(f"Nội dung: {vietnam}, Trang ID: {ids}")

    # Xóa các trang bị đánh dấu
    for page_id in pages_to_delete:
        # Kiểm tra lý do xóa trang
        if page_id in [item for sublist in vietnam_dict.values() for item in sublist if len(sublist) > 1]:
            reason = "Duplicate: 'Vietnam'"
        elif page_id in french_set:
            reason = "Duplicate: 'French'"
        else:
            reason = "Empty"

        print(f"Xóa trang với ID: {page_id} - Lý do: {reason}")
        await notion_manager.delete_page_async(page_id)  # Sử dụng await để chờ kết quả

    # In ra tổng số hàng còn lại sau khi làm sạch
    print(f"Tổng số hàng còn lại sau khi làm sạch: {remaining_pages}")

if __name__ == "__main__":
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    notion_manager = NotionManage(api_key)
    
    # Sử dụng asyncio để chạy hàm bất đồng bộ
    asyncio.run(clean_notion_database(notion_manager, database_id))
