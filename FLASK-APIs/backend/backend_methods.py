"""Backend methods for the Flask API."""
import os
import json
import random
import string

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FOLDER_PATH = os.path.join(SCRIPT_DIR, "STORAGE")
FILE_PATH = os.path.join(FOLDER_PATH, "posts.json")


def save_json(data):
    """Writes data to the json file"""
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except json.JSONDecodeError as error:
        print(f"Reading {FILE_PATH} failed: {error}")


def load_json():
    """Reads the json file"""
    if not os.path.exists(FILE_PATH):
        return None
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data
    except json.JSONDecodeError as error:
        print(f"Reading {FILE_PATH} failed: {error}")
        return None


def check_version(version):
    """Initializes the json file or update its version."""
    initilization = {"version": version, "posts": []}
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"Folder {FOLDER_PATH} created")
    if not os.path.exists(FILE_PATH):
        save_json(initilization)
        print(f"File {FILE_PATH} created")
    exists_data = load_json()
    if exists_data.get("version") != version:
        exists_data["version"] = version
        save_json(exists_data)
        print(f"Version is updataed to {version}")
    else:
        print(f"Version is up to date {version}")


def generate_random_word(length):
    """Generates random words"""
    characters = string.ascii_lowercase  # Use lowercase letters
    return "".join(random.choice(characters) for _ in range(length))


def sample_posts():
    """Sample posts."""
    for i in range(100):
        title = generate_random_word(5)
        content = generate_random_word(10)
        _id = i + 1
        yield {"id": _id, "title": title, "content": content}


def create_test_posts():
    """Creates test posts."""
    posts = []
    for post in sample_posts():
        posts.append(post)
    check_version(1.0)
    data = load_json()
    data["posts"] = posts
    save_json(data)


def add_new_keys_in_posts(key, value):
    """Add new keys in posts"""
    data = load_json()
    if len(data["posts"]) > 0:
        generator = ({**d, key: value} for d in data["posts"])
    save_json(list(generator))


def generate_new_id(posts: list):
    """Finds max value in posts and assigns max + 1"""
    if len(posts) > 0:
        return max(post["id"] for post in posts) + 1
    return 1


def format_post_strings(post: dict):
    """Ignores whitespaces and applies title method"""

    title = post.get("title", "").strip().capitalize()
    content = post.get("content", "").strip().capitalize()
    post_id = post.get("id")
    return {"id": post_id, "title": title, "content": content}


def validate_post(post: dict, posts):
    """validatation for the post"""
    if isinstance(post, dict) and "title" in post and "content" in post:
        # Check if post has "id" key
        if post.get("id") is None:
            # Generate a new id
            post["id"] = generate_new_id(posts)
            return format_post_strings(post)
        else:
            # In here post has "id" key
            post_id = post.get("id")
            if isinstance(post_id, int):
                if next((post for post in posts if post["id"] == post_id), None):
                    # Get new id
                    post_id = generate_new_id(posts=posts)
            return format_post_strings(post)
    return None


def add_post(post: dict, posts: list):
    """Checks if it is valid
    add a unique id and return the post"""
    is_valid_post = validate_post(post, posts)
    if is_valid_post:
        return is_valid_post
    return None
