import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class NotionManager:
    def __init__(self, database_id, api_key):
        self.database_id = database_id
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_notion_data(self):

        """
        Fetch data from a Notion database.

        :return: The raw data retrieved from the Notion database.
        """
        print("Getting notion data...")
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            notion_data = response.json()['results']
            return notion_data
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception("Failed to fetch data from Notion")

    def parse_notion_data(self, notion_data):
        """
        Parse raw Notion data into a more usable format.

        :param notion_data: Raw data from the Notion database.
        :return: Parsed data.
        """
        parsed_data = []
        for item in notion_data:
            properties = item['properties']
            if 'French' in properties and 'Vietnam' in properties and 'Tags' in properties:
                french_property = properties['French']['title']
                vietnamese_property = properties['Vietnam']['rich_text']
                tags_property = properties['Tags']

                if french_property and vietnamese_property:
                    french_word = french_property[0]['text']['content'] if french_property else ""
                    vietnamese_word = vietnamese_property[0]['text']['content'] if vietnamese_property else ""

                    tags = []
                    if tags_property['type'] == 'select' and tags_property['select']:
                        tags.append(tags_property['select']['name'])
                    elif tags_property['type'] == 'multi_select' and tags_property['multi_select']:
                        tags = [tag['name'] for tag in tags_property['multi_select']]

                    parsed_data.append({'French': french_word, 'Vietnamese': vietnamese_word, 'Tags': tags})
        return parsed_data

    def delete_notion_page(self, page_id):
        """
        Delete a Notion page by archiving it.

        :param page_id: The ID of the Notion page.
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"archived": True}
        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 200:
            print(f"Page {page_id} deleted successfully")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception("Failed to delete page")

    def update_notion_page(self, page_id, french_word=None, vietnamese_word=None, grouping=None):
        """
        Update a Notion page with new values.

        :param page_id: The ID of the Notion page.
        :param french_word: The new French word to update.
        :param vietnamese_word: The new Vietnamese word to update.
        :param grouping: The new grouping value to update.
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"properties": {}}
        if french_word:
            data["properties"]["French"] = {
                "title": [{"text": {"content": french_word.capitalize()}}]
            }
        if vietnamese_word:
            data["properties"]["Vietnam"] = {
                "rich_text": [{"text": {"content": vietnamese_word.capitalize()}}]
            }
        if grouping:
            data["properties"]["Grouping"] = {"select": {"name": grouping}}
        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Failed to update page {page_id}: {response.text}")

    def update_grouping_column(self, notion_data):
        """
        Update the grouping column for each item in the Notion database.

        :param notion_data: The data from the Notion database.
        """
        for item in notion_data:
            properties = item['properties']
            grouping = properties['Grouping']['select']['name'] if 'Grouping' in properties and properties['Grouping']['select'] is not None else ""
            if not grouping:
                tag = properties['Tags']['select']['name'] if 'Tags' in properties and properties['Tags']['select'] is not None else ""
                if tag.lower() == 'verb':
                    grouping = "1"
                else:
                    grouping = "0"
                self.update_notion_page(item['id'], grouping=grouping)
        print("Finished updating grouping")

    def clean_notion_data(self, notion_data):

        print("Cleaning notion data...")
        """
        Clean the Notion database by removing duplicates and empty values.

        :param notion_data: The data from the Notion database.
        """
        def add_to_set(word_set, word, item_id, duplicate_dict):
            if word in word_set:
                self.delete_notion_page(item_id)
                return False
            word_set.add(word)
            return True

        french_set = set()
        vietnamese_set = set()
        duplicate_vietnamese = {}

        for item in notion_data:
            properties = item['properties']
            french_word = properties['French']['title'][0]['text']['content'].strip() if properties['French']['title'] else ""
            vietnamese_word = properties['Vietnam']['rich_text'][0]['text']['content'].strip() if properties['Vietnam']['rich_text'] else ""

            if not french_word and not vietnamese_word:
                self.delete_notion_page(item['id'])
                continue

            french_word = french_word.capitalize() if french_word else None
            vietnamese_word = vietnamese_word.capitalize() if vietnamese_word else None

            if french_word and not add_to_set(french_set, french_word, item['id'], duplicate_vietnamese):
                continue

            if vietnamese_word:
                if vietnamese_word in vietnamese_set:
                    if vietnamese_word not in duplicate_vietnamese:
                        duplicate_vietnamese[vietnamese_word] = []
                    duplicate_vietnamese[vietnamese_word].append((french_word, item['id']))
                else:
                    vietnamese_set.add(vietnamese_word)

            if french_word or vietnamese_word:
                self.update_notion_page(item['id'], french_word, vietnamese_word)

        if duplicate_vietnamese:
            for vietnamese_word, duplicates in duplicate_vietnamese.items():
                print(f"Duplicate Vietnamese words found for '{vietnamese_word}':")
                for french_word, page_id in duplicates:
                    print(f" - {french_word} (Page ID: {page_id})")

        print("Finished cleaning data")

    def sort_notion_data(self, notion_data):
        print("Sorting notion data...")
        """
        Sort the Notion database by Vietnamese and Theme properties.

        :param notion_data: The data from the Notion database.
        """
        sorted_data = sorted(notion_data, key=lambda x: (
            x['properties']['Vietnam']['rich_text'][0]['text']['content'] if 'Vietnam' in x['properties'] and x['properties']['Vietnam']['rich_text'] else "", 
            x['properties']['Theme']['multi_select'][0]['name'] if 'Theme' in x['properties'] and x['properties']['Theme']['multi_select'] else ""
        ))
        for item in sorted_data:
            self.update_notion_page(item['id'])

        print("Finished sorting data")
