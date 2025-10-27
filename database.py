"""
Database module for Telegram E-commerce Bot
Handles all database operations using SQLite with aiosqlite for async operations
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import os

logger = logging.getLogger(__name__)


class Database:
    """Database handler for the e-commerce bot"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Establish database connection"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.initialize_tables()
        logger.info(f"Database connected: {self.db_path}")
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def initialize_tables(self):
        """Create database tables if they don't exist"""
        async with self.connection.cursor() as cursor:
            # Users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance REAL DEFAULT 0.0,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0
                )
            """)
            
            # Products table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country_name TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    phone_code TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock_quantity INTEGER DEFAULT 0,
                    description TEXT,
                    session_file_path TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Orders table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'completed',
                    payment_method TEXT DEFAULT 'balance',
                    files_delivered INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Order Items table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_at_purchase REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            # Transactions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Cart table for temporary cart items
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    UNIQUE(user_id, product_id)
                )
            """)
            
            await self.connection.commit()
            logger.info("Database tables initialized successfully")
    
    # ==================== USER OPERATIONS ====================
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Add a new user or update existing user info"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO users (user_id, username, first_name)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        first_name = excluded.first_name
                """, (user_id, username, first_name))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_balance(self, user_id: int) -> float:
        """Get user's current balance"""
        user = await self.get_user(user_id)
        return user['balance'] if user else 0.0
    
    async def update_user_balance(self, user_id: int, amount: float, description: str = "") -> bool:
        """Update user balance and log transaction"""
        try:
            async with self.connection.cursor() as cursor:
                # Update balance
                await cursor.execute("""
                    UPDATE users SET balance = balance + ? WHERE user_id = ?
                """, (amount, user_id))
                
                # Log transaction
                transaction_type = "credit" if amount > 0 else "debit"
                await cursor.execute("""
                    INSERT INTO transactions (user_id, amount, type, description)
                    VALUES (?, ?, ?, ?)
                """, (user_id, abs(amount), transaction_type, description))
                
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating balance for user {user_id}: {e}")
            await self.connection.rollback()
            return False
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        user = await self.get_user(user_id)
        return user['is_admin'] == 1 if user else False
    
    async def is_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        user = await self.get_user(user_id)
        return user['is_banned'] == 1 if user else False
    
    async def ban_user(self, user_id: int) -> bool:
        """Ban a user"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM users ORDER BY registration_date DESC")
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) as count FROM users")
                row = await cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    # ==================== PRODUCT OPERATIONS ====================
    
    async def add_product(self, country_name: str, country_code: str, phone_code: str,
                         price: float, stock_quantity: int, description: str = "",
                         session_file_path: str = "") -> Optional[int]:
        """Add a new product"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO products (country_name, country_code, phone_code, price, 
                                        stock_quantity, description, session_file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (country_name, country_code, phone_code, price, stock_quantity, 
                     description, session_file_path))
                await self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return None
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None
    
    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM products ORDER BY country_name, created_date DESC")
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            return []
    
    async def get_products_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """Get products by country code"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM products 
                    WHERE country_code = ? AND stock_quantity > 0
                    ORDER BY created_date DESC
                """, (country_code,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting products for country {country_code}: {e}")
            return []
    
    async def get_available_countries(self) -> List[Dict[str, Any]]:
        """Get list of countries with available products"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT DISTINCT country_name, country_code, phone_code
                    FROM products
                    WHERE stock_quantity > 0
                    ORDER BY country_name
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting available countries: {e}")
            return []
    
    async def update_product(self, product_id: int, **kwargs) -> bool:
        """Update product fields"""
        try:
            allowed_fields = ['country_name', 'country_code', 'phone_code', 'price', 
                            'stock_quantity', 'description', 'session_file_path']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return False
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [product_id]
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(f"UPDATE products SET {set_clause} WHERE product_id = ?", values)
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            return False
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False
    
    async def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update product stock quantity"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    UPDATE products SET stock_quantity = stock_quantity + ?
                    WHERE product_id = ?
                """, (quantity_change, product_id))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {e}")
            return False
    
    # ==================== CART OPERATIONS ====================
    
    async def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> bool:
        """Add item to cart or update quantity"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, product_id) DO UPDATE SET
                        quantity = quantity + excluded.quantity
                """, (user_id, product_id, quantity))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False
    
    async def get_cart_items(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all items in user's cart with product details"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT c.cart_id, c.user_id, c.product_id, c.quantity,
                           p.country_name, p.country_code, p.phone_code, p.price,
                           p.stock_quantity, p.description
                    FROM cart c
                    JOIN products p ON c.product_id = p.product_id
                    WHERE c.user_id = ?
                    ORDER BY c.added_date
                """, (user_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting cart items: {e}")
            return []
    
    async def update_cart_item(self, user_id: int, product_id: int, quantity: int) -> bool:
        """Update cart item quantity"""
        try:
            async with self.connection.cursor() as cursor:
                if quantity <= 0:
                    await cursor.execute("""
                        DELETE FROM cart WHERE user_id = ? AND product_id = ?
                    """, (user_id, product_id))
                else:
                    await cursor.execute("""
                        UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?
                    """, (quantity, user_id, product_id))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating cart item: {e}")
            return False
    
    async def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        """Remove item from cart"""
        return await self.update_cart_item(user_id, product_id, 0)
    
    async def clear_cart(self, user_id: int) -> bool:
        """Clear all items from user's cart"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            return False
    
    async def get_cart_total(self, user_id: int) -> float:
        """Calculate total price of items in cart"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT SUM(c.quantity * p.price) as total
                    FROM cart c
                    JOIN products p ON c.product_id = p.product_id
                    WHERE c.user_id = ?
                """, (user_id,))
                row = await cursor.fetchone()
                return row['total'] if row and row['total'] else 0.0
        except Exception as e:
            logger.error(f"Error calculating cart total: {e}")
            return 0.0
    
    # ==================== ORDER OPERATIONS ====================
    
    async def create_order(self, user_id: int, total_amount: float, status: str = "completed") -> Optional[int]:
        """Create a new order"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO orders (user_id, total_amount, status)
                    VALUES (?, ?, ?)
                """, (user_id, total_amount, status))
                await self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    async def add_order_item(self, order_id: int, product_id: int, quantity: int, price: float) -> bool:
        """Add item to order"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                    VALUES (?, ?, ?, ?)
                """, (order_id, product_id, quantity, price))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding order item: {e}")
            return False
    
    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    async def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        """Get all items in an order with product details"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT oi.*, p.country_name, p.country_code, p.phone_code, 
                           p.description, p.session_file_path
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = ?
                """, (order_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting order items: {e}")
            return []
    
    async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all orders for a user"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM orders 
                    WHERE user_id = ?
                    ORDER BY order_date DESC
                """, (user_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    async def get_all_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get all orders, optionally filtered by status"""
        try:
            async with self.connection.cursor() as cursor:
                if status:
                    await cursor.execute("""
                        SELECT o.*, u.username, u.first_name
                        FROM orders o
                        JOIN users u ON o.user_id = u.user_id
                        WHERE o.status = ?
                        ORDER BY o.order_date DESC
                    """, (status,))
                else:
                    await cursor.execute("""
                        SELECT o.*, u.username, u.first_name
                        FROM orders o
                        JOIN users u ON o.user_id = u.user_id
                        ORDER BY o.order_date DESC
                    """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all orders: {e}")
            return []
    
    async def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    UPDATE orders SET status = ? WHERE order_id = ?
                """, (status, order_id))
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    async def refund_order(self, order_id: int) -> bool:
        """Refund an order - credit user balance and update status"""
        try:
            order = await self.get_order(order_id)
            if not order:
                return False
            
            async with self.connection.cursor() as cursor:
                # Update order status
                await cursor.execute("""
                    UPDATE orders SET status = 'refunded' WHERE order_id = ?
                """, (order_id,))
                
                # Credit user balance
                await cursor.execute("""
                    UPDATE users SET balance = balance + ? WHERE user_id = ?
                """, (order['total_amount'], order['user_id']))
                
                # Log transaction
                await cursor.execute("""
                    INSERT INTO transactions (user_id, amount, type, description)
                    VALUES (?, ?, 'credit', ?)
                """, (order['user_id'], order['total_amount'], f"Refund for order #{order_id}"))
                
                await self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Error refunding order {order_id}: {e}")
            await self.connection.rollback()
            return False
    
    # ==================== STATISTICS ====================
    
    async def get_order_count(self, status: str = None, days: int = None) -> int:
        """Get order count, optionally filtered by status and time period"""
        try:
            async with self.connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM orders WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if days:
                    query += " AND order_date >= datetime('now', '-' || ? || ' days')"
                    params.append(days)
                
                await cursor.execute(query, params)
                row = await cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"Error getting order count: {e}")
            return 0
    
    async def get_total_revenue(self, days: int = None) -> float:
        """Get total revenue, optionally for a specific time period"""
        try:
            async with self.connection.cursor() as cursor:
                query = "SELECT SUM(total_amount) as revenue FROM orders WHERE status = 'completed'"
                params = []
                
                if days:
                    query += " AND order_date >= datetime('now', '-' || ? || ' days')"
                    params.append(days)
                
                await cursor.execute(query, params)
                row = await cursor.fetchone()
                return row['revenue'] if row and row['revenue'] else 0.0
        except Exception as e:
            logger.error(f"Error getting total revenue: {e}")
            return 0.0
    
    async def get_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get transaction history for a user"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM transactions 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                """, (user_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    async def get_best_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get best selling products"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT p.product_id, p.country_name, p.country_code, p.phone_code,
                           SUM(oi.quantity) as total_sold,
                           SUM(oi.quantity * oi.price_at_purchase) as total_revenue
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE o.status = 'completed'
                    GROUP BY p.product_id
                    ORDER BY total_sold DESC
                    LIMIT ?
                """, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting best selling products: {e}")
            return []
