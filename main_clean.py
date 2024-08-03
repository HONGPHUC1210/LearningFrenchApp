
import os
from dotenv import load_dotenv
from notion_module import NotionManager
import sys
load_dotenv()

# if __name__ == '__main__':
#     database_id = os.getenv("NOTION_DATABASE_ID")
#     api_key = os.getenv("NOTION_API_KEY")

#     notion_manager = NotionManager(database_id, api_key)
#     notion_data = notion_manager.get_notion_data()
    
#     notion_manager.clean_notion_data(notion_data)
#     notion_manager.update_grouping_column(notion_data)
#     notion_manager.sort_notion_data(notion_data)

#     print("Finished")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python your_script.py <option>")
        print("Options: 1 - Clean Data, 2 - Update Grouping Column, 3 - Sort Data")
        sys.exit(1)

    option = sys.argv[1]
    database_id = os.getenv("NOTION_DATABASE_ID")
    api_key = os.getenv("NOTION_API_KEY")

    notion_manager = NotionManager(database_id, api_key)
    notion_data = notion_manager.get_notion_data()

    if option == "1":
        notion_manager.clean_notion_data(notion_data)
    elif option == "2":
        notion_manager.update_grouping_column(notion_data)
    elif option == "3":
        notion_manager.sort_notion_data(notion_data)
    else:
        print("Invalid option")

    print("Finished")