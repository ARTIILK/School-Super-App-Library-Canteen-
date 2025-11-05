🇮🇳 Indian Record Book Management System

A Complete Digital Transformation of Traditional Indian Business Ledgers.

This is a modern, AI-powered business management system designed specifically for Indian businesses to replace traditional record books (बही खाता) with automated billing, intelligent notifications, credit management, and AI-powered analytics.

✨ Complete Feature Set

📊 Core Business Management

✅ Customer Database - Complete KYC with GST numbers, credit limits, payment terms
✅ Transaction Recording - Sales, payments, refunds with automatic tax calculations
✅ Automated Monthly Billing - Generate professional invoices with one click
✅ Credit Limit Management - Real-time monitoring with automatic alerts
✅ Payment Tracking - Due date monitoring, overdue tracking, payment history
✅ Indian Currency Formatting - Proper ₹ formatting with lakhs/crores style

🤖 AI-Powered Features (Google Gemini Integration)

✅ Customer Behavior Analysis - AI insights on payment patterns
✅ Payment Reliability Scoring - 1-10 rating based on history
✅ Risk Assessment - Low/Medium/High risk classification
✅ Credit Limit Recommendations - AI suggestions for adjustments
✅ Collection Strategy Generator - Empathetic debt collection plans
✅ Red Flag Detection - Early warning system for problematic customers
✅ Trend Analysis - Identify payment patterns and behaviors

📧 Automated Email Notifications

✅ Monthly Bill Distribution - Auto-send professional invoices
✅ Overdue Payment Reminders - Scheduled reminder system
✅ Credit Limit Warnings - Alert when customers exceed limits
✅ Payment Confirmations - Automatic receipts
✅ Professional Email Templates - Branded, HTML-formatted emails
✅ Smart Reminder Scheduling - 3 days before, 7/15/30 days after due date
✅ Email Log Tracking - Complete history of all sent emails

💼 Indian Business Specific Features

✅ GST Integration - Automatic tax calculations (18% default, customizable)
✅ HSN Code Support - Product categorization
✅ Indian Number Format - 1,00,000.00 style formatting
✅ Multi-language Ready - Extensible for Hindi/regional languages
✅ Festival Considerations - Respect business holidays
✅ Invoice Numbering - INV202411-0001 format
✅ Professional Bill Format - Match Indian invoice standards

📱 Modern UI/UX

✅ Fully Responsive Design - Perfect on mobile, tablet, desktop
✅ Dark Mode Interface - Easy on eyes for extended use
✅ Gradient Cards - Beautiful, modern aesthetics
✅ Smooth Animations - Hover effects, transitions
✅ Real-time Search - Filter customers instantly
✅ Sorting & Filtering - By name, outstanding, overdue
✅ Interactive Dashboards - Live statistics
✅ Toast Notifications - User-friendly feedback
✅ Modal Dialogs - Clean forms without page reloads

🔐 Security & Authentication

✅ TOTP 2FA - Google Authenticator integration
✅ Secure Sessions - Flask session management
✅ No Browser Storage - All data in memory/database
✅ Protected Routes - Login required for all operations
✅ Password-free - More secure than traditional passwords
✅ QR Code Setup - Easy authentication setup

📈 Reports & Analytics

✅ Customer Ledger Export - Download CSV reports
✅ Outstanding Dashboard - Top debtors at a glance
✅ Revenue Tracking - Monthly revenue summaries
✅ Overdue Analytics - Track payment delays
✅ Payment History - Complete transaction logs
✅ Visual Indicators - Color-coded status badges

🔄 Automation Features

✅ Background Task Runner - Hourly automated checks
✅ Automatic Bill Generation - Monthly scheduling
✅ Smart Reminder System - Progressive reminder escalation
✅ Credit Monitoring - Real-time limit tracking
✅ Email Queue System - Reliable email delivery
✅ Transaction Auto-calculations - Tax, totals, due dates

🎯 How It Works

1. Customer Management Flow
Add Customer → Set Credit Limit → Assign Payment Terms → Start Transactions
↓
Monitor Outstanding → AI Analysis → Automated Alerts → Collection Strategy

2. Transaction Flow
Record Sale/Credit → Auto-calculate Tax → Set Due Date → Track Status
↓
Generate Monthly Bill → Email to Customer → Send Reminders → Mark as Paid

3. Automation Flow
Hourly Background Check → Identify Overdue → Send Reminders → Log Activity
↓
Check Credit Limits → Alert Exceeded → Email Warning → Update Dashboard

📦 Complete Installation Guide

Prerequisites

# Python 3.8 or higher
python --version

# pip package manager
pip --version


Step 1: Install All Dependencies

pip install Flask pandas matplotlib pyotp qrcode[pil] requests Pillow Werkzeug


Step 2: Project Structure

indian-record-book-system/
├── app.py                      # Main application (Enhanced)
├── record_book.db              # SQLite database (auto-created)
├── templates/
│   ├── layout.html             # Base layout (Modern UI)
│   ├── login.html              # TOTP login page
│   ├── setup_2fa.html          # 2FA setup with QR
│   ├── dashboard.html          # Analytics dashboard (NEW)
│   ├── customers.html          # Customer management (AI-powered)
│   ├── customer_detail.html    # Detailed customer view
│   ├── transactions.html       # Transaction recording
│   ├── bills.html              # Monthly billing
│   └── settings.html           # System configuration
└── README.md                   # This file


Step 3: Initial Setup

# Start the application
python app.py

# You'll see:
# ============================================
# 🚀 Indian Record Book System Starting...
# ============================================
# 📍 Access URL: [http://127.0.0.1:5000](http://127.0.0.1:5000)
# 🔐 Setup 2FA: [http://127.0.0.1:5000/setup-2fa](http://127.0.0.1:5000/setup-2fa)
# 🔑 Login: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
# ============================================


Step 4: Configure 2FA Authentication

Open: http://127.0.0.1:5000/setup-2fa

Scan QR Code with Google Authenticator app

Or manually enter the secret key provided.

Save this secret securely!

Step 5: Login

Go to: http://127.0.0.1:5000/login

Enter 6-digit code from Google Authenticator

Access granted! 🎉

⚙️ Essential Configuration

1. Email Setup (Gmail Example)

Generate App Password

Go to: https://myaccount.google.com/security

Enable 2-Step Verification

Go to: https://myaccount.google.com/apppasswords

Select "Mail" + Your device

Copy the 16-character password

Configure in Settings Page

SMTP Server: smtp.gmail.com

SMTP Port: 587

SMTP Email: youremail@gmail.com

SMTP Password: [16-character app password]

Test Email

Click "Test Email" button in Settings

Check your inbox for confirmation

2. AI Setup (Google Gemini)

Get API Key

Visit: https://makersuite.google.com/app/apikey

Sign in with Google account

Click "Create API Key"

Copy the key (starts with AIzaSy...)

Configure in Settings

Gemini API Key: AIzaSy...your-key-here

Test AI Features

Go to Customers page

Click 💡 icon next to any customer

View AI-powered analysis

3. Business Information

Business Name: Your Company Name

Business Address: Full address with city, state, PIN

Business Phone: +91 98765 43210

Business Email: business@example.com

Business GST Number: 22AAAAA0000A1Z5

Tax Rate: 18.0 (GST percentage)

📖 User Guide

Adding Your First Customer

Navigate to Customers page

Click "Add Customer" button

Fill in details:

Name, Email, Phone (required)

GST Number (optional)

Credit Limit (default: ₹5,000)

Payment Days (default: 30 days)

Address

Submit - Customer added!

Recording Transactions

Go to Transactions page

Click "New Transaction"

Select customer from dropdown

Choose type:

Sale/Credit: Customer owes money (creates unpaid transaction)

Payment Received: Customer paid (marks as paid)

Refund: Return money to customer

Enter amount - Tax calculated automatically

Add description (optional)

Submit - Transaction recorded!

Generating Monthly Bills

Navigate to Bills page

Click "Generate Bills"

Select month (e.g., 2024-11)

Click "Generate & Send"

System will:

Calculate all unpaid transactions for the month

Create bills for each customer

Send professional invoices via email

Log all activities

Using AI Analysis

Go to Customers page

Click 💡 (bulb icon) next to customer

View AI analysis:

Payment reliability score (1-10)

Risk assessment (Low/Medium/High)

Payment patterns

Credit limit recommendations

Red flags & positive indicators

Action items

Getting Collection Strategy

Customer with overdue bills shows 🚨 icon

Click the icon

AI generates:

Communication approach

Payment plan suggestion

Email template

Follow-up schedule

Escalation steps

Sending Payment Reminders

Click "Check Alerts" in sidebar

System automatically:

Scans all overdue bills

Sends reminder emails

Checks credit limit violations

Logs all notifications

Toast notification confirms completion

Exporting Customer Ledger

Go to customer detail page

Click download icon (↓)

CSV file downloads with:

All transactions

Dates, amounts, status

Tax calculations

Payment history

🎨 UI Features Explained

Dashboard Cards

Blue Card: Total active customers

Red Card: Outstanding balance (unpaid)

Yellow Card: Overdue bills (past due date)

Green Card: This month's revenue

Color Coding

🟢 Green: Paid, within limits, healthy

🟡 Yellow: Unpaid, approaching limit

🔴 Red: Overdue, exceeded limit, risky

🔵 Blue: Information, credit limit

🟣 Purple: AI features, analysis

Status Badges

Active: Customer is active

Inactive: Customer is inactive

Paid: Transaction completed

Unpaid: Payment pending

Overdue: Past due date

Icons & Actions

👁️ View: See detailed information

💡 AI Analysis: Get insights

🚨 Collection: Get strategy

↓ Export: Download ledger

✉️ Email: Send bill/reminder

🔧 Advanced Features

Automatic Tax Calculation

# GST is added automatically
Sale Amount: ₹10,000
Tax (18%): ₹1,800
Total: ₹11,800


Smart Due Date Setting

# Based on customer's payment terms
Transaction Date: 2024-11-01
Payment Days: 30
Due Date: 2024-12-01 (auto-calculated)


Progressive Reminder System

Day -3: Friendly reminder (payment due in 3 days)

Day 0: Payment due today

Day +7: First overdue reminder

Day +15: Second reminder (more urgent)

Day +30: Final reminder (escalation)

Indian Number Formatting

Western: 100,000.00

Indian: 1,00,000.00 ✓

Western: 1,000,000.00

Indian: 10,00,000.00 ✓

Bill Number Format

INV202411-0001

INV: Prefix (customizable)

202411: Year-Month

0001: Sequential number

📊 Database Schema

Customers Table

customer_id: Primary key

name, email, phone: Contact info

address, gst_number: Business details

credit_limit: Maximum credit

payment_days_limit: Payment terms

registration_date, status: Tracking

Transactions Table

transaction_id: Primary key

customer_id: Foreign key

transaction_type: Sale/Payment/Refund

amount, tax_amount, total_amount: Financials

transaction_date, due_date: Dates

status, payment_mode: Tracking

Monthly_Bills Table

bill_id: Primary key

bill_number: Unique invoice number

customer_id: Foreign key

bill_month: Billing period

subtotal, tax_amount, total_amount: Amounts

paid_amount, due_amount: Balance

bill_date, due_date: Dates

sent_date, last_reminder_date: Tracking

reminder_count, status: Automation

Email_Log Table

log_id: Primary key

customer_id: Foreign key

email_type: overdue / credit_limit / bill

sent_date, status, message: Tracking

🚀 Deployment Options

Local Network Access

# Start server (already configured for network access)
python app.py

# Find your computer's IP
# Windows: ipconfig
# Mac/Linux: ifconfig

# Access from other devices
[http://192.168.1.100:5000](http://192.168.1.100:5000)


Cloud Deployment

Option 1: Heroku (Free Tier)

# Install Heroku CLI
heroku login
heroku create your-app-name
git push heroku main


Option 2: Render (Modern PaaS)

Push code to GitHub

Connect Render to repository

Deploy automatically

Option 3: PythonAnywhere

Upload files via web interface

Configure web app

Set up virtual environment

🛡️ Security Best Practices

For Production Use

Change Secret Keys

# Generate new keys
import secrets
import pyotp

new_secret_key = secrets.token_hex(32)
new_totp_secret = pyotp.random_base32()

# Update app.py
app.config['SECRET_KEY'] = new_secret_key
app.config['TOTP_SECRET'] = new_totp_secret


Use Environment Variables

import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['TOTP_SECRET'] = os.getenv('TOTP_SECRET')


Backup Database Regularly

# Daily backup script
cp record_book.db backups/record_book_$(date +%Y%m%d).db


Enable HTTPS

Use reverse proxy (Nginx) or deploy to platform with SSL

Restrict Setup Page

# After initial setup, comment out:
# @app.route('/setup-2fa')


🐛 Troubleshooting

"Invalid authentication code"

✅ Ensure phone time is synced

✅ Codes refresh every 30 seconds

✅ Check correct secret key used

✅ Try previous/next code (valid_window=1)

Emails not sending

✅ Verify SMTP settings correct

✅ Use App Password (not regular password)

✅ Click "Test Email" in Settings

✅ Check spam folder

✅ Verify firewall/antivirus settings

AI analysis not working

✅ Verify Gemini API key valid

✅ Check internet connection

✅ Ensure API quota not exceeded

✅ Look for errors in console (F12)

✅ Try generating new API key

Database errors

✅ Check file permissions

✅ Ensure disk space available

✅ Backup and recreate if corrupted

✅ Stop all running instances

Mobile display issues

✅ Hard refresh (Ctrl+Shift+R)

✅ Clear browser cache

✅ Try different browser

✅ Check CSS loading correctly

📱 Mobile App Features

Responsive Design

✅ Single column layout on mobile

✅ Touch-friendly buttons

✅ Swipeable modals

✅ Optimized font sizes

✅ Collapsible sections

✅ Mobile-first approach

Mobile-Specific Features

✅ Quick actions on home screen

✅ One-tap customer add

✅ Simplified transaction entry

✅ Voice input support (browser feature)

✅ Camera for receipt scanning (future)

🎓 Educational Value

For CBSE Class 12 Students

This project demonstrates:

Python Programming: Functions, classes, decorators

Web Development: Flask, HTML, CSS, JavaScript

Database Management: SQLite, CRUD operations

API Integration: REST APIs, JSON handling

Authentication: TOTP, session management

Email Automation: SMTP, threading

AI/ML Integration: Natural language processing

UI/UX Design: Responsive design, user experience

Business Logic: Accounting, invoicing, taxation

Software Engineering: Modular design, best practices

🔮 Future Enhancements

Planned Features

[ ] PDF invoice generation

[ ] WhatsApp integration (via Twilio)

[ ] Payment gateway (Razorpay/Paytm)

[ ] Multi-user support with roles

[ ] Inventory management

[ ] Barcode/QR scanning

[ ] Voice commands

[ ] Mobile app (React Native)

[ ] Multi-language support

[ ] Advanced reporting & charts

[ ] Expense tracking

[ ] Profit/loss statements

[ ] TDS/TCS calculations

[ ] E-way bill generation

[ ] Bank reconciliation

🤝 Support & Contribution

Getting Help

Check troubleshooting section

Review error messages in console

Test with sample data

Verify all settings configured

Contributing

Report bugs

Suggest features

Improve documentation

Share use cases

Test on different devices

📄 License

MIT License - Free to use, modify, and distribute.

🙏 Credits

Built with:

Python & Flask

Google Gemini AI

Tailwind CSS

SQLite

PyOTP

Love ❤️ for Indian businesses

Perfect for:

CBSE Class 12 Computer Science Project

Small business management

Freelancer invoicing

Shop/retail management

Service providers

Any business needing credit management

📞 Contact & Support

For queries, issues, or feedback:

Check the troubleshooting section

Review console logs (F12 in browser)

Test email configuration

Verify AI API key

🇮🇳 Made in India, for India | Proudly Supporting Digital India Initiative

⚡ Quick Start Checklist

[ ] Install Python 3.8+

[ ] Install dependencies (pip install ...)

[ ] Run app (python app.py)

[ ] Setup 2FA (scan QR code)

[ ] Login with 6-digit code

[ ] Configure email (Settings)

[ ] Add Gemini API key (Settings)

[ ] Add first customer

[ ] Record first transaction

[ ] Generate first bill

[ ] Test AI analysis

[ ] Check automated reminders

[ ] Export customer ledger

[ ] Customize business info

🎉 You're all set! Welcome to the future of Indian business management! 🚀
