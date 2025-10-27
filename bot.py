"""
Telegram E-commerce Bot for Session Files
Main bot file with user and admin handlers
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
from dotenv import load_dotenv
import asyncio

from database import Database

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
SESSION_FILES_DIR = os.getenv("SESSION_FILES_DIR", "session_files")
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "5"))

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "bot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database(os.getenv("DATABASE_URL", "bot_database.db").replace("sqlite:///", ""))

# Conversation states
(WAITING_COUNTRY_NAME, WAITING_COUNTRY_CODE, WAITING_PHONE_CODE, WAITING_PRICE,
 WAITING_STOCK, WAITING_DESCRIPTION, WAITING_FILE, WAITING_PRODUCT_EDIT,
 WAITING_BALANCE_AMOUNT, WAITING_USER_ID, WAITING_BROADCAST_MESSAGE) = range(11)

# Country flag emojis mapping
COUNTRY_FLAGS = {
    "US": "🇺🇸", "UK": "🇬🇧", "CA": "🇨🇦", "AU": "🇦🇺", "DE": "🇩🇪",
    "FR": "🇫🇷", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷", "IN": "🇮🇳",
    "CN": "🇨🇳", "JP": "🇯🇵", "KR": "🇰🇷", "RU": "🇷🇺", "MX": "🇲🇽",
    "NL": "🇳🇱", "SE": "🇸🇪", "NO": "🇳🇴", "FI": "🇫🇮", "DK": "🇩🇰",
    "PL": "🇵🇱", "TR": "🇹🇷", "SA": "🇸🇦", "AE": "🇦🇪", "SG": "🇸🇬",
}


def get_country_flag(country_code: str) -> str:
    """Get flag emoji for country code"""
    return COUNTRY_FLAGS.get(country_code.upper(), "🌍")


async def ensure_user_exists(update: Update) -> bool:
    """Ensure user exists in database and is not banned"""
    user = update.effective_user
    if not user:
        return False
    
    # Check if user is banned
    if await db.is_banned(user.id):
        await update.message.reply_text("❌ You have been banned from using this bot.")
        return False
    
    # Add or update user
    await db.add_user(user.id, user.username, user.first_name)
    return True


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


# ==================== USER HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show main menu"""
    if not await ensure_user_exists(update):
        return
    
    user = update.effective_user
    await show_main_menu(update, context, f"Welcome {user.first_name}! 👋\n\nWhat would you like to do?")


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str = None):
    """Display main menu"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")],
        [InlineKeyboardButton("🛒 My Cart", callback_data="view_cart")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("💳 Balance & Payment", callback_data="balance")],
        [InlineKeyboardButton("ℹ️ Help & Support", callback_data="help")],
    ]
    
    if is_admin(update.effective_user.id):
        keyboard.append([InlineKeyboardButton("👤 Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = message or "🏠 Main Menu\n\nWhat would you like to do?"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def browse_products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available countries"""
    query = update.callback_query
    await query.answer()
    
    countries = await db.get_available_countries()
    
    if not countries:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
        await query.edit_message_text(
            "❌ No products available at the moment.\n\nPlease check back later!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Paginate countries
    page = int(context.user_data.get("country_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_countries = countries[start_idx:end_idx]
    
    keyboard = []
    for country in page_countries:
        flag = get_country_flag(country['country_code'])
        button_text = f"{country['phone_code']} {flag} {country['country_name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"country_{country['country_code']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data="countries_prev"))
    if end_idx < len(countries):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="countries_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    
    text = f"🌍 Browse Products by Country\n\nPage {page + 1} of {(len(countries) - 1) // ITEMS_PER_PAGE + 1}"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_country_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show products for selected country"""
    query = update.callback_query
    await query.answer()
    
    country_code = query.data.split("_")[1]
    products = await db.get_products_by_country(country_code)
    
    if not products:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="browse_products")]]
        await query.edit_message_text(
            "❌ No products available for this country.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Store country code for pagination
    context.user_data['current_country'] = country_code
    page = int(context.user_data.get("product_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_products = products[start_idx:end_idx]
    
    keyboard = []
    for product in page_products:
        flag = get_country_flag(product['country_code'])
        button_text = f"{flag} {product['country_name']} - ${product['price']:.2f} (Stock: {product['stock_quantity']})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"product_{product['product_id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data="products_prev"))
    if end_idx < len(products):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="products_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="browse_products")])
    
    flag = get_country_flag(country_code)
    text = f"{flag} Products for {products[0]['country_name']}\n\nPage {page + 1} of {(len(products) - 1) // ITEMS_PER_PAGE + 1}"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed product information"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    product = await db.get_product(product_id)
    
    if not product:
        await query.edit_message_text("❌ Product not found.")
        return
    
    flag = get_country_flag(product['country_code'])
    text = f"{flag} **{product['country_name']}**\n\n"
    text += f"📞 Phone Code: {product['phone_code']}\n"
    text += f"💰 Price: ${product['price']:.2f}\n"
    text += f"📦 Available: {product['stock_quantity']} items\n\n"
    text += f"📝 Description:\n{product['description'] or 'No description available.'}"
    
    keyboard = []
    if product['stock_quantity'] > 0:
        keyboard.append([InlineKeyboardButton("➕ Add to Cart", callback_data=f"add_to_cart_{product_id}")])
    else:
        text += "\n\n❌ **Out of Stock**"
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"country_{product['country_code']}")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add product to cart"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[3])
    user_id = update.effective_user.id
    
    product = await db.get_product(product_id)
    if not product or product['stock_quantity'] <= 0:
        await query.answer("❌ Product is out of stock!", show_alert=True)
        return
    
    success = await db.add_to_cart(user_id, product_id, 1)
    
    if success:
        await query.answer("✅ Added to cart!", show_alert=True)
        # Show updated product details
        await show_product_details(update, context)
    else:
        await query.answer("❌ Failed to add to cart.", show_alert=True)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show cart contents"""
    query = update.callback_query
    if query:
        await query.answer()
    
    user_id = update.effective_user.id
    cart_items = await db.get_cart_items(user_id)
    
    if not cart_items:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
        text = "🛒 Your cart is empty!\n\nBrowse products to add items."
        
        if query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    total = 0
    text = "🛒 **Your Cart**\n\n"
    
    keyboard = []
    for item in cart_items:
        flag = get_country_flag(item['country_code'])
        item_total = item['price'] * item['quantity']
        total += item_total
        
        text += f"{flag} {item['country_name']}\n"
        text += f"   Qty: {item['quantity']} × ${item['price']:.2f} = ${item_total:.2f}\n\n"
        
        # Add quantity adjustment buttons
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"cart_dec_{item['product_id']}"),
            InlineKeyboardButton(f"{item['country_name'][:20]}", callback_data=f"cart_view_{item['product_id']}"),
            InlineKeyboardButton("➕", callback_data=f"cart_inc_{item['product_id']}"),
        ])
    
    text += f"💰 **Total: ${total:.2f}**"
    
    # Action buttons
    keyboard.append([
        InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart"),
        InlineKeyboardButton("💳 Checkout", callback_data="checkout")
    ])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def cart_adjust_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adjust cart item quantity"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    action = parts[1]  # inc or dec
    product_id = int(parts[2])
    user_id = update.effective_user.id
    
    cart_items = await db.get_cart_items(user_id)
    current_item = next((item for item in cart_items if item['product_id'] == product_id), None)
    
    if not current_item:
        await query.answer("❌ Item not found in cart!", show_alert=True)
        return
    
    new_quantity = current_item['quantity']
    if action == "inc":
        product = await db.get_product(product_id)
        if product and new_quantity < product['stock_quantity']:
            new_quantity += 1
        else:
            await query.answer("❌ Not enough stock!", show_alert=True)
            return
    elif action == "dec":
        new_quantity -= 1
    
    await db.update_cart_item(user_id, product_id, new_quantity)
    await view_cart(update, context)


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all items from cart"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    await db.clear_cart(user_id)
    
    await query.answer("🗑️ Cart cleared!", show_alert=True)
    await view_cart(update, context)


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process checkout and deliver files instantly"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    cart_items = await db.get_cart_items(user_id)
    
    if not cart_items:
        await query.answer("❌ Your cart is empty!", show_alert=True)
        return
    
    # Calculate total
    total = await db.get_cart_total(user_id)
    balance = await db.get_user_balance(user_id)
    
    # Check balance
    if balance < total:
        keyboard = [
            [InlineKeyboardButton("💳 Add Balance", callback_data="balance")],
            [InlineKeyboardButton("⬅️ Back to Cart", callback_data="view_cart")]
        ]
        text = f"❌ Insufficient balance!\n\n"
        text += f"Cart Total: ${total:.2f}\n"
        text += f"Your Balance: ${balance:.2f}\n"
        text += f"Need: ${total - balance:.2f} more"
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Check stock availability
    for item in cart_items:
        product = await db.get_product(item['product_id'])
        if not product or product['stock_quantity'] < item['quantity']:
            await query.answer(f"❌ {item['country_name']} is out of stock!", show_alert=True)
            await view_cart(update, context)
            return
    
    try:
        # Create order
        order_id = await db.create_order(user_id, total, "completed")
        
        if not order_id:
            await query.answer("❌ Failed to create order!", show_alert=True)
            return
        
        # Add order items and update stock
        for item in cart_items:
            await db.add_order_item(order_id, item['product_id'], item['quantity'], item['price'])
            await db.update_stock(item['product_id'], -item['quantity'])
        
        # Deduct balance
        await db.update_user_balance(user_id, -total, f"Purchase - Order #{order_id}")
        
        # Clear cart
        await db.clear_cart(user_id)
        
        # Send files immediately
        text = f"✅ **Order #{order_id} Completed!**\n\n"
        text += f"Total Paid: ${total:.2f}\n"
        text += f"Remaining Balance: ${balance - total:.2f}\n\n"
        text += "📦 **Your Session Files:**\n"
        
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        
        # Send each file
        order_items = await db.get_order_items(order_id)
        for item in order_items:
            if item['session_file_path'] and os.path.exists(item['session_file_path']):
                flag = get_country_flag(item['country_code'])
                caption = f"{flag} {item['country_name']} - Qty: {item['quantity']}"
                
                for _ in range(item['quantity']):
                    try:
                        with open(item['session_file_path'], 'rb') as file:
                            await context.bot.send_document(
                                chat_id=user_id,
                                document=file,
                                caption=caption
                            )
                    except Exception as e:
                        logger.error(f"Error sending file for order {order_id}: {e}")
        
        # Show success message with options
        keyboard = [
            [InlineKeyboardButton("📦 View Orders", callback_data="my_orders")],
            [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="browse_products")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ All files delivered successfully!\n\nYou can re-download them anytime from My Orders.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        await query.answer("❌ Checkout failed! Please try again.", show_alert=True)


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's order history"""
    query = update.callback_query
    if query:
        await query.answer()
    
    user_id = update.effective_user.id
    orders = await db.get_user_orders(user_id)
    
    if not orders:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
        text = "📦 You haven't placed any orders yet.\n\nStart shopping to see your orders here!"
        
        if query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    page = int(context.user_data.get("orders_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_orders = orders[start_idx:end_idx]
    
    text = "📦 **Your Orders**\n\n"
    keyboard = []
    
    for order in page_orders:
        status_emoji = "✅" if order['status'] == "completed" else "❌" if order['status'] == "failed" else "🔄"
        date = datetime.fromisoformat(order['order_date']).strftime("%Y-%m-%d %H:%M")
        
        button_text = f"{status_emoji} Order #{order['order_id']} - ${order['total_amount']:.2f} ({date})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"order_details_{order['order_id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data="orders_prev"))
    if end_idx < len(orders):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="orders_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    
    text += f"Page {page + 1} of {(len(orders) - 1) // ITEMS_PER_PAGE + 1}"
    
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show order details and re-download option"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split("_")[2])
    order = await db.get_order(order_id)
    
    if not order:
        await query.answer("❌ Order not found!", show_alert=True)
        return
    
    order_items = await db.get_order_items(order_id)
    
    status_emoji = "✅" if order['status'] == "completed" else "❌" if order['status'] == "failed" else "🔄"
    date = datetime.fromisoformat(order['order_date']).strftime("%Y-%m-%d %H:%M")
    
    text = f"📦 **Order #{order_id}**\n\n"
    text += f"Status: {status_emoji} {order['status'].upper()}\n"
    text += f"Date: {date}\n"
    text += f"Total: ${order['total_amount']:.2f}\n\n"
    text += "**Items:**\n"
    
    for item in order_items:
        flag = get_country_flag(item['country_code'])
        text += f"{flag} {item['country_name']} × {item['quantity']} = ${item['price_at_purchase'] * item['quantity']:.2f}\n"
    
    keyboard = []
    if order['status'] == 'completed':
        keyboard.append([InlineKeyboardButton("📥 Re-download Files", callback_data=f"redownload_{order_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="my_orders")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def redownload_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Re-download files from a completed order"""
    query = update.callback_query
    await query.answer("📥 Sending files...")
    
    order_id = int(query.data.split("_")[1])
    user_id = update.effective_user.id
    
    order = await db.get_order(order_id)
    if not order or order['user_id'] != user_id:
        await query.answer("❌ Order not found!", show_alert=True)
        return
    
    order_items = await db.get_order_items(order_id)
    
    for item in order_items:
        if item['session_file_path'] and os.path.exists(item['session_file_path']):
            flag = get_country_flag(item['country_code'])
            caption = f"{flag} {item['country_name']} - Order #{order_id}"
            
            for _ in range(item['quantity']):
                try:
                    with open(item['session_file_path'], 'rb') as file:
                        await context.bot.send_document(
                            chat_id=user_id,
                            document=file,
                            caption=caption
                        )
                except Exception as e:
                    logger.error(f"Error re-sending file for order {order_id}: {e}")
    
    await query.answer("✅ Files sent!", show_alert=True)


async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show balance and payment options"""
    query = update.callback_query
    if query:
        await query.answer()
    
    user_id = update.effective_user.id
    balance = await db.get_user_balance(user_id)
    
    text = f"💳 **Your Balance**\n\n"
    text += f"Current Balance: ${balance:.2f}"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton("📜 Transaction History", callback_data="transactions")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ]
    
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def add_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show payment instructions"""
    query = update.callback_query
    await query.answer()
    
    text = "💳 **Add Balance**\n\n"
    text += "To add balance to your account, please contact an administrator.\n\n"
    text += "Send your payment details and the administrator will credit your account.\n\n"
    text += "📧 Contact: @admin (replace with actual contact)"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="balance")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def transactions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show transaction history"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    transactions = await db.get_transactions(user_id)
    
    if not transactions:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="balance")]]
        await query.edit_message_text(
            "📜 No transactions yet.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    text = "📜 **Transaction History**\n\n"
    
    # Show last 10 transactions
    for trans in transactions[:10]:
        date = datetime.fromisoformat(trans['timestamp']).strftime("%Y-%m-%d %H:%M")
        sign = "+" if trans['type'] == "credit" else "-"
        text += f"{date}\n{sign}${trans['amount']:.2f} - {trans['description']}\n\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="balance")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help and support information"""
    query = update.callback_query
    if query:
        await query.answer()
    
    text = "ℹ️ **Help & Support**\n\n"
    text += "**How to use this bot:**\n\n"
    text += "1️⃣ Browse products by country\n"
    text += "2️⃣ Add items to your cart\n"
    text += "3️⃣ Checkout and pay with your balance\n"
    text += "4️⃣ Receive files instantly after payment\n"
    text += "5️⃣ Re-download files anytime from My Orders\n\n"
    text += "**Need help?**\n"
    text += "Contact support: @admin (replace with actual contact)\n\n"
    text += "**Payment:**\n"
    text += "Add balance through an administrator and use it to purchase session files."
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
    
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


# ==================== PAGINATION HANDLERS ====================

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination for various lists"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("countries_"):
        direction = data.split("_")[1]
        current_page = int(context.user_data.get("country_page", 0))
        context.user_data["country_page"] = current_page + 1 if direction == "next" else current_page - 1
        await browse_products_handler(update, context)
    
    elif data.startswith("products_"):
        direction = data.split("_")[1]
        current_page = int(context.user_data.get("product_page", 0))
        context.user_data["product_page"] = current_page + 1 if direction == "next" else current_page - 1
        country_code = context.user_data.get('current_country')
        if country_code:
            # Reconstruct callback to show products
            query.data = f"country_{country_code}"
            await show_country_products(update, context)
    
    elif data.startswith("orders_"):
        direction = data.split("_")[1]
        current_page = int(context.user_data.get("orders_page", 0))
        context.user_data["orders_page"] = current_page + 1 if direction == "next" else current_page - 1
        await my_orders(update, context)


# ==================== ADMIN HANDLERS IMPORT ====================

# Import admin handlers
from admin_handlers import (
    admin_panel, admin_products, admin_view_products, admin_product_details,
    start_add_product, receive_country_name, receive_country_code, receive_phone_code,
    receive_price, receive_stock, receive_description, receive_file, skip_file,
    delete_product, confirm_delete_product,
    admin_orders, admin_view_orders, admin_order_details, admin_resend_files,
    admin_refund_order, admin_confirm_refund,
    admin_users, admin_view_users, admin_user_details, admin_ban_user, admin_unban_user,
    admin_analytics, start_broadcast, receive_broadcast_message
)


# ==================== CALLBACK QUERY ROUTER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route callback queries to appropriate handlers"""
    query = update.callback_query
    data = query.data
    
    # Main menu
    if data == "main_menu":
        await show_main_menu(update, context)
    
    # User handlers
    elif data == "browse_products":
        await browse_products_handler(update, context)
    elif data.startswith("country_"):
        await show_country_products(update, context)
    elif data.startswith("product_"):
        await show_product_details(update, context)
    elif data.startswith("add_to_cart_"):
        await add_to_cart(update, context)
    elif data == "view_cart":
        await view_cart(update, context)
    elif data.startswith("cart_inc_") or data.startswith("cart_dec_"):
        await cart_adjust_quantity(update, context)
    elif data == "clear_cart":
        await clear_cart(update, context)
    elif data == "checkout":
        await checkout(update, context)
    elif data == "my_orders":
        await my_orders(update, context)
    elif data.startswith("order_details_"):
        await order_details(update, context)
    elif data.startswith("redownload_"):
        await redownload_files(update, context)
    elif data == "balance":
        await balance_handler(update, context)
    elif data == "add_balance":
        await add_balance_handler(update, context)
    elif data == "transactions":
        await transactions_handler(update, context)
    elif data == "help":
        await help_handler(update, context)
    
    # Pagination
    elif data.startswith("countries_") or data.startswith("products_") or data.startswith("orders_"):
        await handle_pagination(update, context)
    
    # Admin handlers
    elif data == "admin_panel":
        await admin_panel(update, context)
    elif data == "admin_products":
        await admin_products(update, context)
    elif data == "admin_view_products":
        await admin_view_products(update, context)
    elif data.startswith("admin_product_"):
        await admin_product_details(update, context)
    elif data.startswith("admin_delete_product_"):
        await delete_product(update, context)
    elif data.startswith("admin_confirm_delete_"):
        await confirm_delete_product(update, context)
    elif data == "admin_orders":
        await admin_orders(update, context)
    elif data.startswith("admin_orders_"):
        await admin_view_orders(update, context)
    elif data.startswith("admin_order_"):
        await admin_order_details(update, context)
    elif data.startswith("admin_resend_"):
        await admin_resend_files(update, context)
    elif data.startswith("admin_refund_"):
        await admin_refund_order(update, context)
    elif data.startswith("admin_confirm_refund_"):
        await admin_confirm_refund(update, context)
    elif data == "admin_users":
        await admin_users(update, context)
    elif data == "admin_view_users":
        await admin_view_users(update, context)
    elif data.startswith("admin_user_"):
        await admin_user_details(update, context)
    elif data.startswith("admin_ban_"):
        await admin_ban_user(update, context)
    elif data.startswith("admin_unban_"):
        await admin_unban_user(update, context)
    elif data == "admin_analytics":
        await admin_analytics(update, context)
    elif data == "admin_broadcast":
        await start_broadcast(update, context)
    elif data == "admin_add_product":
        await start_add_product(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END


# ==================== MAIN FUNCTION ====================

async def post_init(application: Application):
    """Initialize database connection after application starts"""
    await db.connect()
    logger.info("Bot initialized successfully")


async def post_shutdown(application: Application):
    """Close database connection before application stops"""
    await db.close()
    logger.info("Bot shutdown complete")


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    # Add conversation handler for adding products
    add_product_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_product, pattern="^admin_add_product$")],
        states={
            WAITING_COUNTRY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_country_name)],
            WAITING_COUNTRY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_country_code)],
            WAITING_PHONE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone_code)],
            WAITING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price)],
            WAITING_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_stock)],
            WAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description),
                CommandHandler("skip", receive_description)
            ],
            WAITING_FILE: [
                MessageHandler(filters.Document.ALL, receive_file),
                CommandHandler("skip", skip_file),
                MessageHandler(filters.TEXT & ~filters.COMMAND, skip_file)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add conversation handler for broadcast
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_broadcast, pattern="^admin_broadcast$")],
        states={
            WAITING_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_product_conv)
    application.add_handler(broadcast_conv)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
