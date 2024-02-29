import requests

def get_user_profiles(group_ids):
    page_cursor = None

    for group_id in group_ids:
        while True:
            try:
                url = f"https://groups.roblox.com/v1/groups/{group_id}/users"
                if page_cursor:
                    url += f"?cursor={page_cursor}"

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

                            if groups_response.status_code == 200:
                                groups_data = groups_response.json()
                                user_groups = groups_data.get("data", [])

                                for group in user_groups:
                                    group_id = group.get("group", {}).get("id")
                                    group_link = f"https://www.roblox.com/groups/{group_id}/x"
                                    print(f"User ID: {user_id}, Group ID: {group_id}, Group Link: {group_link}")

                            else:
                                print(f"Failed to retrieve groups for User ID: {user_id}. Status code: {groups_response.status_code}")

                    page_cursor = data.get("nextPageCursor")
                    if page_cursor is None:
                        break

                else:
                    print(f"Failed to retrieve data for Group ID: {group_id}. Status code: {response.status_code}")
                    break

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                break

if __name__ == "__main__":
    group_ids = ["33687674"]
    get_user_profiles(group_ids)
