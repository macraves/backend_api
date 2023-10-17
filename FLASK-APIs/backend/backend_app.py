"""Api for the backend app.
version control applied. in VERSION dict show available version
0 is the first version where global POSTS object is used
1.0 is the second version where JSON file is used given number of sample generated randomly
1.1 adds date stamp to the posts
1.2 adds author to the posts
Related functions are backend_methods.py
!!!! limiter package gives error, still workin on it"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from backend_methods import add_post, validate_post, load_json, check_version, save_json

# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

app = Flask(__name__)
# limiter = Limiter(app, key_func=get_remote_address)

# Set a rate limit for all routes (e.g., 10 requests per minute)
# limiter.limit("10 per minute")(app)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "abcdef", "content": "zwyt."},
    {"id": 2, "title": "dcba", "content": "twu"},
]


def global_posts(version):
    """global posts"""
    if version == 0:
        return POSTS


CHOSEN = 1.2
VERSION = {"0": global_posts, "1.0": load_json, "1.1": load_json, "1.2": load_json}


# Attention here !!!
# limiter = Limiter(app, key_func=get_remote_address)
#               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: Limiter.__init__() got multiple values for argument 'key_func'
class CustomError(Exception):
    """Custom error class."""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def lower_posts_strings(posts: list):
    """Ignores whitespaces and applies title method to run
    in method for stirngs"""
    for post in posts:
        post["title"] = post["title"].strip().lower()
        post["content"] = post["content"].strip().lower()
    return posts


def page_view(star, end, data: dict or list):
    """limitation of the page view"""
    if isinstance(data, list):
        return jsonify(data[star:end])
    return jsonify(data["posts"][star:end])


# def are_there_comman_param(params, keys):
#     """Validate parameters"""
#     valid_params = keys + ["sort", "direction", "page", "limit"]
#     return all(key in valid_params for key in params.keys())


@app.route("/api/posts", methods=["GET"])
# @limiter.limit("5 per minute")
def get_posts():
    """Get all posts. It represents how to do version control
    unnecessary to at version variable but it gives general idea"""
    version = CHOSEN
    if version == 0:
        posts = VERSION[str(version)](version)
    elif version > 0:
        check_version(version)
        data = VERSION[str(version)](version)
        posts = data["posts"]
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    start_index = (page - 1) * limit
    end_index = page * limit
    # Current post exists keys
    keys = list(posts[0].keys())
    direction = {"asc": False, "desc": True}
    external_keys = ["sort", "direction", "page", "limit"]
    exists_params = {**request.args}
    all_valid_keys = keys + external_keys + list(direction.keys())
    if (
        not any(key in all_valid_keys for key in exists_params.keys())
        and len(exists_params) > 0
    ):
        raise CustomError("Invalid GET request", 400)
    # First shape the posts list with external parameters
    if all(key in external_keys for key in exists_params.keys()):
        if "sort" in exists_params:
            sort = exists_params["sort"]
            posts = sorted(
                posts,
                key=lambda post: post[sort],
                reverse=direction.get(
                    exists_params.get("direction", "asc").strip().lower()
                ),
            )
            # wheb we get here posts list is sorted
    # If there is / are common parameter(s) in the request
    if all(key in keys for key in exists_params.keys()):
        posts = [
            post
            for post in posts
            if all(post.get(key) == exists_params[key] for key in exists_params)
        ]
    return page_view(start_index, end_index, posts)


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title or content."""

    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
    if CHOSEN > 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
    posts = lower_posts_strings(posts)
    title = request.args.get("title", "").strip().lower()
    content = request.args.get("content", "").strip().lower()
    if title and content:
        filtered_posts = [
            post
            for post in posts
            if title in post["title"] or content in post["content"]
        ]
        return jsonify(filtered_posts)
    if title == "" and content:
        filtered_posts = [post for post in posts if content in post["content"]]
        return jsonify(filtered_posts)
    if title and content == "":
        filtered_posts = [post for post in posts if title in post["title"]]
        return jsonify(filtered_posts)
    return []


@app.route("/api/posts", methods=["POST"])
def handle_posts():
    """Add a new post if post is valid."""
    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
        flag = False
    else:
        flag = True
    if CHOSEN > 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
    received_data = request.get_json()

    post = add_post(received_data, data)

    if post:
        posts.append(post)
        if flag:
            save_json(data)
        return page_view(0, 20, posts)
    raise CustomError("Bad Data Structure for POST", 400)


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete post by id."""
    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
        flag = False
    else:
        flag = True
    if CHOSEN > 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
    post = next((post for post in posts if post["id"] == post_id), None)
    if post:
        posts.remove(post)
        if flag:
            save_json(data)
        return page_view(0, 20, posts)
    raise CustomError("Invalid DELETE request", 404)


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update post by id."""
    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
        flag = False
    if CHOSEN > 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        flag = True
        posts = data["posts"]
    received_post = request.get_json()
    valid_post = validate_post(received_post, data)
    post = next((post for post in posts if post["id"] == post_id), None)
    if post and valid_post:
        valid_post["id"] = post_id
        pop_post = posts.pop(posts.index(post))
        del pop_post
        posts.append(valid_post)
        if flag:
            save_json(data)
        return page_view(0, 20, posts)
    raise CustomError("PUT object either invalid or id could not find", 404)


@app.errorhandler(CustomError)
def handle_custom_error(error):
    "custom error handler"
    response = {
        "message": error.message,
        "status_code": error.status_code,
    }
    return jsonify(response), error.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
