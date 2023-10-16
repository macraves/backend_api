"""Backend methods for the Flask API."""


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
