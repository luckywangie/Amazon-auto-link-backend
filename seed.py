from app import app
from models import db, User, Category, Vehicle
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Create Admin User
        if not User.query.filter_by(email="admin@gmail.com").first():
            admin = User(
                name="Admin",
                email="admin@gmail.com",
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

        # Vehicles data
        vehicles_data = [
            {
                "name": "Toyota Land Cruiser",
                "description": "Spacious, powerful SUV ideal for off-road.",
                "price": 12000.0,
                "availability": True,
                "category_name": "SUV",
                "image_url": "https://i.pinimg.com/736x/c4/f5/1b/c4f51b497cfd0ee9243a845058dda64c.jpg"
            },
            {
                "name": "Honda CR-V",
                "description": "Reliable and efficient SUV great for families.",
                "price": 9500.0,
                "availability": True,
                "category_name": "SUV",
                "image_url": "https://i.pinimg.com/736x/a5/9c/a5/a59ca5d1cb5c114112ff837bf67be1d1.jpg"
            },
            {
                "name": "Toyota Camry",
                "description": "Comfortable and fuel-efficient sedan.",
                "price": 7000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://i.pinimg.com/736x/a4/9a/3a/a49a3ae24cde7e528650ae09436f233f.jpg"
            },
            {
                "name": "Mercedes-Benz C-Class",
                "description": "Luxury sedan with premium features.",
                "price": 15000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://i.pinimg.com/736x/73/e4/fd/73e4fd4077ce10f47eb458dea380cc2e.jpg"
            },
            {
                "name": "Toyota Hiace",
                "description": "Reliable van perfect for business transport.",
                "price": 11000.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://i.pinimg.com/1200x/64/5f/e3/645fe3e1bdc22e2782b4daba8a94ef5b.jpg"
            },
            {
                "name": "Ford Transit",
                "description": "Spacious van with modern features for cargo or passenger use.",
                "price": 12500.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://i.pinimg.com/1200x/97/94/c2/9794c2cdf8219fddba4f7b47d6aff96d.jpg"
            },
            {
                "name": "Isuzu N-Series",
                "description": "Durable truck for commercial use.",
                "price": 18000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://i.pinimg.com/736x/87/01/35/8701358f1cba7b9fdce67b775654ecad.jpg"
            },
            {
                "name": "Ford F-150",
                "description": "Powerful pickup truck with towing capabilities.",
                "price": 20000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://i.pinimg.com/1200x/31/c1/7d/31c17df9ff612addc9293148bb193eca.jpg"
            }
        ]

        # Seed Vehicles
        for vehicle_data in vehicles_data:
            category = Category.query.filter_by(name=vehicle_data["category_name"]).first()
            if category:
                existing_vehicle = Vehicle.query.filter_by(name=vehicle_data["name"]).first()
                if not existing_vehicle:
                    new_vehicle = Vehicle(
                        name=vehicle_data["name"],
                        description=vehicle_data["description"],
                        price=vehicle_data["price"],
                        availability=vehicle_data["availability"],
                        category_id=category.id,
                        image_url=vehicle_data["image_url"]
                    )
                    db.session.add(new_vehicle)
                    print(f"✔ Vehicle '{vehicle_data['name']}' added.")
            else:
                print(f"⚠ Category '{vehicle_data['category_name']}' not found, skipping vehicle '{vehicle_data['name']}'.")

        db.session.commit()
        print("🎉 Seeding completed.")

if __name__ == "__main__":
    seed_data()
