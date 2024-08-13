import os
import json
import requests
from collections import defaultdict
from dotenv import load_dotenv

# Nạp biến môi trường từ tệp .env
load_dotenv()

class NotionManage:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_data(self, database_id):
        """Lấy dữ liệu từ một cơ sở dữ liệu Notion."""
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        try:
            response = requests.post(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            notion_data = response.json()['results']
            return notion_data
        except requests.exceptions.RequestException as e:
            print(f"Failed to get data: {e}")
            return None

    def delete_page(self, page_id, timeout=10, max_retries=5):
        """Xóa (archive) một trang trên Notion."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"archived": True}
        retries = 0
        while retries < max_retries:
            try:
                response = requests.patch(url, headers=self.headers, json=data, timeout=timeout)
                if response.status_code == 200:
                    print(f"Page {page_id} đã được xóa.")
                    break
                else:
                    print(f"Failed to delete page {page_id}: {response.status_code} - {response.text}")
                    break
            except requests.exceptions.Timeout:
                print(f"Request to delete page {page_id} timed out. Retrying with longer timeout.")
                retries += 1
                timeout += 10  # Tăng thêm 10 giây cho mỗi lần retry

        if retries == max_retries:
            print(f"Failed to delete page {page_id} after {max_retries} retries.")

    def update_page(self, page_id, properties, timeout=10, max_retries=5):
        """Cập nhật nội dung của một trang trên Notion."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        retries = 0
        while retries < max_retries:
            try:
                response = requests.patch(url, headers=self.headers, json={"properties": properties}, timeout=timeout)
                if response.status_code == 200:
                    print(f"Page {page_id} đã được cập nhật.")
                    break
                else:
                    print(f"Failed to update page {page_id}: {response.status_code} - {response.text}")
                    break
            except requests.exceptions.Timeout:
                print(f"Request to update page {page_id} timed out. Retrying with longer timeout.")
                retries += 1
                timeout += 10  # Tăng thêm 10 giây cho mỗi lần retry

        if retries == max_retries:
            print(f"Failed to update page {page_id} after {max_retries} retries.")


def capitalize(text):
    """Viết hoa chữ cái đầu của chuỗi."""
    if text:
        return text.capitalize()
    return text

def clean_notion_database(notion_manage, database_id):
    """
    Hàm làm sạch dữ liệu Notion.

    :param notion_manage: Đối tượng NotionManage để quản lý Notion.
    :param database_id: ID của cơ sở dữ liệu Notion.
    """
    notion_data = notion_manage.get_data(database_id)
    if not notion_data:
        return

    vietnam_dict = defaultdict(list)
    french_set = set()
    pages_to_delete = []

    for page in notion_data:
        page_id = page['id']
        properties = page['properties']

        # Lấy nội dung của cột French
        french_content = properties.get('French', {}).get('title', [])
        french_text = french_content[0]['plain_text'].strip() if french_content else None

        # Lấy nội dung của cột Vietnam
        vietnam_content = properties.get('Vietnam', {}).get('rich_text', [])
        vietnam_text = vietnam_content[0]['plain_text'].strip() if vietnam_content else None

        # Viết hoa chữ cái đầu
        if french_text:
            french_text = capitalize(french_text)
        if vietnam_text:
            vietnam_text = capitalize(vietnam_text)

        # Kiểm tra và đánh dấu trang cần xóa
        if not french_text and not vietnam_text:
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

        # Cập nhật lại nội dung viết hoa cho French và Vietnam
        updated_properties = {}
        if french_text:
            updated_properties['French'] = {'title': [{'text': {'content': french_text}}]}
        if vietnam_text:
            updated_properties['Vietnam'] = {'rich_text': [{'text': {'content': vietnam_text}}]}

        # Cập nhật trang trên Notion
        if updated_properties:
            notion_manage.update_page(page_id, updated_properties)

    # In ra các trang có nội dung trùng lặp ở cột Vietnam
    print("Các trang có nội dung trùng lặp ở cột Vietnam:")
    for vietnam, ids in vietnam_dict.items():
        if len(ids) > 1:
            print(f"Nội dung: {vietnam}, Trang ID: {ids}")

    # Xóa các trang bị đánh dấu
    for page_id in pages_to_delete:
        notion_manage.delete_page(page_id)

if __name__ == "__main__":
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    # Khởi tạo đối tượng NotionManage
    notion_manage = NotionManage(api_key)

    # Làm sạch dữ liệu và phản hồi lại Notion
    clean_notion_database(notion_manage, database_id)
