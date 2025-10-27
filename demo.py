"""
Demo script - Shows what the bot can do without requiring Telegram connection
This is useful for understanding the bot's features and testing database operations
"""

import asyncio
import os
from datetime import datetime
from database import Database


async def demo():
    """Demonstrate bot functionality"""
    print("\n" + "=" * 70)
    print(" " * 15 + "TELEGRAM E-COMMERCE BOT DEMO")
    print("=" * 70)
    
    # Initialize database
    db = Database("demo_database.db")
    await db.connect()
    print("\n✓ Database initialized")
    
    # Simulate admin adding products
    print("\n" + "-" * 70)
    print("ADMIN: Adding Products")
    print("-" * 70)
    
    products_data = [
        ("United States", "US", "+1", 9.99, 50),
        ("United Kingdom", "UK", "+44", 12.99, 30),
        ("Canada", "CA", "+1", 8.99, 40),
        ("Australia", "AU", "+61", 11.99, 25),
        ("Germany", "DE", "+49", 10.99, 35),
    ]
    
    for country_name, code, phone, price, stock in products_data:
        product_id = await db.add_product(
            country_name=country_name,
            country_code=code,
            phone_code=phone,
            price=price,
            stock_quantity=stock,
            description=f"{country_name} session files"
        )
        print(f"  Added: {phone} {country_name} - ${price:.2f} (Stock: {stock})")
    
    # Simulate user registration
    print("\n" + "-" * 70)
    print("USER: Registration")
    print("-" * 70)
    
    user_id = 123456
    await db.add_user(user_id, "demouser", "Demo User")
    user = await db.get_user(user_id)
    print(f"  Welcome {user['first_name']}!")
    print(f"  Username: @{user['username']}")
    print(f"  Balance: ${user['balance']:.2f}")
    
    # Admin adds balance
    print("\n" + "-" * 70)
    print("ADMIN: Adding balance to user")
    print("-" * 70)
    
    await db.update_user_balance(user_id, 100.0, "Admin deposit")
    balance = await db.get_user_balance(user_id)
    print(f"  ${balance:.2f} added to account")
    print(f"  New balance: ${balance:.2f}")
    
    # User browses products
    print("\n" + "-" * 70)
    print("USER: Browsing Products")
    print("-" * 70)
    
    countries = await db.get_available_countries()
    print(f"  Available countries: {len(countries)}")
    for country in countries:
        print(f"    {country['phone_code']} {country['country_name']}")
    
    # User selects US products
    print("\n  Viewing US products...")
    us_products = await db.get_products_by_country("US")
    for product in us_products:
        print(f"    Product #{product['product_id']}: ${product['price']:.2f} (Stock: {product['stock_quantity']})")
    
    # User adds to cart
    print("\n" + "-" * 70)
    print("USER: Adding items to cart")
    print("-" * 70)
    
    # Add 2 US products and 1 UK product
    await db.add_to_cart(user_id, 1, 2)  # 2x US @ $9.99
    await db.add_to_cart(user_id, 2, 1)  # 1x UK @ $12.99
    
    cart_items = await db.get_cart_items(user_id)
    cart_total = await db.get_cart_total(user_id)
    
    print(f"  Cart items:")
    for item in cart_items:
        print(f"    {item['country_name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}")
    print(f"\n  Cart Total: ${cart_total:.2f}")
    
    # User checks out
    print("\n" + "-" * 70)
    print("USER: Checkout")
    print("-" * 70)
    
    balance = await db.get_user_balance(user_id)
    print(f"  Balance: ${balance:.2f}")
    print(f"  Cart Total: ${cart_total:.2f}")
    
    if balance >= cart_total:
        print("  ✓ Sufficient balance!")
        
        # Create order
        order_id = await db.create_order(user_id, cart_total, "completed")
        print(f"\n  Order #{order_id} created")
        
        # Add order items and update stock
        for item in cart_items:
            await db.add_order_item(order_id, item['product_id'], item['quantity'], item['price'])
            await db.update_stock(item['product_id'], -item['quantity'])
        
        # Deduct balance
        await db.update_user_balance(user_id, -cart_total, f"Purchase - Order #{order_id}")
        
        # Clear cart
        await db.clear_cart(user_id)
        
        new_balance = await db.get_user_balance(user_id)
        print(f"  Balance deducted: ${cart_total:.2f}")
        print(f"  New balance: ${new_balance:.2f}")
        print(f"  Files delivered instantly! ✅")
    
    # View order history
    print("\n" + "-" * 70)
    print("USER: Order History")
    print("-" * 70)
    
    orders = await db.get_user_orders(user_id)
    for order in orders:
        print(f"  Order #{order['order_id']}")
        print(f"    Date: {datetime.fromisoformat(order['order_date']).strftime('%Y-%m-%d %H:%M')}")
        print(f"    Total: ${order['total_amount']:.2f}")
        print(f"    Status: {order['status']}")
        
        order_items = await db.get_order_items(order['order_id'])
        print(f"    Items:")
        for item in order_items:
            print(f"      - {item['country_name']} x{item['quantity']}")
    
    # Admin views statistics
    print("\n" + "-" * 70)
    print("ADMIN: Dashboard Statistics")
    print("-" * 70)
    
    total_users = await db.get_user_count()
    total_orders = await db.get_order_count(status="completed")
    total_revenue = await db.get_total_revenue()
    
    print(f"  Total Users: {total_users}")
    print(f"  Total Orders: {total_orders}")
    print(f"  Total Revenue: ${total_revenue:.2f}")
    
    # Admin views best sellers
    print("\n  Best Selling Products:")
    best_sellers = await db.get_best_selling_products(3)
    for i, product in enumerate(best_sellers, 1):
        print(f"    {i}. {product['country_name']}: {product['total_sold']} sold (${product['total_revenue']:.2f})")
    
    # Simulate a refund
    print("\n" + "-" * 70)
    print("ADMIN: Processing Refund")
    print("-" * 70)
    
    print(f"  Refunding Order #{order_id}")
    await db.refund_order(order_id)
    
    order = await db.get_order(order_id)
    balance = await db.get_user_balance(user_id)
    
    print(f"  Order status: {order['status']}")
    print(f"  User balance: ${balance:.2f}")
    print(f"  Refund completed! ✅")
    
    # View transactions
    print("\n" + "-" * 70)
    print("USER: Transaction History")
    print("-" * 70)
    
    transactions = await db.get_transactions(user_id)
    for trans in transactions:
        sign = "+" if trans['type'] == "credit" else "-"
        date = datetime.fromisoformat(trans['timestamp']).strftime('%Y-%m-%d %H:%M')
        print(f"  {date}: {sign}${trans['amount']:.2f} - {trans['description']}")
    
    # Close database
    await db.close()
    
    # Clean up demo database
    if os.path.exists("demo_database.db"):
        os.remove("demo_database.db")
    
    print("\n" + "=" * 70)
    print(" " * 25 + "DEMO COMPLETE!")
    print("=" * 70)
    print("\nThis demonstrates the bot's core functionality:")
    print("  ✓ Product management (add, view, stock tracking)")
    print("  ✓ User registration and balance management")
    print("  ✓ Shopping cart and checkout process")
    print("  ✓ Instant order fulfillment and file delivery")
    print("  ✓ Order history and re-download capability")
    print("  ✓ Refund processing")
    print("  ✓ Transaction tracking")
    print("  ✓ Admin statistics and analytics")
    print("\nTo run the actual bot, configure .env and run: python bot.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
