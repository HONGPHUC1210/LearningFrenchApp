import os
import json
from collections import defaultdict
import requests
import aiohttp
import asyncio

class NotionManage:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_data(self, database_id):
        """Lấy dữ liệu từ một cơ sở dữ liệu Notion (Đồng bộ)."""
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        try:
            response = requests.post(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            notion_data = response.json()['results']
            return notion_data
        except requests.exceptions.RequestException as e:
            print(f"Failed to get data: {e}")
            return None

    async def get_data_async(self, database_id):
        """Lấy toàn bộ dữ liệu từ một cơ sở dữ liệu Notion (Bất đồng bộ), xử lý phân trang."""
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        all_results = []
        has_more = True
        start_cursor = None

        async with aiohttp.ClientSession() as session:
            try:
                while has_more:
                    payload = {}
                    if start_cursor:
                        payload['start_cursor'] = start_cursor

                    async with session.post(url, headers=self.headers, json=payload, timeout=60) as response:
                        if response.status == 200:
                            notion_data = await response.json()
                            all_results.extend(notion_data['results'])
                            has_more = notion_data.get('has_more', False)
                            start_cursor = notion_data.get('next_cursor')
                        else:
                            print(f"Failed to get data: {response.status} - {await response.text()}")
                            return None
            except aiohttp.ClientError as e:
                print(f"Failed to get data due to client error: {str(e)}")
                return None

        return all_results

    def update_page(self, page_id, properties, timeout=10, max_retries=5):
        """Cập nhật nội dung của một trang trên Notion (Đồng bộ)."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        retries = 0
        while retries < max_retries:
            try:
                response = requests.patch(url, headers=self.headers, json={"properties": properties}, timeout=timeout)
                if response.status_code == 200:
                    print(f"Page {page_id} đã được cập nhật.")
                    break
                else:
                    print(f"Failed to update page {page_id}: {response.status_code} - {response.text()}")
                    break
            except requests.exceptions.Timeout:
                print(f"Request to update page {page_id} timed out. Retrying with longer timeout.")
                retries += 1
                timeout += 10  # Tăng thêm 10 giây cho mỗi lần retry

        if retries == max_retries:
            print(f"Failed to update page {page_id} after {max_retries} retries.")

    async def update_page_async(self, page_id, properties, timeout=10, max_retries=5):
        """Cập nhật nội dung của một trang trên Notion (Bất đồng bộ)."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        retries = 0
        async with aiohttp.ClientSession() as session:
            while retries < max_retries:
                try:
                    async with session.patch(url, headers=self.headers, json={"properties": properties}, timeout=timeout) as response:
                        if response.status == 200:
                            print(f"Page {page_id} đã được cập nhật.")
                            return
                        else:
                            print(f"Failed to update page {page_id}: {response.status} - {await response.text()}")
                            return
                except asyncio.TimeoutError:
                    print(f"Request to update page {page_id} timed out. Retrying with longer timeout.")
                except aiohttp.ClientError as e:
                    print(f"Request to update page {page_id} failed due to client error: {str(e)}")
                    break  # Nếu muốn dừng hẳn khi gặp lỗi client, có thể thêm `break` ở đây

                retries += 1
                timeout += 10  # Tăng thêm 10 giây cho mỗi lần retry

        print(f"Failed to update page {page_id} after {max_retries} retries.")
    async def delete_page_async(self, page_id, timeout=10, max_retries=5):
        """Xóa một trang trên Notion (Bất đồng bộ)."""
        url = f"https://api.notion.com/v1/blocks/{page_id}"
        retries = 0
        async with aiohttp.ClientSession() as session:
            while retries < max_retries:
                try:
                    async with session.delete(url, headers=self.headers, timeout=timeout) as response:
                        if response.status == 200:
                            print(f"Page {page_id} đã được xóa.")
                            return
                        else:
                            print(f"Failed to delete page {page_id}: {response.status} - {await response.text()}")
                            return
                except asyncio.TimeoutError:
                    print(f"Request to delete page {page_id} timed out. Retrying with longer timeout.")
                except aiohttp.ClientError as e:
                    print(f"Request to delete page {page_id} failed due to client error: {str(e)}")
                    break  # Nếu muốn dừng hẳn khi gặp lỗi client, có thể thêm `break` ở đây

                retries += 1
                timeout += 10  # Tăng thêm 10 giây cho mỗi lần retry

        print(f"Failed to delete page {page_id} after {max_retries} retries.")
