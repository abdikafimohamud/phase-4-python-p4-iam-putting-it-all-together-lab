from flask import Flask, request, session
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, User, Recipe

app = Flask(__name__)
app.secret_key = "super-secret-key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)


# ---------------- Resources ---------------- #

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data["username"],
                image_url=data.get("image_url"),
                bio=data.get("bio")
            )
            new_user.password_hash = data["password"]

            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            return {
                "id": new_user.id,
                "username": new_user.username,
                "image_url": new_user.image_url,
                "bio": new_user.bio,
            }, 201
        except Exception as e:
            return {"errors": [str(e)]}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)  # ✅ Modern
            return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401



class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data["username"]).first()  # This is fine
        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password"}, 401



class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session.pop("user_id")
            return "", 204
        return {"error": "Unauthorized"}, 401


class RecipeIndex(Resource):
    def get(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return [{
            "id": r.id,
            "title": r.title,
            "instructions": r.instructions,
            "minutes_to_complete": r.minutes_to_complete,
            "user": {
                "id": r.user.id,
                "username": r.user.username,
                "image_url": r.user.image_url,
                "bio": r.user.bio
            }
        } for r in recipes], 200

    def post(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        try:
            new_recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=session["user_id"]
            )
            db.session.add(new_recipe)
            db.session.commit()

            return {
                "id": new_recipe.id,
                "title": new_recipe.title,
                "instructions": new_recipe.instructions,
                "minutes_to_complete": new_recipe.minutes_to_complete,
                "user": {
                    "id": new_recipe.user.id,
                    "username": new_recipe.user.username,
                    "image_url": new_recipe.user.image_url,
                    "bio": new_recipe.user.bio
                }
            }, 201
        except Exception as e:
            return {"errors": [str(e)]}, 422


# ---------------- Register Resources ---------------- #
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
