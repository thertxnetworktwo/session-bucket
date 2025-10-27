# User Guide - Telegram E-commerce Bot

## For End Users

### Getting Started

1. **Start the bot**: Find the bot on Telegram and send `/start`
2. You'll see the main menu with these options:
   - 🛍️ Browse Products
   - 🛒 My Cart
   - 📦 My Orders
   - 💳 Balance & Payment
   - ℹ️ Help & Support

### Browsing and Shopping

#### Browse Products
1. Click **"🛍️ Browse Products"**
2. Select a country from the list (organized by phone code)
3. View available session files for that country
4. Click on a product to see details (price, stock, description)

#### Add to Cart
1. When viewing a product, click **"➕ Add to Cart"**
2. The item is added to your cart
3. You can continue shopping or go to your cart

#### Manage Cart
1. Click **"🛒 My Cart"** from the main menu
2. View all items in your cart
3. Adjust quantities:
   - Click **➖** to decrease quantity
   - Click **➕** to increase quantity
4. Click **"🗑️ Clear Cart"** to remove all items
5. Click **"💳 Checkout"** when ready to purchase

#### Checkout Process
1. Review your cart items and total
2. The system checks if you have sufficient balance
3. If balance is sufficient:
   - Order is created instantly
   - Balance is deducted
   - Files are delivered immediately
   - Order is saved to history
4. If balance is insufficient:
   - You'll see how much more you need
   - Click **"💳 Add Balance"** to add funds

### Managing Your Account

#### View Balance
1. Click **"💳 Balance & Payment"**
2. See your current balance
3. View transaction history

#### Add Balance
1. From Balance menu, click **"➕ Add Balance"**
2. Follow the payment instructions
3. Contact an administrator to credit your account
4. Once credited, you can start shopping

#### Transaction History
1. From Balance menu, click **"📜 Transaction History"**
2. View all your transactions (deposits, purchases, refunds)

### Order Management

#### View Orders
1. Click **"📦 My Orders"** from main menu
2. See list of all your orders
3. Each order shows:
   - Order number
   - Date and time
   - Total amount
   - Status (✅ Completed, ❌ Failed, 🔄 Refunded)

#### Order Details
1. Click on any order to view details
2. See all items in the order
3. View total amount paid

#### Re-download Files
1. Open any completed order
2. Click **"📥 Re-download Files"**
3. All session files from that order are sent to you again
4. You can re-download anytime - no extra charge!

### Navigation Tips

- Every screen has a **"⬅️ Back"** button
- Use it to return to the previous menu
- Click **"🏠 Main Menu"** to return home anytime
- Use pagination arrows (◀️ ▶️) for long lists

### Common Questions

**Q: How do I pay for products?**
A: All purchases are made using your account balance. Add funds first, then shop!

**Q: When do I receive my files?**
A: Immediately! As soon as payment is processed, files are delivered.

**Q: Can I download files again?**
A: Yes! Go to My Orders, select the order, and click Re-download Files.

**Q: What if I ordered the wrong product?**
A: Contact an administrator for a refund. They can process it and credit your balance.

**Q: How do I add balance?**
A: Click Balance & Payment → Add Balance and follow the instructions to contact an admin.

---

## For Administrators

### Accessing Admin Panel

1. Your Telegram User ID must be in the `ADMIN_IDS` configuration
2. Start the bot and send `/start`
3. Click **"👤 Admin Panel"** from the main menu

### Admin Dashboard

The dashboard shows key statistics:
- Total users registered
- Total orders (all time, today, this week)
- Total revenue (all time, today, this week)

### Product Management

#### Add New Product
1. Go to **"📦 Manage Products"** → **"➕ Add Product"**
2. Follow the prompts:
   - Enter country name (e.g., "United States")
   - Enter country code (e.g., "US")
   - Enter phone code (e.g., "+1")
   - Enter price (e.g., "9.99")
   - Enter stock quantity (e.g., "50")
   - Enter description (or /skip)
   - Upload session file (or /skip)
3. Product is created and immediately available to users

#### View Products
1. Go to **"📦 Manage Products"** → **"📋 View All Products"**
2. See list of all products
3. Click on any product to view details

#### Edit Product
1. View product details
2. Click options to edit:
   - **"✏️ Edit Price"** - Change product price
   - **"📦 Edit Stock"** - Adjust stock quantity
   - **"📝 Edit Description"** - Update description
   - **"📄 Edit File"** - Upload new session file

#### Delete Product
1. View product details
2. Click **"🗑️ Delete Product"**
3. Confirm deletion
4. Product is permanently removed

### Order Management

#### View Orders
1. Go to **"🛍️ Manage Orders"**
2. Filter by status:
   - **"✅ Completed Orders"** - Successfully delivered
   - **"❌ Failed Orders"** - Payment failed
   - **"🔄 Refunded Orders"** - Refunded to user
   - **"📋 All Orders"** - View everything

#### Order Details
1. Click on any order
2. View:
   - User information
   - Order date and status
   - Items ordered
   - Total amount

#### Resend Files
1. View order details
2. Click **"📥 Resend Files"**
3. All session files are sent to the user again
4. Useful if user lost files or experienced download issues

#### Refund Order
1. View completed order details
2. Click **"🔄 Refund Order"**
3. Confirm refund
4. Order status changes to "refunded"
5. User's balance is credited with the order amount
6. Transaction is logged

### User Management

#### View Users
1. Go to **"👥 Manage Users"** → **"📋 View All Users"**
2. See all registered users
3. Icons indicate:
   - 👑 Admin users
   - 🚫 Banned users

#### User Details
1. Click on any user
2. View:
   - User ID and username
   - Current balance
   - Registration date
   - Total orders and spending
   - Ban status

#### Adjust User Balance
1. View user details
2. Click **"💰 Adjust Balance"**
3. Follow prompts to add or deduct funds
4. Transaction is logged

#### Ban/Unban Users
1. View user details
2. Click **"🚫 Ban User"** to ban
3. Click **"✅ Unban User"** to unban
4. Banned users cannot use the bot

### Analytics

1. Go to **"📊 Analytics"**
2. View:
   - Best-selling products
   - Total sales per product
   - Revenue by product

### Broadcast Messages

1. Go to **"📢 Broadcast"**
2. Send a message
3. Message is sent to all active (non-banned) users
4. Use for announcements, promotions, updates

### Admin Best Practices

1. **Stock Management**:
   - Regularly update stock quantities
   - Upload session files before adding products
   - Set accurate descriptions

2. **User Support**:
   - Respond to payment requests promptly
   - Credit balances accurately
   - Process refunds when appropriate

3. **Monitoring**:
   - Check dashboard daily
   - Review failed orders
   - Monitor user activity

4. **Security**:
   - Keep admin IDs confidential
   - Verify payment receipts before crediting
   - Review suspicious activity

5. **File Management**:
   - Organize session files properly
   - Test file uploads before adding products
   - Keep backups of session files

### Common Admin Tasks

#### Daily Tasks
- Check dashboard statistics
- Review new orders
- Process balance requests
- Respond to support messages

#### Weekly Tasks
- Review analytics
- Update product stock
- Check for inactive products
- Review user activity

#### Monthly Tasks
- Generate revenue reports
- Update pricing if needed
- Review and update product descriptions
- Archive old orders if needed

---

## Troubleshooting

### For Users

**Problem**: "Insufficient balance" error
- **Solution**: Add balance through the Balance & Payment menu

**Problem**: Can't find a product
- **Solution**: Check if it's in stock; out-of-stock items don't appear

**Problem**: Files not received
- **Solution**: Check your Telegram for file messages; use Re-download if needed

### For Admins

**Problem**: Can't access Admin Panel
- **Solution**: Verify your User ID is in ADMIN_IDS in .env file

**Problem**: Files not sending to users
- **Solution**: Check that session files exist at the specified path

**Problem**: Database errors
- **Solution**: Check bot.log file for error details; restart bot if needed

---

## Support

For additional help:
- Check bot.log for error messages
- Review README.md for setup instructions
- Contact repository maintainer for technical issues
