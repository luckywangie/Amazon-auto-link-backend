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
                "image_url": "https://i.pinimg.com/736x/dd/fd/31/ddfd311cc524dcea4753a1259ea67756.jpg"
            },
            {
                "name": "Honda CR-V",
                "description": "Reliable and efficient SUV great for families.",
                "price": 9500.0,
                "availability": True,
                "category_name": "SUV",
                "image_url": "https://hondanews.com/en-US/photos/download/45a34b6c1f574b2a9222eddf01521f65"
            },
            {
                "name": "Toyota Camry",
                "description": "Comfortable and fuel-efficient sedan.",
                "price": 7000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://www.toyota.com/imgix/responsive/images/mlp/colorizer/2022/camry/1H1.png"
            },
            {
                "name": "Mercedes-Benz C-Class",
                "description": "Luxury sedan with premium features.",
                "price": 15000.0,
                "availability": True,
                "category_name": "Sedan",
                "image_url": "https://cdn.motor1.com/images/mgl/BEvvZ/s3/2022-mercedes-c-class.jpg"
            },
            {
                "name": "Toyota Hiace",
                "description": "Reliable van perfect for business transport.",
                "price": 11000.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://toyota-africa.com/wp-content/uploads/2021/09/Hiace.png"
            },
            {
                "name": "Ford Transit",
                "description": "Spacious van with modern features for cargo or passenger use.",
                "price": 12500.0,
                "availability": True,
                "category_name": "Van",
                "image_url": "https://media.ford.com/content/fordmedia/fna/us/en/products/vans/transit/_jcr_content/image.img.jpg"
            },
            {
                "name": "Isuzu N-Series",
                "description": "Durable truck for commercial use.",
                "price": 18000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://www.isuzu.com.au/media/1553/n-series-homepage.jpg"
            },
            {
                "name": "Ford F-150",
                "description": "Powerful pickup truck with towing capabilities.",
                "price": 20000.0,
                "availability": True,
                "category_name": "Truck",
                "image_url": "https://www.ford.com/is/image/content/dam/brand_ford/en_us/brand/resources/general/new-vehicles/f150/2023/3-2/23_FRD_F15_40622.tif?croppathe=1_3x2&wid=900"
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
