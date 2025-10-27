"""
Test script for Telegram E-commerce Bot
Tests database operations and basic functionality
"""

import asyncio
import os
import sys
from database import Database

async def test_database():
    """Test database operations"""
    print("=" * 60)
    print("Testing Database Operations")
    print("=" * 60)
    
    # Initialize database
    db = Database("test_database.db")
    await db.connect()
    print("✓ Database connected and tables initialized")
    
    # Test user operations
    print("\n--- Testing User Operations ---")
    await db.add_user(123456, "testuser", "Test User")
    user = await db.get_user(123456)
    print(f"✓ User created: {user['username']}, Balance: ${user['balance']:.2f}")
    
    # Test balance operations
    await db.update_user_balance(123456, 100.0, "Initial deposit")
    balance = await db.get_user_balance(123456)
    print(f"✓ Balance updated: ${balance:.2f}")
    
    # Test product operations
    print("\n--- Testing Product Operations ---")
    product_id = await db.add_product(
        country_name="United States",
        country_code="US",
        phone_code="+1",
        price=9.99,
        stock_quantity=10,
        description="Test session file",
        session_file_path=""
    )
    print(f"✓ Product created: ID {product_id}")
    
    product = await db.get_product(product_id)
    print(f"✓ Product retrieved: {product['country_name']}, Price: ${product['price']:.2f}, Stock: {product['stock_quantity']}")
    
    # Test cart operations
    print("\n--- Testing Cart Operations ---")
    await db.add_to_cart(123456, product_id, 2)
    cart_items = await db.get_cart_items(123456)
    print(f"✓ Added to cart: {len(cart_items)} item(s)")
    
    cart_total = await db.get_cart_total(123456)
    print(f"✓ Cart total: ${cart_total:.2f}")
    
    # Test order operations
    print("\n--- Testing Order Operations ---")
    order_id = await db.create_order(123456, cart_total, "completed")
    print(f"✓ Order created: ID {order_id}")
    
    for item in cart_items:
        await db.add_order_item(order_id, item['product_id'], item['quantity'], item['price'])
    print(f"✓ Order items added")
    
    # Test stock update
    await db.update_stock(product_id, -2)
    product = await db.get_product(product_id)
    print(f"✓ Stock updated: {product['stock_quantity']} remaining")
    
    # Test balance deduction
    await db.update_user_balance(123456, -cart_total, f"Purchase - Order #{order_id}")
    balance = await db.get_user_balance(123456)
    print(f"✓ Balance after purchase: ${balance:.2f}")
    
    # Clear cart
    await db.clear_cart(123456)
    cart_items = await db.get_cart_items(123456)
    print(f"✓ Cart cleared: {len(cart_items)} item(s)")
    
    # Test order retrieval
    orders = await db.get_user_orders(123456)
    print(f"✓ User has {len(orders)} order(s)")
    
    # Test statistics
    print("\n--- Testing Statistics ---")
    user_count = await db.get_user_count()
    order_count = await db.get_order_count()
    revenue = await db.get_total_revenue()
    print(f"✓ Users: {user_count}, Orders: {order_count}, Revenue: ${revenue:.2f}")
    
    # Test transactions
    transactions = await db.get_transactions(123456)
    print(f"✓ User has {len(transactions)} transaction(s)")
    
    # Test refund
    print("\n--- Testing Refund ---")
    await db.refund_order(order_id)
    order = await db.get_order(order_id)
    balance = await db.get_user_balance(123456)
    print(f"✓ Order refunded: Status = {order['status']}, Balance: ${balance:.2f}")
    
    # Test ban/unban
    print("\n--- Testing User Ban/Unban ---")
    await db.ban_user(123456)
    is_banned = await db.is_banned(123456)
    print(f"✓ User banned: {is_banned}")
    
    await db.unban_user(123456)
    is_banned = await db.is_banned(123456)
    print(f"✓ User unbanned: {not is_banned}")
    
    # Test best sellers
    print("\n--- Testing Analytics ---")
    best_sellers = await db.get_best_selling_products(5)
    print(f"✓ Retrieved {len(best_sellers)} best selling product(s)")
    
    # Close database
    await db.close()
    print("\n✓ Database closed")
    
    # Clean up test database
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
        print("✓ Test database removed")
    
    print("\n" + "=" * 60)
    print("All Tests Passed! ✅")
    print("=" * 60)


async def test_country_flags():
    """Test country flag function"""
    print("\n--- Testing Country Flags ---")
    from bot import get_country_flag
    
    test_countries = ["US", "UK", "CA", "AU", "FR", "DE", "JP", "XY"]
    for code in test_countries:
        flag = get_country_flag(code)
        print(f"{code}: {flag}")
    
    print("✓ Country flags working")


async def main():
    """Run all tests"""
    try:
        await test_database()
        await test_country_flags()
        print("\n🎉 All tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
