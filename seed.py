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

        # Updated vehicles data with better image URLs
        vehicles_data = [
            {
                "name": "Toyota Land Cruiser",
                "description": "Spacious, powerful SUV ideal for off-road.",
                "price": 12000.0,
                "availability": True,
                "category_name": "SUV",
                "image_url": "https://images.unsplash.com/photo-1606152421802-db97b9c7a11b?w=500&h=300&fit=crop"
            },
            {
                "name": "Honda CR-V",
                "description": "Reliable and efficient SUV great for families.",
                "price": 9500.0,
                "availability": True,
                "category_name": "SUV",
                "image_url": "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=500&h=300&fit=crop"
            },
            {
                "name": "Toyota Camry",
                "description": "Comfortable and fuel-efficient sedan.",
                "price": 7000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=500&h=300&fit=crop"
            },
            {
                "name": "Mercedes-Benz C-Class",
                "description": "Luxury sedan with premium features.",
                "price": 15000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500&h=300&fit=crop"
            },
            {
                "name": "Toyota Hiace",
                "description": "Reliable van perfect for business transport.",
                "price": 11000.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&h=300&fit=crop"
            },
            {
                "name": "Ford Transit",
                "description": "Spacious van with modern features for cargo or passenger use.",
                "price": 12500.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=500&h=300&fit=crop"
            },
            {
                "name": "Isuzu N-Series",
                "description": "Durable truck for commercial use.",
                "price": 18000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=500&h=300&fit=crop"
            },
            {
                "name": "Ford F-150",
                "description": "Powerful pickup truck with towing capabilities.",
                "price": 20000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://images.unsplash.com/photo-1593941707874-ef25b8b4a92b?w=500&h=300&fit=crop"
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
                        image_url=vehicle_data["image_url"]  # Ensure image_url is set
                    )
                    db.session.add(new_vehicle)
                    print(f"✔ Vehicle '{vehicle_data['name']}' added with image URL.")
            else:
                print(f"⚠ Category '{vehicle_data['category_name']}' not found, skipping vehicle '{vehicle_data['name']}'.")

        db.session.commit()
        print("🎉 Seeding completed.")

if __name__ == "__main__":
    seed_data()