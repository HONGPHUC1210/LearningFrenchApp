import os
import json
import asyncio
from dotenv import load_dotenv
from notion_manager import NotionManage



import json

def save_cleaned_data_to_json(cleaned_data, file_name="test.json"):
    """
    Hàm lưu dữ liệu đã làm sạch ra tệp JSON và in ra số lượng phần tử.

    :param cleaned_data: Dữ liệu đã làm sạch (danh sách các từ điển).
    :param file_name: Tên tệp JSON để lưu dữ liệu.
    """
    try:
        # Lưu dữ liệu vào tệp JSON
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(cleaned_data, json_file, ensure_ascii=False, indent=4)
        print(f"Dữ liệu đã được lưu thành công vào tệp {file_name}")
        
        # In ra số lượng phần tử
        element_count = len(cleaned_data)
        print(f"Số lượng phần tử trong tệp JSON: {element_count}")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")

# Ví dụ sử dụng:
# save_cleaned_data_to_json(cleaned_data)



import aiohttp

async def get_data_async(database_id):
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

                async with session.post(url, headers=headers, json=payload, timeout=60) as response:
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
async def main():
    # Khởi tạo đối tượng NotionManage
    mana = NotionManage(api_key)
    
    # Lấy dữ liệu từ Notion (sử dụng await để chờ kết quả)
    raw = await mana.get_data_async(database_id)
    
    # Lưu dữ liệu vào tệp JSON
    save_cleaned_data_to_json(raw)
    

# Chạy hàm main bằng asyncio
if __name__ == "__main__":
    # Nạp biến môi trường từ tệp .env
    load_dotenv()
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    asyncio.run(main())
