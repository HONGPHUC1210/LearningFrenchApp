import os
from dotenv import load_dotenv
import json
from collections import defaultdict
import requests
import aiohttp
import asyncio
import random

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
        """Lấy dữ liệu từ một cơ sở dữ liệu Notion (Bất đồng bộ)."""
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, timeout=60) as response:
                    if response.status == 200:
                        notion_data = await response.json()
                        return notion_data['results']
                    else:
                        print(f"Failed to get data: {response.status} - {await response.text()}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Failed to get data due to client error: {str(e)}")
                return None

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
    async def parse_notion_data(self,notion_data):
            parsed_data = []
            for item in notion_data:
                properties = item.get('properties', {})
                page_id = item.get('id', '')

                # Trích xuất 'French'
                french_property = properties.get('French', {}).get('title', [])
                french_word = french_property[0]['text']['content'] if french_property else ""

                # Trích xuất 'Vietnam'
                vietnamese_property = properties.get('Vietnam', {}).get('rich_text', [])
                vietnamese_word = vietnamese_property[0]['text']['content'] if vietnamese_property else ""

                # Trích xuất 'Tags'
                tags_property = properties.get('Tags', {}).get('select', {})
                tags = [tags_property['name']] if tags_property else []

                # Trích xuất 'Exemple'
                exemples_property = properties.get('Exemple', {}).get('rich_text', [])
                exemples = exemples_property[0]['text']['content'] if exemples_property else ""

                # Trích xuất 'Number'
                number_property = properties.get('Number', {}).get('number', 0) or 0

                # Thêm dữ liệu đã trích xuất vào danh sách, bao gồm cả page_id
                parsed_data.append({
                    'page_id': page_id,
                    'French': french_word,
                    'Vietnamese': vietnamese_word,
                    'Tags': tags,
                    'Exemple': exemples,
                    'Number': number_property
                })

            return parsed_data
    async def select_random_words(self,data, num_verbs, num_nouns, num_adjvs, num_phrases):
        # Sắp xếp dữ liệu theo `Number` từ thấp đến cao
        data_sorted_by_number = sorted(data, key=lambda x: x['Number'])

        # Lọc các từ theo tag và ưu tiên `Number` thấp
        verbs = [item for item in data_sorted_by_number if 'Tags' in item and 'Verb' in item['Tags']]
        nouns = [item for item in data_sorted_by_number if 'Tags' in item and 'Nouns' in item['Tags']]
        adjvs = [item for item in data_sorted_by_number if 'Tags' in item and 'Adj/Adv' in item['Tags']]
        phrases = [item for item in data_sorted_by_number if 'Tags' in item and 'Cụm' in item['Tags']]

        # Chọn những từ có `Number` thấp nhất
        def select_min_number_words(word_list, num_words):
            min_number = word_list[0]['Number']
            min_number_words = [word for word in word_list if word['Number'] == min_number]
            return random.sample(min_number_words, min(num_words, len(min_number_words)))

        # Chọn ngẫu nhiên các từ từ những từ có `Number` thấp nhất
        selected_verbs = select_min_number_words(verbs, num_verbs)
        selected_nouns = select_min_number_words(nouns, num_nouns)
        selected_adjvs = select_min_number_words(adjvs, num_adjvs)
        selected_phrases = select_min_number_words(phrases, num_phrases)

        selected_words = selected_verbs + selected_nouns + selected_adjvs + selected_phrases
        random.shuffle(selected_words)
        return selected_words

