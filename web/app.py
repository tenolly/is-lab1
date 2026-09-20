import os
import re
import logging
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Flask, jsonify, request
from markupsafe import escape
import jwt

from models import db, User, Post

logging.basicConfig(filename='app.log', level=logging.INFO)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

JWT_ALGORITHM = "HS256"

db.init_app(app)


with app.app_context():
    db.create_all()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401
        
        token = auth_header.split(" ")[1].strip()
        
        try:
            payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=JWT_ALGORITHM)
            if not (current_user := db.session.get(User, int(payload["sub"]))):
                return jsonify({"error": "User not found"}), 401
        
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {repr(e)}"}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    login = data.get("login")
    password = data.get("password")
    
    if not login or not password:
        return jsonify({"error": "Login and password are required"}), 400

    if not re.match(r"^[a-zA-Z0-9_-]{4,20}$", login):
        return jsonify({
            "error": "Login must be between 4 and 20 characters long and contain only letters, numbers, underscores, and hyphens."
        }), 400
        
    if not (
        6 <= len(password) <= 32 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password)
    ):
        return jsonify({
            "error": (
                "Password must be between 6 and 32 characters long and contain at least one uppercase letter, "
                "one lowercase letter, and one number."
            )
        }), 400
        
    if User.query.filter_by(login=login).first():
        return jsonify({"error": "User with this login already exists"}), 400
        
    new_user = User(login=login)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": {"id": new_user.id, "login": new_user.login}
    }), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    
    login = data.get("login")
    password = data.get("password")
    
    if not login or not password:
        return jsonify({"error": "Login and password are required"}), 400
        
    user = User.query.filter_by(login=login).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
        
    payload = {
        "sub": str(user.id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm=JWT_ALGORITHM)
    
    return jsonify({"access_token": token, "token_type": "Bearer"}), 200


@app.route("/api/data", methods=["GET"])
@token_required
def get_posts(current_user):
    posts = Post.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for post in posts:
        result.append({
            "id": post.id,
            "title": str(escape(post.title)),
            "description": str(escape(post.description)) if post.description else None
        })
        
    return jsonify(result), 200


@app.route("/api/data", methods=["POST"])
@token_required
def create_post(current_user):
    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
        
    new_post = Post(
        title=title,
        description=description,
        user_id=current_user.id
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({
        "message": "Post created successfully",
        "post": {
            "id": new_post.id,
            "title": str(escape(new_post.title)),
            "description": str(escape(new_post.description)) if new_post.description else None
        }
    }), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
