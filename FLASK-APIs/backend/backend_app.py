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
from backend_methods import (
    add_post,
    validate_post,
    load_json,
    check_version,
    save_json,
    datetime,
)

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


CHOSEN = 1.0
VERSION = {"0": global_posts, "1.0": load_json, "1.1": load_json, "1.2": load_json}

if CHOSEN == 1.0:
    version_keys = ["id", "title", "content"]
if CHOSEN == 1.1:
    version_keys = ["id", "title", "content", "date"]
if CHOSEN == 1.2:
    version_keys = ["id", "title", "content", "date", "author"]


# Attention here !!!
# limiter = Limiter(app, key_func=get_remote_address)
#               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: Limiter.__init__() got multiple values for argument 'key_func'
class CustomError(Exception):
    """Custom error class."""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def titilized_post(posts: list):
    """Ignores whitespaces and applies title method
    on json files posts"""
    titlized = []
    for post in posts:
        for key in post:
            if key not in ("id", "date"):
                post[key] = post.get(key, "Unknown").title().strip()
        titlized.append(post)
    return titlized


def page_view(star, end, data: dict or list):
    """limitation of the page view and in a case global POSTS
    usage"""
    if isinstance(data, list):
        return jsonify(data[star:end])
    return jsonify(data["posts"][star:end])


def format_common_key_value(queries: dict, keys: list):
    """Format request args values accordingly to the values in the posts"""
    formattables = list(filter(lambda x: x not in ("id", "date"), keys))
    formatted = {}
    for key, val in queries.items():
        if key in formattables:
            val = val.title().strip()
        if key == "id":
            try:
                val = int(val)
            except ValueError as value_error:
                raise CustomError(value_error, 400) from value_error
        formatted[key] = val
    return formatted


def sort_without_date(sort, posts, direction, exsits_params):
    """sort without date, default direction value is set (asc)"""
    if sort == "date":
        posts = titilized_post(posts)
        posts = sorted(
            posts,
            key=lambda post: post[sort],
            reverse=direction.get(
                exsits_params.get("direcection", "asc").strip().lower()
            ),
        )
    return posts


def sort_with_date(sort, posts, direction, exists_params):
    """Date string has to be converted time object. String date format
    can not be accuaretly sorted. Default direction value is set (asc)"""
    posts = sorted(
        posts,
        key=lambda post: datetime.strptime(post[sort], "%Y-%m-%d"),
        reverse=direction.get(exists_params.get("direction", "asc").strip().lower()),
    )
    return posts


@app.route("/api/posts", methods=["GET"])
# @limiter.limit("5 per minute")
def get_posts():
    """Get all posts. It represents how to do version control
    unnecessary to at version variable but it gives general idea"""

    version = CHOSEN
    if version == 0:
        posts = VERSION[str(version)](version)
    if version >= 1.0:
        check_version(version)
        data = VERSION[str(version)](version)
        posts = data["posts"]
        # posts string values needs to match with request args values
        posts = titilized_post(posts)

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    start_index = (page - 1) * limit
    end_index = page * limit

    direction = {"asc": False, "desc": True}
    external_keys = ["sort", "direction", "page", "limit"]
    exists_params = {**request.args}
    all_valid_keys = version_keys + external_keys + list(direction.keys())
    exists_params = format_common_key_value(exists_params, version_keys)
    # while request args has key(s)if any of is not valid
    if (
        not any(key in all_valid_keys for key in exists_params)
        and len(exists_params) > 0
    ):
        raise CustomError("Invalid GET parameter(s) request", 400)
    # First shape the posts list with external parameters
    if any(key in external_keys for key in exists_params):
        sort = exists_params.get("sort", "id")  # default sort is id
        if sort != "date":
            posts = sort_without_date(sort, posts, direction, exists_params)
        if sort == "date":
            posts = sort_with_date(sort, posts, direction, exists_params)

        # When we get here posts list is sorted with sort value given parameters
    # If there is / are common parameter(s) is used, extract them from the list
    post_keys = list(
        filter(lambda x: x in ("title", "author", "content", "id"), exists_params)
    )
    if post_keys:
        posts = [
            post
            for key in post_keys
            for post in posts
            if post.get(key) == exists_params.get(key)
        ]

        return page_view(start_index, end_index, posts)
    return page_view(start_index, end_index, posts)


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title or content."""

    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
    if CHOSEN >= 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
        posts = titilized_post(posts)
    queries = {**request.args}

    queries = format_common_key_value(queries, version_keys)
    # eliminating empty values ony get keys with values
    given_params = {k: v for k, v in queries.items() if v != ""}
    # all existes posts key can be used for search
    # any invalid key in request args will be returned empty list
    if given_params:
        if (
            any(key not in version_keys for key in given_params)
            and len(given_params) > 0
        ):
            return jsonify([])
        filtered_posts = []
        for post in posts:
            for key in given_params:
                if post.get(key) == given_params[key]:
                    filtered_posts.append(post)
        return jsonify(filtered_posts)
    return jsonify(posts)


@app.route("/api/posts", methods=["POST"])
def handle_posts():
    """Add a new post if post is valid."""
    if CHOSEN == 0:
        posts = VERSION[str(CHOSEN)]
        flag = False
    if CHOSEN >= 1.0:
        flag = True
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
        posts = titilized_post(posts)
    received_data = request.get_json()

    post = add_post(received_data, data)

    if post:
        data["posts"].append(post)
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

    if CHOSEN >= 1.0:
        flag = True
        data = VERSION[str(CHOSEN)](CHOSEN)
        posts = data["posts"]
        posts = titilized_post(posts)
    post = next((post for post in posts if post["id"] == post_id), None)
    if post:
        data["posts"].remove(post)
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
    if CHOSEN >= 1.0:
        data = VERSION[str(CHOSEN)](CHOSEN)
        flag = True
        posts = data["posts"]
        posts = titilized_post(posts)
    received_post = request.get_json()
    valid_post = validate_post(received_post, data)
    if valid_post is None:
        raise CustomError("PUT object has invalid structure", 404)
    valid_post["id"] = post_id
    post = next((post for post in posts if post["id"] == post_id), None)
    if post and valid_post:
        pop_post = data["posts"].pop(posts.index(post))
        del pop_post
        data["posts"].append(valid_post)
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
