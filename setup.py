"""
Setup script for Telegram E-commerce Bot
Creates sample data and helps with initial setup
"""

import asyncio
import os
from database import Database


async def create_sample_data():
    """Create sample products for testing"""
    print("=" * 60)
    print("Creating Sample Data")
    print("=" * 60)
    
    db = Database("bot_database.db")
    await db.connect()
    
    # Sample products data
    sample_products = [
        {
            "country_name": "United States",
            "country_code": "US",
            "phone_code": "+1",
            "price": 9.99,
            "stock_quantity": 50,
            "description": "Premium US session files with high quality accounts"
        },
        {
            "country_name": "United Kingdom",
            "country_code": "UK",
            "phone_code": "+44",
            "price": 12.99,
            "stock_quantity": 30,
            "description": "UK session files for verified accounts"
        },
        {
            "country_name": "Canada",
            "country_code": "CA",
            "phone_code": "+1",
            "price": 8.99,
            "stock_quantity": 40,
            "description": "Canadian session files with active accounts"
        },
        {
            "country_name": "Australia",
            "country_code": "AU",
            "phone_code": "+61",
            "price": 11.99,
            "stock_quantity": 25,
            "description": "Australian session files for premium accounts"
        },
        {
            "country_name": "Germany",
            "country_code": "DE",
            "phone_code": "+49",
            "price": 10.99,
            "stock_quantity": 35,
            "description": "German session files with verified profiles"
        },
        {
            "country_name": "France",
            "country_code": "FR",
            "phone_code": "+33",
            "price": 9.99,
            "stock_quantity": 30,
            "description": "French session files for active accounts"
        },
        {
            "country_name": "India",
            "country_code": "IN",
            "phone_code": "+91",
            "price": 5.99,
            "stock_quantity": 100,
            "description": "Indian session files with bulk availability"
        },
        {
            "country_name": "Japan",
            "country_code": "JP",
            "phone_code": "+81",
            "price": 13.99,
            "stock_quantity": 20,
            "description": "Japanese session files for premium accounts"
        },
    ]
    
    print("\nAdding sample products...")
    for product in sample_products:
        product_id = await db.add_product(
            country_name=product["country_name"],
            country_code=product["country_code"],
            phone_code=product["phone_code"],
            price=product["price"],
            stock_quantity=product["stock_quantity"],
            description=product["description"],
            session_file_path=""
        )
        print(f"✓ Added: {product['country_name']} (ID: {product_id})")
    
    await db.close()
    
    print("\n✅ Sample data created successfully!")
    print("=" * 60)


async def check_setup():
    """Check if setup is complete"""
    print("=" * 60)
    print("Checking Bot Setup")
    print("=" * 60)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n❌ .env file not found!")
        print("   Please copy .env.example to .env and configure it:")
        print("   cp .env.example .env")
        return False
    else:
        print("✓ .env file exists")
    
    # Check if BOT_TOKEN is set
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "your_bot_token_here":
        print("❌ BOT_TOKEN not configured in .env")
        print("   Get your bot token from @BotFather on Telegram")
        return False
    else:
        print("✓ BOT_TOKEN is configured")
    
    admin_ids = os.getenv("ADMIN_IDS")
    if not admin_ids or admin_ids == "123456789,987654321":
        print("⚠️  ADMIN_IDS not configured in .env")
        print("   Get your Telegram User ID from @userinfobot")
        print("   Add it to ADMIN_IDS in .env")
    else:
        print("✓ ADMIN_IDS is configured")
    
    # Check if session_files directory exists
    session_dir = os.getenv("SESSION_FILES_DIR", "session_files")
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        print(f"✓ Created {session_dir} directory")
    else:
        print(f"✓ {session_dir} directory exists")
    
    print("\n✅ Setup check complete!")
    print("=" * 60)
    return True


async def main():
    """Main setup function"""
    print("\n🚀 Telegram E-commerce Bot Setup")
    print()
    
    # Check setup
    setup_ok = await check_setup()
    
    if not setup_ok:
        print("\n⚠️  Please complete the setup steps above before running the bot.")
        return
    
    # Ask if user wants sample data
    print("\nWould you like to create sample product data? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        await create_sample_data()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\nYou can now start the bot with:")
    print("  python bot.py")
    print("\nFor testing, you can run:")
    print("  python test_bot.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
