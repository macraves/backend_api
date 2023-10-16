"""Api for the backend app."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend_methods import add_post, validate_post, load_json, check_version

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
VERSION = {"0": POSTS, "1.0": load_json()}


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
    """Ignores whitespaces and applies title method"""
    for post in posts:
        post["title"] = post["title"].strip().lower()
        post["content"] = post["content"].strip().lower()
    return posts


@app.route("/api/posts", methods=["GET"])
# @limiter.limit("5 per minute")
def get_posts():
    """Get all posts."""
    version = 0
    if version > 0:
        check_version(1.0)
    posts = VERSION[str(version)]
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=20, type=int)
    start_index = (page - 1) * limit
    end_index = page * limit
    sort = request.args.get("sort", "").strip().lower()
    direction = request.args.get("direction", "").strip().lower()
    direct = {"asc": False, "desc": True}
    if version == 0:
        keys = {"title": "title", "content": "content", "id": "id"}
        if sort in keys and direction in direct:
            return jsonify(
                sorted(
                    posts,
                    key=lambda post: post[keys[sort]],
                    reverse=direct[direction],
                )
            )
        raise CustomError("Invalid sort or direction", 400)
    if version == 1.0:
        keys = list(posts["posts"][0].keys())
        if sort in keys and direction in direct:
            return jsonify(
                sorted(
                    posts,
                    key=lambda post: post[keys[sort]],
                    reverse=direct[direction],
                )
            )
        raise CustomError("Invalid sort or direction", 400)
    return jsonify(posts[start_index:end_index])


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title or content."""
    posts = load_json()
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
    posts = load_json()
    received_data = request.get_json()
    post = add_post(received_data, posts)
    if post:
        posts.append(post)
        return jsonify(posts)
    raise CustomError("Bad Data Structure for POST", 400)


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete post by id."""
    posts = load_json()
    post = next((post for post in posts if post["id"] == post_id), None)
    if post:
        posts.remove(post)
        return jsonify(posts)
    raise CustomError("Invalid DELETE request", 404)


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update post by id."""
    posts = load_json()
    received_post = request.get_json()
    valid_post = validate_post(received_post, posts)
    post = next((post for post in posts if post["id"] == post_id), None)
    if post and valid_post:
        valid_post["id"] = post_id
        pop_post = posts.pop(posts.index(post))
        del pop_post
        posts.append(valid_post)
        return jsonify(posts)
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
