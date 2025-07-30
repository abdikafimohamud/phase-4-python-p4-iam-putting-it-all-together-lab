from app import app, db
from models import User, Recipe

with app.app_context():
    print("Seeding database...")

    db.drop_all()
    db.create_all()

    # Create test users
    user1 = User(username="alice", image_url="https://picsum.photos/200", bio="Chef Alice")
    user1.password_hash = "password123"

    user2 = User(username="bob", image_url="https://picsum.photos/200", bio="Chef Bob")
    user2.password_hash = "mypassword"

    db.session.add_all([user1, user2])
    db.session.commit()

    # Create test recipes
    recipe1 = Recipe(
        title="Spaghetti Carbonara",
        instructions="Boil pasta, cook pancetta, mix with eggs, cheese, and pepper until creamy.",
        minutes_to_complete=25,
        user_id=user1.id
    )

    recipe2 = Recipe(
        title="Vegetable Stir Fry",
        instructions="Chop vegetables, stir fry with soy sauce, garlic, and ginger until tender.",
        minutes_to_complete=15,
        user_id=user2.id
    )

    db.session.add_all([recipe1, recipe2])
    db.session.commit()

    print("Database seeded successfully!")
