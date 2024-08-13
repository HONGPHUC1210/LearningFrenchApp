import os
from dotenv import load_dotenv
import json
from collections import defaultdict
import requests


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




