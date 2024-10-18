import asyncio
import aiohttp
import configparser
import csv
import json
import os

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Client error occurred: {e}")
    except asyncio.TimeoutError:
        print(f"Request to {url} timed out.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def get_user_profiles(group_ids, keywords):
    user_profiles = []  # List to hold user profile data
    processed_groups = set()

    async with aiohttp.ClientSession() as session:
        for group_id in group_ids:
            page_number = 1
            while page_number <15:
                url = f"https://groups.roblox.com/v1/groups/{group_id}/users?limit=100&page={page_number}"
                try:
                    response = await fetch(session, url)
                    
                    if response is None:
                        print(f"Failed to retrieve data for Group ID: {group_id}. Skipping to the next group.")
                        break  # Skip to the next group if the response is None

                    users = response.get("data", [])
                    for user in users:
                        user_data = user.get("user", {})
                        user_id = user_data.get("userId")

                        if user_id is not None:
                            groups_url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
                            groups_response = await fetch(session, groups_url)

                            if groups_response is None:
                                print(f"Failed to retrieve groups for User ID: {user_id}. Skipping to the next user.")
                                continue  # Skip to the next user if the response is None

                            user_groups = groups_response.get("data", [])
                            for group in user_groups:
                                group_info = group.get("group", {})
                                group_id = group_info.get("id")
                                group_name = group_info.get("name")

                                if group_id not in processed_groups and any(keyword.lower() in group_name.lower() for keyword in keywords):
                                    processed_groups.add(group_id)
                                    group_link = f"https://www.roblox.com/groups/{group_id}/x"
                                    print(f"User  ID: {user_id}, Group ID: {group_id}, Group Name: {group_name}, Group Link: {group_link}")

                                    user_profiles.append({
                                        "User  ID": user_id,
                                        "Group ID": group_id,
                                        "Group Name": group_name,
                                        "Group Link": group_link
                                    })

                    if not users:  # If no users are returned, break the loop
                        break

                except Exception as e:
                    print(f"An error occurred while processing Group ID {group_id}: {str(e)}")
                    break  # Skip to the next group on error instead of stopping when encountered error.

                break

            page_number += 1


    # Save the collected data to CSV and JSON files
    save_to_csv(user_profiles)
    save_to_json(user_profiles)

def save_to_csv(user_profiles):
    file_exists = os.path.isfile('potential.csv')
    existing_profiles = []

    if file_exists:
        with open('potential.csv', mode='r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            existing_profiles = [row for row in reader]

    new_profiles = [profile for profile in user_profiles if profile not in existing_profiles]

    with open('potential.csv', mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["User  ID", "Group ID", "Group Name", "Group Link"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for profile in new_profiles:
            writer.writerow(profile)

    print(f"Appended {len(new_profiles)} new profiles to potential.csv")

def save_to_json(user_profiles):
    existing_data = []
    if os.path.exists('potential.json'):
        with open('potential.json', 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)

    new_profiles = [profile for profile in user_profiles if profile not in existing_data]
    existing_data.extend(new_profiles)

    with open('potential.json', 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

    print(f"Appended {len(new_profiles)} new profiles to potential.json")

def read_config():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    group_ids = config['Settings']['group_ids'].split(',')
    keywords = config['Settings']['keywords'].split(',')
    return group_ids, keywords

if __name__ == "__main__":
    group_ids, keywords = read_config()
    asyncio.run(get_user_profiles(group_ids, keywords))