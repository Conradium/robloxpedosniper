import requests
import configparser

def read_config():
    config = configparser.ConfigParser()
    config.read('config.cfg')

    group_ids = config['Settings']['group_ids'].split(',')
    keywords = config['Settings']['keywords'].split(',')

    return group_ids, keywords

def get_user_profiles(group_ids, keywords):
    page_cursor = None

    for group_id in group_ids:
        page_number = 1
        processed_groups = set()

        while True:
            try:
                url = f"https://groups.roblox.com/v1/groups/{group_id}/users?cursor=&limit=100&page={page_number}"
                if page_cursor:
                    url += f"&cursor={page_cursor}"

                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    users = data.get("data", [])

                    for user in users:
                        user_data = user.get("user", {})
                        user_id = user_data.get("userId")

                        if user_id is not None:
                            groups_url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
                            groups_response = requests.get(groups_url)

                            try:
                                groups_response.raise_for_status()
                                groups_data = groups_response.json()
                                user_groups = groups_data.get("data", [])

                                for group in user_groups:
                                    group_info = group.get("group", {})
                                    group_id = group_info.get("id")
                                    group_name = group_info.get("name")

                                    
                                    if group_id not in processed_groups and any(keyword.lower() in group_name.lower() for keyword in keywords):
                                        processed_groups.add(group_id)

                                        group_link = f"https://www.roblox.com/groups/{group_id}/x"
                                        print(f"User ID: {user_id}, Group ID: {group_id}, Group Name: {group_name}, Group Link: {group_link}")

                            except requests.exceptions.HTTPError as http_err:
                                print(f"Failed to retrieve groups for User ID: {user_id}. Status code: {groups_response.status_code}")
                                print(f"Error details: {http_err}")

                            except Exception as e:
                                print(f"An unexpected error occurred while processing user groups: {str(e)}")

                    page_cursor = data.get("nextPageCursor")
                    if page_cursor is None:
                        break

                    page_number += 1 

                else:
                    print(f"Failed to retrieve data for Group ID: {group_id}. Status code: {response.status_code}")
                    break

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                

if __name__ == "__main__":
    group_ids, keywords = read_config()
    get_user_profiles(group_ids, keywords)
