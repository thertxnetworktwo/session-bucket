# Quick Reference Guide

## Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/thertxnetworktwo/session-bucket.git
cd session-bucket

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your bot token and admin IDs

# 4. Run setup (optional - creates sample data)
python setup.py

# 5. Run tests (optional - verify everything works)
python test_bot.py

# 6. View demo (optional - see features without Telegram)
python demo.py

# 7. Start the bot
python bot.py
```

## Getting Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the bot token provided
5. Add token to `.env` file as `BOT_TOKEN=your_token_here`

## Getting Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Bot replies with your User ID
4. Add your ID to `.env` file as `ADMIN_IDS=your_id_here`

## Environment Variables (.env)

```env
# Required
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz          # From @BotFather
ADMIN_IDS=123456789,987654321                           # Comma-separated User IDs

# Optional (defaults work fine)
DATABASE_URL=sqlite:///bot_database.db                  # Database file path
SESSION_FILES_DIR=session_files                         # Where to store uploaded files
LOG_LEVEL=INFO                                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=bot.log                                        # Log file location
MAX_CART_ITEMS=50                                       # Maximum items in cart
ITEMS_PER_PAGE=5                                        # Items per page in lists
```

## File Structure

```
session-bucket/
├── bot.py                 # Main bot application
├── admin_handlers.py      # Admin panel functionality
├── database.py           # Database operations
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your configuration (create this)
├── .gitignore          # Git ignore rules
├── README.md           # Main documentation
├── USER_GUIDE.md       # Detailed user guide
├── QUICK_REFERENCE.md  # This file
├── setup.py           # Setup and sample data script
├── test_bot.py        # Test suite
├── demo.py            # Feature demonstration
└── session_files/     # Product files (created at runtime)
```

## User Commands (In-Bot)

- `/start` - Start bot and show main menu

All other interactions use inline keyboard buttons:
- 🛍️ Browse Products
- 🛒 My Cart
- 📦 My Orders
- 💳 Balance & Payment
- ℹ️ Help & Support
- 👤 Admin Panel (admins only)

## Admin Operations

### Product Management
1. Admin Panel → Manage Products → Add Product
2. Follow prompts: country, code, phone, price, stock, description, file
3. Use `/skip` to skip optional fields (description, file)
4. Use `/cancel` to cancel operation

### User Balance Management
1. Admin Panel → Manage Users → View All Users
2. Select user → Adjust Balance
3. Enter amount (positive to add, negative to deduct)

### Order Refunds
1. Admin Panel → Manage Orders → All Orders
2. Select order → Refund Order
3. Confirm refund
4. User balance is credited automatically

### Broadcast Messages
1. Admin Panel → Broadcast
2. Type message
3. Message sent to all active users

## Database Schema Quick Reference

### Main Tables
- **users** - User accounts and balances
- **products** - Available session files
- **orders** - Completed purchases
- **order_items** - Items in each order
- **transactions** - Balance changes
- **cart** - Temporary shopping cart

### Key Relationships
- Orders belong to Users
- Order Items belong to Orders and Products
- Cart items belong to Users and Products
- Transactions belong to Users

## Common Tasks

### Add First Product (Admin)
```
1. Start bot → Admin Panel
2. Manage Products → Add Product
3. Country name: United States
4. Country code: US
5. Phone code: +1
6. Price: 9.99
7. Stock: 50
8. Description: Premium US session files
9. Upload file or /skip
```

### Add User Balance (Admin)
```
1. Admin Panel → Manage Users
2. View All Users → Select user
3. Adjust Balance
4. Enter amount: 100
5. Confirm
```

### Make First Purchase (User)
```
1. Browse Products → Select country
2. Select product → Add to Cart
3. My Cart → Checkout
4. Files delivered instantly
5. Check My Orders to re-download
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot doesn't start | Check BOT_TOKEN in .env |
| Can't access admin panel | Add your User ID to ADMIN_IDS |
| Files not sending | Check session_files/ directory exists |
| Database errors | Delete bot_database.db and restart |
| "Insufficient balance" | Add balance via admin panel |
| Product not showing | Check stock_quantity > 0 |

## Testing

### Run All Tests
```bash
python test_bot.py
```

### Run Demo (No Telegram Required)
```bash
python demo.py
```

### Manual Testing Checklist
- [ ] User registration (/start)
- [ ] Browse products by country
- [ ] Add items to cart
- [ ] Adjust cart quantities
- [ ] Checkout with sufficient balance
- [ ] Checkout with insufficient balance
- [ ] View order history
- [ ] Re-download files
- [ ] View balance and transactions
- [ ] Admin panel access
- [ ] Add product
- [ ] Edit product
- [ ] Delete product
- [ ] View orders
- [ ] Refund order
- [ ] Manage users
- [ ] Ban/unban user
- [ ] Adjust user balance
- [ ] Broadcast message
- [ ] View analytics

## Performance Tips

1. **For Large Product Catalogs**:
   - Keep ITEMS_PER_PAGE at 5-10
   - Use clear product descriptions
   - Organize by country codes

2. **For High Volume**:
   - Monitor bot.log regularly
   - Keep session_files/ organized
   - Regular database backups

3. **For Better UX**:
   - Update stock quantities regularly
   - Respond to balance requests quickly
   - Use broadcast for important updates

## Security Checklist

- [ ] BOT_TOKEN is secret (never commit .env)
- [ ] ADMIN_IDS are correct
- [ ] .gitignore includes .env and *.db
- [ ] Session files are backed up
- [ ] Admin access is restricted
- [ ] Regular monitoring of bot.log

## Deployment Options

### Local (Development)
```bash
python bot.py
```

### Systemd Service (Linux Production)
```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

### Docker (Containerized)
```bash
docker build -t telegram-bot .
docker run -d --env-file .env telegram-bot
```

### Screen (Simple Background)
```bash
screen -S telegram-bot
python bot.py
# Press Ctrl+A, then D to detach
```

## Support & Resources

- **Main Documentation**: README.md
- **User Guide**: USER_GUIDE.md
- **Test Suite**: test_bot.py
- **Demo**: demo.py
- **Setup Helper**: setup.py
- **Repository**: https://github.com/thertxnetworktwo/session-bucket
- **Telegram Bot API**: https://core.telegram.org/bots/api

## Updates & Maintenance

### Regular Tasks
1. Check bot.log for errors
2. Monitor disk space (session_files/)
3. Update product stock
4. Process user balance requests
5. Review analytics

### Backup Strategy
1. Database: Copy bot_database.db regularly
2. Files: Backup session_files/ directory
3. Config: Keep .env backed up securely

## Version Information

- **Bot Version**: 1.0.0
- **Python Required**: 3.8+
- **python-telegram-bot**: 20.7
- **Database**: SQLite (upgradable to PostgreSQL)

---

**Need Help?** Check USER_GUIDE.md for detailed instructions or README.md for setup details.
