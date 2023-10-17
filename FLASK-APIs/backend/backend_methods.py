"""Backend methods for the Flask API."""
import os
import json
import random
import string
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FOLDER_PATH = os.path.join(SCRIPT_DIR, "STORAGE")
FILE_PATH = os.path.join(FOLDER_PATH, "posts.json")


def save_json(dataset: dict):
    """Writes data to the json file"""
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(dataset, file, indent=4)
    except json.JSONDecodeError as error:
        print(f"Reading {FILE_PATH} failed: {error}")


def load_json(version: float) -> dict or None:
    """Reads the json file"""
    if not os.path.exists(FILE_PATH):
        return None
    try:
        check_version(version)
        with open(FILE_PATH, "r", encoding="utf-8") as json_file:
            dataset = json.load(json_file)
        return dataset
    except json.JSONDecodeError as error:
        print(f"Reading {FILE_PATH} failed: {error}")
        return None


def read_json():
    """Reads the json file"""
    if not os.path.exists(FILE_PATH):
        return None
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as json_file:
            dataset = json.load(json_file)
        return dataset
    except json.JSONDecodeError as error:
        print(f"Reading {FILE_PATH} failed: {error}")
        return None


def generate_random_date():
    """Generates random date"""
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2023, 12, 31)
    # (start + random(0 , end - start))
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    return random_date.strftime("%Y-%m-%d")


def check_version(version: float):
    """Initializes the json file or update its version."""
    initilization = {"version": version, "posts": []}
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"Folder {FOLDER_PATH} created")
    if not os.path.exists(FILE_PATH):
        save_json(initilization)
        print(f"File {FILE_PATH} created")
    exists_data = read_json()
    if version == 1.0 and exists_data.get("version") != version:
        exists_data["version"] = version
        create_test_posts(version)
        print(f"Version is updataed to {version}")
    else:
        print(f"Version is up to date {version}")
    if version == 1.1 and exists_data.get("version") != version:
        exists_data["version"] = version
        add_new_keys_in_posts("date", generate_random_date, exists_data)
        print(f"Version is updataed to {version}")
    if version == 1.2 and exists_data.get("version") != version:
        exists_data["version"] = version
        add_new_keys_in_posts("author", add_fake_authors, exists_data)
        print(f"Version is updataed to {version}")


def generate_random_word(length: int) -> str:
    """Generates random words"""
    characters = string.ascii_lowercase  # Use lowercase letters
    return "".join(random.choice(characters) for _ in range(length))


def random_words(num):
    """Sample posts."""
    for i in range(num):
        title = generate_random_word(5)
        content = generate_random_word(10)
        _id = i + 1
        yield {"id": _id, "title": title, "content": content}


def create_test_posts(version: float, num: int = 20):
    """Creates a new dictionary of dictionaryies in the format
    {"version": version, "posts": posts}. Overwrites the existing
    Args:
        version (float): _description_
    """
    posts = []
    for post in random_words(num):
        posts.append(post)
    save_json({"version": version, "posts": posts})
    check_version(version)


def add_fake_authors():
    """add fake authors"""
    return fake.name()


def add_new_keys_in_posts(key, value, data):
    """add new key in dictionaries of post in exists data set
    Args:
        key (str): key name
        value (func): appropiate function to create value
    """
    if len(data["posts"]) > 0:
        generator = ({**d, key: value()} for d in data["posts"])
        data["posts"] = list(generator)
        save_json(data)


def generate_new_id(posts: list):
    """Finds max value in the posts list and assigns max + 1"""
    if len(posts) > 0:
        return max(post["id"] for post in posts) + 1
    return 1


def format_post_strings(post: dict, posts: list):
    """Ignores whitespaces on key value pairs
    and applies capitalize method"""
    sample = list(posts[0].keys())
    for key in sample:
        if key != "id" and post.get(key):
            post[key] = post[key].strip().capitalize()
        else:
            post[key] = "Anonymous"


def validate_post(post: dict, posts: list) -> dict or None:
    """In the given post firstly get tested for existance of keys "title" and "content"
    secondly checks if "id" is presenet and if it is present checks if it is unique
    Args:
        post (dict): received post by api
        posts (list): list of posts

    Returns:
        dict or None: it returns only validated post
    """
    if isinstance(post, dict) and "title" in post and "content" in post:
        # Check if post has "id" key
        if post.get("id") is None:
            # Generate a new id
            post["id"] = generate_new_id(posts)
            return format_post_strings(post, posts)
        else:
            # In here post has "id" key
            if isinstance(post.get("id"), int):
                post_id = post.get("id")
                if next((post for post in posts if post["id"] == post_id), None):
                    # Get new id
                    post["id"] = generate_new_id(posts=posts)
            return format_post_strings(post, posts)
    return None


def add_post(post: dict, posts: list):
    """Checks if it is valid
    add a unique id and return the post"""
    is_valid_post = validate_post(post, posts)
    if is_valid_post:
        return is_valid_post
    return None


def test_to_initialise():
    """Test to initialise the json file
    avaialble versions are 1.0, 1.1, 1.2"""
    version = 1.2
    # create_test_posts(version)
    check_version(version)


# test_to_initialise()
