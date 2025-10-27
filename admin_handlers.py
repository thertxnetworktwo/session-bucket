"""
Admin Panel Handlers for Telegram E-commerce Bot
"""

import os
import logging
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

# Import from shared module
from shared import (
    db, is_admin, ITEMS_PER_PAGE, get_country_flag,
    WAITING_COUNTRY_NAME, WAITING_COUNTRY_CODE, WAITING_PHONE_CODE, 
    WAITING_PRICE, WAITING_STOCK, WAITING_DESCRIPTION, WAITING_FILE,
    WAITING_BALANCE_AMOUNT, WAITING_USER_ID, WAITING_BROADCAST_MESSAGE,
    SESSION_FILES_DIR
)


def admin_required(func):
    """Decorator to require admin access"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("❌ Admin access required!", show_alert=True)
            else:
                await update.message.reply_text("❌ You don't have admin access!")
            return
        return await func(update, context)
    return wrapper


@admin_required
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin dashboard"""
    query = update.callback_query
    if query:
        await query.answer()
    
    # Get statistics
    total_users = await db.get_user_count()
    total_orders = await db.get_order_count(status="completed")
    orders_today = await db.get_order_count(status="completed", days=1)
    orders_week = await db.get_order_count(status="completed", days=7)
    total_revenue = await db.get_total_revenue()
    revenue_today = await db.get_total_revenue(days=1)
    revenue_week = await db.get_total_revenue(days=7)
    
    text = "👤 **Admin Dashboard**\n\n"
    text += "📊 **Statistics:**\n"
    text += f"👥 Total Users: {total_users}\n"
    text += f"📦 Total Orders: {total_orders}\n"
    text += f"   - Today: {orders_today}\n"
    text += f"   - This Week: {orders_week}\n"
    text += f"💰 Total Revenue: ${total_revenue:.2f}\n"
    text += f"   - Today: ${revenue_today:.2f}\n"
    text += f"   - This Week: ${revenue_week:.2f}\n"
    
    keyboard = [
        [InlineKeyboardButton("📦 Manage Products", callback_data="admin_products")],
        [InlineKeyboardButton("🛍️ Manage Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("👥 Manage Users", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# ==================== PRODUCT MANAGEMENT ====================

@admin_required
async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product management menu"""
    query = update.callback_query
    await query.answer()
    
    products = await db.get_all_products()
    
    text = f"📦 **Product Management**\n\nTotal Products: {len(products)}"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")],
        [InlineKeyboardButton("📋 View All Products", callback_data="admin_view_products")],
        [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_view_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all products with edit/delete options"""
    query = update.callback_query
    await query.answer()
    
    products = await db.get_all_products()
    
    if not products:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_products")]]
        await query.edit_message_text(
            "❌ No products found.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    page = int(context.user_data.get("admin_products_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_products = products[start_idx:end_idx]
    
    text = "📋 **All Products**\n\n"
    keyboard = []
    
    for product in page_products:
        flag = get_country_flag(product['country_code'])
        button_text = f"{flag} {product['country_name']} - ${product['price']:.2f} (Stock: {product['stock_quantity']})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"admin_product_{product['product_id']}")
        ])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="admin_products_prev"))
    if end_idx < len(products):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="admin_products_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_products")])
    
    text += f"Page {page + 1} of {(len(products) - 1) // ITEMS_PER_PAGE + 1}"
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product details with admin options"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[2])
    product = await db.get_product(product_id)
    
    if not product:
        await query.answer("❌ Product not found!", show_alert=True)
        return
    
    flag = get_country_flag(product['country_code'])
    text = f"📦 **Product Details**\n\n"
    text += f"{flag} **{product['country_name']}**\n"
    text += f"ID: {product['product_id']}\n"
    text += f"Country Code: {product['country_code']}\n"
    text += f"Phone Code: {product['phone_code']}\n"
    text += f"Price: ${product['price']:.2f}\n"
    text += f"Stock: {product['stock_quantity']}\n"
    text += f"Description: {product['description'] or 'N/A'}\n"
    text += f"File: {product['session_file_path'] or 'N/A'}\n"
    
    keyboard = [
        [
            InlineKeyboardButton("✏️ Edit Price", callback_data=f"admin_edit_price_{product_id}"),
            InlineKeyboardButton("📦 Edit Stock", callback_data=f"admin_edit_stock_{product_id}")
        ],
        [
            InlineKeyboardButton("📝 Edit Description", callback_data=f"admin_edit_desc_{product_id}"),
            InlineKeyboardButton("📄 Edit File", callback_data=f"admin_edit_file_{product_id}")
        ],
        [InlineKeyboardButton("🗑️ Delete Product", callback_data=f"admin_delete_product_{product_id}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="admin_view_products")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new product"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ **Add New Product**\n\nPlease enter the country name:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_COUNTRY_NAME


async def receive_country_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive country name"""
    context.user_data['new_product'] = {'country_name': update.message.text}
    
    await update.message.reply_text(
        "Please enter the country code (e.g., US, UK, CA):",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_COUNTRY_CODE


async def receive_country_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive country code"""
    context.user_data['new_product']['country_code'] = update.message.text.upper()
    
    await update.message.reply_text(
        "Please enter the phone code (e.g., +1, +44, +91):",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_PHONE_CODE


async def receive_phone_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone code"""
    context.user_data['new_product']['phone_code'] = update.message.text
    
    await update.message.reply_text(
        "Please enter the price (e.g., 9.99):",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_PRICE


async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive price"""
    try:
        price = float(update.message.text)
        context.user_data['new_product']['price'] = price
        
        await update.message.reply_text(
            "Please enter the stock quantity:",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_STOCK
    except ValueError:
        await update.message.reply_text("❌ Invalid price. Please enter a number:")
        return WAITING_PRICE


async def receive_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive stock quantity"""
    try:
        stock = int(update.message.text)
        context.user_data['new_product']['stock_quantity'] = stock
        
        await update.message.reply_text(
            "Please enter a description (or send /skip to skip):",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_DESCRIPTION
    except ValueError:
        await update.message.reply_text("❌ Invalid quantity. Please enter a number:")
        return WAITING_STOCK


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive description"""
    if update.message.text != "/skip":
        context.user_data['new_product']['description'] = update.message.text
    else:
        context.user_data['new_product']['description'] = ""
    
    await update.message.reply_text(
        "Please upload the session file (or send /skip to skip):",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_FILE


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive session file"""
    if update.message.document:
        # Create session files directory if it doesn't exist
        os.makedirs(SESSION_FILES_DIR, exist_ok=True)
        
        # Download file
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = os.path.join(SESSION_FILES_DIR, update.message.document.file_name)
        await file.download_to_drive(file_path)
        
        context.user_data['new_product']['session_file_path'] = file_path
    else:
        context.user_data['new_product']['session_file_path'] = ""
    
    # Save product
    product_data = context.user_data['new_product']
    product_id = await db.add_product(
        country_name=product_data['country_name'],
        country_code=product_data['country_code'],
        phone_code=product_data['phone_code'],
        price=product_data['price'],
        stock_quantity=product_data['stock_quantity'],
        description=product_data.get('description', ''),
        session_file_path=product_data.get('session_file_path', '')
    )
    
    if product_id:
        keyboard = [[InlineKeyboardButton("⬅️ Back to Products", callback_data="admin_products")]]
        await update.message.reply_text(
            f"✅ Product added successfully!\n\nProduct ID: {product_id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("❌ Failed to add product.")
    
    # Clear user data
    context.user_data.pop('new_product', None)
    
    return ConversationHandler.END


async def skip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip file upload"""
    return await receive_file(update, context)


@admin_required
async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a product"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[3])
    
    # Show confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Delete", callback_data=f"admin_confirm_delete_{product_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"admin_product_{product_id}")
        ]
    ]
    
    await query.edit_message_text(
        f"⚠️ Are you sure you want to delete product #{product_id}?\n\nThis action cannot be undone!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@admin_required
async def confirm_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm product deletion"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[3])
    success = await db.delete_product(product_id)
    
    if success:
        await query.answer("✅ Product deleted!", show_alert=True)
        # Redirect back to products list
        query.data = "admin_view_products"
        await admin_view_products(update, context)
    else:
        await query.answer("❌ Failed to delete product!", show_alert=True)


# ==================== ORDER MANAGEMENT ====================

@admin_required
async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show order management menu"""
    query = update.callback_query
    await query.answer()
    
    text = "🛍️ **Order Management**\n\nView and manage all orders."
    
    keyboard = [
        [InlineKeyboardButton("✅ Completed Orders", callback_data="admin_orders_completed")],
        [InlineKeyboardButton("❌ Failed Orders", callback_data="admin_orders_failed")],
        [InlineKeyboardButton("🔄 Refunded Orders", callback_data="admin_orders_refunded")],
        [InlineKeyboardButton("📋 All Orders", callback_data="admin_orders_all")],
        [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View orders by status"""
    query = update.callback_query
    await query.answer()
    
    status_map = {
        "admin_orders_completed": "completed",
        "admin_orders_failed": "failed",
        "admin_orders_refunded": "refunded",
        "admin_orders_all": None
    }
    
    status = status_map.get(query.data)
    orders = await db.get_all_orders(status)
    
    if not orders:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_orders")]]
        await query.edit_message_text(
            "❌ No orders found.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    page = int(context.user_data.get("admin_orders_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_orders = orders[start_idx:end_idx]
    
    status_text = status.upper() if status else "ALL"
    text = f"📋 **{status_text} Orders**\n\n"
    keyboard = []
    
    for order in page_orders:
        status_emoji = "✅" if order['status'] == "completed" else "❌" if order['status'] == "failed" else "🔄"
        date = datetime.fromisoformat(order['order_date']).strftime("%Y-%m-%d")
        username = order.get('username', 'N/A')
        
        button_text = f"{status_emoji} #{order['order_id']} - @{username} - ${order['total_amount']:.2f} ({date})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_order_{order['order_id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"{query.data}_prev"))
    if end_idx < len(orders):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"{query.data}_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_orders")])
    
    text += f"Page {page + 1} of {(len(orders) - 1) // ITEMS_PER_PAGE + 1}"
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show order details with admin actions"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split("_")[2])
    order = await db.get_order(order_id)
    
    if not order:
        await query.answer("❌ Order not found!", show_alert=True)
        return
    
    order_items = await db.get_order_items(order_id)
    user = await db.get_user(order['user_id'])
    
    status_emoji = "✅" if order['status'] == "completed" else "❌" if order['status'] == "failed" else "🔄"
    date = datetime.fromisoformat(order['order_date']).strftime("%Y-%m-%d %H:%M")
    
    text = f"📦 **Order #{order_id}**\n\n"
    text += f"Status: {status_emoji} {order['status'].upper()}\n"
    text += f"Date: {date}\n"
    text += f"User: @{user.get('username', 'N/A')} (ID: {order['user_id']})\n"
    text += f"Total: ${order['total_amount']:.2f}\n\n"
    text += "**Items:**\n"
    
    for item in order_items:
        flag = get_country_flag(item['country_code'])
        text += f"{flag} {item['country_name']} × {item['quantity']} = ${item['price_at_purchase'] * item['quantity']:.2f}\n"
    
    keyboard = []
    
    if order['status'] == 'completed':
        keyboard.append([InlineKeyboardButton("📥 Resend Files", callback_data=f"admin_resend_{order_id}")])
        keyboard.append([InlineKeyboardButton("🔄 Refund Order", callback_data=f"admin_refund_{order_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_orders_all")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_resend_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resend order files to user"""
    query = update.callback_query
    await query.answer("📥 Resending files...")
    
    order_id = int(query.data.split("_")[2])
    order = await db.get_order(order_id)
    
    if not order:
        await query.answer("❌ Order not found!", show_alert=True)
        return
    
    order_items = await db.get_order_items(order_id)
    
    for item in order_items:
        if item['session_file_path'] and os.path.exists(item['session_file_path']):
            flag = get_country_flag(item['country_code'])
            caption = f"{flag} {item['country_name']} - Order #{order_id} (Resent by Admin)"
            
            for _ in range(item['quantity']):
                try:
                    with open(item['session_file_path'], 'rb') as file:
                        await context.bot.send_document(
                            chat_id=order['user_id'],
                            document=file,
                            caption=caption
                        )
                except Exception as e:
                    logger.error(f"Error resending file for order {order_id}: {e}")
    
    await query.answer("✅ Files resent to user!", show_alert=True)


@admin_required
async def admin_refund_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refund an order"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split("_")[2])
    
    # Show confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Refund", callback_data=f"admin_confirm_refund_{order_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"admin_order_{order_id}")
        ]
    ]
    
    await query.edit_message_text(
        f"⚠️ Refund order #{order_id}?\n\nThis will credit the user's balance.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@admin_required
async def admin_confirm_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm order refund"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split("_")[3])
    success = await db.refund_order(order_id)
    
    if success:
        await query.answer("✅ Order refunded!", show_alert=True)
        # Show updated order details
        query.data = f"admin_order_{order_id}"
        await admin_order_details(update, context)
    else:
        await query.answer("❌ Failed to refund order!", show_alert=True)


# ==================== USER MANAGEMENT ====================

@admin_required
async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user management menu"""
    query = update.callback_query
    await query.answer()
    
    users = await db.get_all_users()
    
    text = f"👥 **User Management**\n\nTotal Users: {len(users)}"
    
    keyboard = [
        [InlineKeyboardButton("📋 View All Users", callback_data="admin_view_users")],
        [InlineKeyboardButton("💰 Adjust User Balance", callback_data="admin_adjust_balance")],
        [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all users"""
    query = update.callback_query
    await query.answer()
    
    users = await db.get_all_users()
    
    if not users:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_users")]]
        await query.edit_message_text(
            "❌ No users found.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    page = int(context.user_data.get("admin_users_page", 0))
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_users = users[start_idx:end_idx]
    
    text = "👥 **All Users**\n\n"
    keyboard = []
    
    for user in page_users:
        banned_emoji = "🚫" if user['is_banned'] else ""
        admin_emoji = "👑" if user['is_admin'] else ""
        username = user.get('username', 'N/A')
        
        button_text = f"{admin_emoji}{banned_emoji} @{username} - ${user['balance']:.2f}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_user_{user['user_id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="admin_users_prev"))
    if end_idx < len(users):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="admin_users_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_users")])
    
    text += f"Page {page + 1} of {(len(users) - 1) // ITEMS_PER_PAGE + 1}"
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user details with admin actions"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split("_")[2])
    user = await db.get_user(user_id)
    
    if not user:
        await query.answer("❌ User not found!", show_alert=True)
        return
    
    orders = await db.get_user_orders(user_id)
    total_spent = sum(order['total_amount'] for order in orders if order['status'] == 'completed')
    
    text = f"👤 **User Details**\n\n"
    text += f"ID: {user['user_id']}\n"
    text += f"Username: @{user.get('username', 'N/A')}\n"
    text += f"Name: {user.get('first_name', 'N/A')}\n"
    text += f"Balance: ${user['balance']:.2f}\n"
    text += f"Registered: {datetime.fromisoformat(user['registration_date']).strftime('%Y-%m-%d')}\n"
    text += f"Total Orders: {len(orders)}\n"
    text += f"Total Spent: ${total_spent:.2f}\n"
    text += f"Status: {'🚫 Banned' if user['is_banned'] else '✅ Active'}\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Adjust Balance", callback_data=f"admin_balance_{user_id}")],
    ]
    
    if user['is_banned']:
        keyboard.append([InlineKeyboardButton("✅ Unban User", callback_data=f"admin_unban_{user_id}")])
    else:
        keyboard.append([InlineKeyboardButton("🚫 Ban User", callback_data=f"admin_ban_{user_id}")])
    
    keyboard.append([InlineKeyboardButton("📦 View Orders", callback_data=f"admin_user_orders_{user_id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_view_users")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


@admin_required
async def admin_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split("_")[2])
    success = await db.ban_user(user_id)
    
    if success:
        await query.answer("✅ User banned!", show_alert=True)
        # Show updated user details
        query.data = f"admin_user_{user_id}"
        await admin_user_details(update, context)
    else:
        await query.answer("❌ Failed to ban user!", show_alert=True)


@admin_required
async def admin_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split("_")[2])
    success = await db.unban_user(user_id)
    
    if success:
        await query.answer("✅ User unbanned!", show_alert=True)
        # Show updated user details
        query.data = f"admin_user_{user_id}"
        await admin_user_details(update, context)
    else:
        await query.answer("❌ Failed to unban user!", show_alert=True)


# ==================== ANALYTICS ====================

@admin_required
async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show analytics and reports"""
    query = update.callback_query
    await query.answer()
    
    # Get best selling products
    best_sellers = await db.get_best_selling_products(5)
    
    text = "📊 **Analytics**\n\n"
    text += "**Best Selling Products:**\n"
    
    if best_sellers:
        for i, product in enumerate(best_sellers, 1):
            flag = get_country_flag(product['country_code'])
            text += f"{i}. {flag} {product['country_name']}\n"
            text += f"   Sold: {product['total_sold']} | Revenue: ${product['total_revenue']:.2f}\n"
    else:
        text += "No sales data available.\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


# ==================== BROADCAST ====================

@admin_required
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast message"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📢 **Broadcast Message**\n\nPlease send the message you want to broadcast to all users:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_BROADCAST_MESSAGE


async def receive_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and send broadcast message"""
    message_text = update.message.text
    
    users = await db.get_all_users()
    success_count = 0
    fail_count = 0
    
    await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    for user in users:
        if not user['is_banned']:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=f"📢 **Broadcast Message**\n\n{message_text}",
                    parse_mode=ParseMode.MARKDOWN
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user['user_id']}: {e}")
                fail_count += 1
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="admin_panel")]]
    
    await update.message.reply_text(
        f"✅ Broadcast complete!\n\nSent: {success_count}\nFailed: {fail_count}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END
