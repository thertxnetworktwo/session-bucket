# Telegram E-commerce Bot for Session Files

A comprehensive Telegram bot for selling session files with complete user and admin functionality, instant payment processing, and automatic file delivery.

## Features

### User Features
- 🛍️ **Browse Products by Country** - Organized by phone codes with country flags
- 🛒 **Shopping Cart** - Add, remove, and adjust quantities
- 💳 **Instant Checkout** - Automatic balance deduction and immediate file delivery
- 📦 **Order History** - View past orders and re-download files anytime
- 💰 **Balance Management** - Check balance and transaction history
- ℹ️ **Help & Support** - Built-in help system

### Admin Features
- 👤 **Admin Dashboard** - Quick overview of statistics (users, orders, revenue)
- 📦 **Product Management** - Add, edit, delete products with file uploads
- 🛍️ **Order Management** - View, refund, and resend files for orders
- 👥 **User Management** - View users, adjust balances, ban/unban users
- 📊 **Analytics** - Best-selling products and sales statistics
- 📢 **Broadcast** - Send messages to all users

### Technical Features
- ⚡ **Instant Order Fulfillment** - No pending status, immediate delivery
- 🔒 **Secure** - Admin authentication, input validation, error handling
- 📊 **Database** - SQLite with comprehensive data persistence
- 🔄 **Pagination** - Efficient browsing for large lists
- 📝 **Logging** - Comprehensive logging for debugging and monitoring
- 🌍 **Country Flags** - Emoji flags for better UX

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Admin Telegram User ID(s)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/thertxnetworktwo/session-bucket.git
cd session-bucket
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Admin Configuration (comma-separated Telegram user IDs)
ADMIN_IDS=123456789,987654321

# Database Configuration
DATABASE_URL=sqlite:///bot_database.db

# File Storage
SESSION_FILES_DIR=session_files

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Bot Settings
MAX_CART_ITEMS=50
ITEMS_PER_PAGE=5
```

4. **Get your Telegram User ID**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram to get your User ID
   - Add your User ID to `ADMIN_IDS` in `.env`

5. **Create session files directory**
```bash
mkdir session_files
```

6. **Run the bot**
```bash
python bot.py
```

## Usage

### For Users

1. **Start the bot**: Send `/start` to the bot
2. **Browse Products**: Click "🛍️ Browse Products" and select a country
3. **Add to Cart**: View product details and add items to cart
4. **Checkout**: Review cart and click "💳 Checkout"
5. **Receive Files**: Files are delivered instantly after successful payment
6. **Re-download**: Access past orders anytime from "📦 My Orders"

### For Admins

1. **Access Admin Panel**: Click "👤 Admin Panel" from the main menu
2. **Add Products**:
   - Go to "📦 Manage Products" → "➕ Add Product"
   - Follow the prompts to enter product details
   - Upload session file when requested
3. **Manage Orders**: View all orders, refund if needed, resend files
4. **Manage Users**: Adjust balances, ban/unban users
5. **View Analytics**: See best-selling products and sales statistics
6. **Broadcast Messages**: Send announcements to all users

## Database Schema

### Users Table
- `user_id` (PRIMARY KEY) - Telegram user ID
- `username` - Telegram username
- `first_name` - User's first name
- `balance` - User's current balance
- `registration_date` - When user first started the bot
- `is_banned` - Ban status (0 or 1)
- `is_admin` - Admin status (0 or 1)

### Products Table
- `product_id` (PRIMARY KEY) - Auto-increment ID
- `country_name` - Country name
- `country_code` - ISO country code (US, UK, etc.)
- `phone_code` - Phone code (+1, +44, etc.)
- `price` - Product price
- `stock_quantity` - Available quantity
- `description` - Product description
- `session_file_path` - Path to session file
- `created_date` - When product was added

### Orders Table
- `order_id` (PRIMARY KEY) - Auto-increment ID
- `user_id` (FOREIGN KEY) - References users.user_id
- `order_date` - When order was placed
- `total_amount` - Order total
- `status` - completed, failed, or refunded
- `payment_method` - Payment method used (default: balance)
- `files_delivered` - Whether files were delivered (0 or 1)

### Order Items Table
- `item_id` (PRIMARY KEY) - Auto-increment ID
- `order_id` (FOREIGN KEY) - References orders.order_id
- `product_id` (FOREIGN KEY) - References products.product_id
- `quantity` - Number of items ordered
- `price_at_purchase` - Price at time of purchase

### Transactions Table
- `transaction_id` (PRIMARY KEY) - Auto-increment ID
- `user_id` (FOREIGN KEY) - References users.user_id
- `amount` - Transaction amount
- `type` - credit or debit
- `description` - Transaction description
- `timestamp` - When transaction occurred

### Cart Table
- `cart_id` (PRIMARY KEY) - Auto-increment ID
- `user_id` (FOREIGN KEY) - References users.user_id
- `product_id` (FOREIGN KEY) - References products.product_id
- `quantity` - Number of items in cart
- `added_date` - When item was added

## Project Structure

```
session-bucket/
├── bot.py                  # Main bot file with user handlers
├── admin_handlers.py       # Admin panel handlers
├── database.py             # Database operations
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── README.md              # This file
├── session_files/         # Directory for session files (created at runtime)
└── bot_database.db        # SQLite database (created at runtime)
```

## Security Considerations

- **Admin Authentication**: Only users with IDs in `ADMIN_IDS` can access admin features
- **Input Validation**: All user inputs are validated before processing
- **Error Handling**: Comprehensive error handling prevents crashes
- **Database Transactions**: Atomic operations ensure data consistency
- **File Security**: Session files stored outside web-accessible directories
- **No Hardcoded Credentials**: All sensitive data in environment variables

## Testing Checklist

- [x] User registration and main menu navigation
- [x] Product browsing by country with pagination
- [x] Add to cart functionality
- [x] Cart quantity adjustment
- [x] Checkout with balance validation
- [x] Instant file delivery after payment
- [x] Stock quantity auto-update
- [x] Order history and re-download
- [x] Balance and transaction display
- [x] Admin panel authentication
- [x] Product CRUD operations
- [x] Order refund functionality
- [x] File resending
- [x] User management (ban/unban)
- [x] Balance adjustment
- [x] Broadcast messaging
- [x] Analytics display
- [x] Back button navigation
- [x] Insufficient balance handling
- [x] Out of stock handling
- [x] Error logging

## Troubleshooting

### Bot doesn't start
- Check if `BOT_TOKEN` in `.env` is correct
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check bot.log for error messages

### Admin panel not accessible
- Verify your Telegram User ID is in `ADMIN_IDS` in `.env`
- Get your User ID from [@userinfobot](https://t.me/userinfobot)

### Files not being sent
- Check if `session_files/` directory exists
- Verify file paths in database are correct
- Check bot.log for file sending errors

### Database errors
- Delete `bot_database.db` and restart bot to recreate tables
- Check file permissions on database file

## Deployment

### Local Deployment
```bash
python bot.py
```

### Production Deployment

#### Using systemd (Linux)
Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram E-commerce Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/session-bucket
ExecStart=/usr/bin/python3 /path/to/session-bucket/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

#### Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t telegram-bot .
docker run -d --name telegram-bot --env-file .env telegram-bot
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For support, please contact the repository owner or open an issue on GitHub.

## Changelog

### Version 1.0.0 (Initial Release)
- User interface with product browsing, cart, and orders
- Admin panel with full management capabilities
- Instant checkout and file delivery
- Order history and re-download feature
- User and transaction management
- Analytics and reporting
- Broadcast messaging
- Comprehensive error handling and logging
