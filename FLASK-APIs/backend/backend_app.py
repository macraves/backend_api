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


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Return all posts."""
    return jsonify(POSTS)


@app.route("/api/posts", methods=["POST"])
def handle_posts():
    """Add a new post if post is valid."""
    received_data = request.get_json()
    post = add_post(received_data, POSTS)
    if post:
        POSTS.append(post)
        return jsonify(POSTS)
    raise CustomError({"message": "Bad Data Structure", "method": "PUT"}, 400)


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete post by id."""
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post:
        POSTS.remove(post)
        return jsonify(POSTS)
    raise CustomError({f"{post_id}": "Invalid delete request"}, 404)


@app.route("/api/posts", methods=["PUT"])
def update_post(post_id):
    """Update post by id."""
    received_post = request.get_json()
    valid_post = validate_post(received_post, POSTS)
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post and valid_post:
        pop_post = POSTS.pop(POSTS.index(post))
        pop_post = valid_post
        POSTS.append(pop_post)
        return jsonify(POSTS)
    raise CustomError(
        {"message": "Put object either invalid or id coul not find", "method": "PUT"},
        404,
    )


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
