"""Api for the backend app."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend_methods import add_post, validate_post

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


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
def get_books():
    """Get all posts."""
    return jsonify(POSTS)


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title or content."""
    posts = lower_posts_strings(POSTS)
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
    raise CustomError("Invalid search request", 400)


@app.route("/api/posts", methods=["POST"])
def handle_posts():
    """Add a new post if post is valid."""
    received_data = request.get_json()
    post = add_post(received_data, POSTS)
    if post:
        POSTS.append(post)
        return jsonify(POSTS)
    raise CustomError("Bad Data Structure for POST", 400)


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete post by id."""
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post:
        POSTS.remove(post)
        return jsonify(POSTS)
    raise CustomError("Invalid DELETE request", 404)


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update post by id."""
    received_post = request.get_json()
    valid_post = validate_post(received_post, POSTS)
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post and valid_post:
        valid_post["id"] = post_id
        pop_post = POSTS.pop(POSTS.index(post))
        del pop_post
        POSTS.append(valid_post)
        return jsonify(POSTS)
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
