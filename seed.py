from app import app
from models import db, User, Category, Vehicle
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Create Admin User
        if not User.query.filter_by(email="admin@amazonautolink.com").first():
            admin = User(
                name="Admin",
                email="admin@amazonautolink.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            print("✔ Admin user created.")
        else:
            print("ℹ Admin user already exists.")

        # Add Categories
        categories = ["SUV", "Sedan", "Van", "Truck"]
        for cat in categories:
            if not Category.query.filter_by(name=cat).first():
                db.session.add(Category(name=cat))
                print(f"✔ Category '{cat}' added.")

        db.session.commit()

        # Add Sample Vehicles
        sample_vehicle = Vehicle.query.first()
        if not sample_vehicle:
            suv = Category.query.filter_by(name="SUV").first()
            if suv:
                vehicle = Vehicle(
                    name="Toyota Land Cruiser",
                    description="Spacious, powerful SUV ideal for off-road.",
                    price=12000.0,
                    availability=True,
                    category_id=suv.id
                )
                db.session.add(vehicle)
                db.session.commit()
                print("✔ Sample vehicle added.")
            else:
                print("⚠ SUV category not found, skipping vehicle seed.")

        print("🎉 Seeding completed.")

if __name__ == "__main__":
    seed_data()
