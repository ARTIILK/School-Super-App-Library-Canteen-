import sqlite3
import os
import datetime
from functools import wraps
from decimal import Decimal
import json

# DEBUG: Confirm app.py path
print(f"DEBUG: app.py loaded from: {os.path.abspath(__file__)}")

# --- Web App & Analytics Imports ---
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# --- Authentication & Email Imports ---
import pyotp
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from threading import Thread
import time

from functools import wraps
import hashlib

# --- AI & PDF Imports ---
import requests

# --- Database Setup ---


def get_db_conn(db_path=None):


    if db_path is None:


        db_path = app.config.get('DATABASE', 'record_book.db')


    conn = sqlite3.connect(db_path)


    conn.row_factory = sqlite3.Row


    return conn



def initialize_database(db_path="record_book.db"):

    """Creates the database with all tables for record book management"""

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    

    # --- Customers Table ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS customers (

            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            phone TEXT NOT NULL,

            address TEXT,

            gst_number TEXT,

            credit_limit REAL DEFAULT 5000.00,

            payment_days_limit INTEGER DEFAULT 30,

            registration_date TEXT NOT NULL,

            status TEXT DEFAULT 'Active',

            reminder_preference TEXT DEFAULT 'email'

        )

    """

    )

    

    # --- Transactions Table ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS transactions (

            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            transaction_type TEXT NOT NULL,

            amount REAL NOT NULL,

            tax_amount REAL DEFAULT 0,

            total_amount REAL NOT NULL,

            description TEXT,

            transaction_date TEXT NOT NULL,

            due_date TEXT,

            status TEXT DEFAULT 'Unpaid',

            payment_mode TEXT,

            reference_number TEXT,

            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)

        )

    """

    )

    

    # --- Monthly Bills Table ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS monthly_bills (

            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            bill_number TEXT UNIQUE NOT NULL,

            bill_month TEXT NOT NULL,

            subtotal REAL NOT NULL,

            tax_amount REAL DEFAULT 0,

            total_amount REAL NOT NULL,

            paid_amount REAL DEFAULT 0,

            due_amount REAL NOT NULL,

            bill_date TEXT NOT NULL,

            due_date TEXT NOT NULL,

            status TEXT DEFAULT 'Unpaid',

            sent_date TEXT,

            last_reminder_date TEXT,

            reminder_count INTEGER DEFAULT 0,

            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)

        )

    """

    )

    

    # --- Email Notifications Log ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS email_log (

            log_id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            email_type TEXT NOT NULL,

            sent_date TEXT NOT NULL,

            status TEXT NOT NULL,

            message TEXT,

            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)

        )

    """

    )

    

    # --- Products/Services Table ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS products (

            product_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT,

            hsn_code TEXT,

            price REAL NOT NULL,

            tax_rate REAL DEFAULT 18.0,

            category TEXT,

            stock_quantity INTEGER DEFAULT 0,

            unit TEXT DEFAULT 'piece'

        )

    """

    )

    

    # --- Payment Reminders Schedule ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS reminder_schedule (

            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,

            bill_id INTEGER,

            reminder_date TEXT NOT NULL,

            reminder_type TEXT NOT NULL,

            status TEXT DEFAULT 'pending',

            sent_date TEXT,

            FOREIGN KEY (bill_id) REFERENCES monthly_bills (bill_id)

        )

    """

    )

    

    # --- System Settings Table ---

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS settings (

            setting_key TEXT PRIMARY KEY,

            setting_value TEXT NOT NULL

        )

    """

    )

    

    # Insert default settings

    default_settings = {

        'smtp_server': '',

        'smtp_port': '587',

        'smtp_email': '',

        'smtp_password': '',

        'gemini_api_key': '',

        'business_name': 'My Business',

        'business_address': '',

        'business_phone': '',

        'business_email': '',

        'business_gst': '',

        'tax_rate': '18.0',

        'currency_symbol': '₹',

        'bill_prefix': 'INV',

        'reminder_days_before': '3',

        'reminder_days_after': '7,15,30',

        'business_logo_url': ''

    }

    

    for key, value in default_settings.items():

        cursor.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (key, value))

    

    conn.commit()

    conn.close()



# --- Flask App Initialization ---

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a8f5f167f44f4964e6c998dee827110c')

app.config['TOTP_SECRET'] = os.getenv('TOTP_SECRET', 'JBSWY3DPEHPK3PXP')

app.config['DATABASE'] = 'record_book.db'

# --- Helper Functions ---
def get_db_conn():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_setting(key):
    """Get a setting value from database"""
    conn = get_db_conn(app.config['DATABASE'])
    result = conn.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,)).fetchone()
    conn.close()
    return result['setting_value'] if result else None

def format_currency(amount):
    """Format amount in Indian currency style"""
    
    # --- FIX: Define default symbol *before* the try block ---
    symbol = '₹'  
    
    try:
        amount = float(amount)
        
        # Try to get a new symbol from DB, but 'symbol' is already safe
        db_symbol = get_setting('currency_symbol')
        if db_symbol:
            symbol = db_symbol
        
        # Simple fix - use standard formatting
        return f"{symbol}{amount:,.2f}"
        
        # OR for proper Indian style (lakhs/crores):
        # ... (your other formatting logic) ...
        
    except:
        # No error: 'symbol' is guaranteed to be '₹' (the default)
        return f"{symbol}0.00"

def generate_bill_number():
    """Generate unique bill number"""
    prefix = get_setting('bill_prefix') or 'INV'
    today = datetime.now()
    conn = get_db_conn(app.config['DATABASE'])
    
    # Count bills this month
    count = conn.execute("""
        SELECT COUNT(*) as cnt FROM monthly_bills 
        WHERE strftime('%Y-%m', bill_date) = ?
    """, (today.strftime('%Y-%m'),)).fetchone()['cnt']
    
    conn.close()
    
    return f"{prefix}{today.strftime('%Y%m')}{str(count + 1).zfill(4)}"

def send_email_async(recipient, subject, body, attachment=None):
    """Send email in background thread"""
    def send():
        try:
            smtp_server = get_setting('smtp_server')
            smtp_port = int(get_setting('smtp_port') or 587)
            smtp_email = get_setting('smtp_email')
            smtp_password = get_setting('smtp_password')
            
            if not all([smtp_server, smtp_email, smtp_password]):
                print("Email settings not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = smtp_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachment if provided
            if attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['data'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment["filename"]}')
                msg.attach(part)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    Thread(target=send).start()

    conn = get_db_conn(app.config['DATABASE'])
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_date_obj = datetime.strptime(today_str, '%Y-%m-%d')
    business_name = get_setting('business_name')
    
    overdue_bills = conn.execute("""
        SELECT b.*, c.name, c.email, c.credit_limit 
        FROM monthly_bills b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE b.status = 'Unpaid' AND b.due_date < ?
    """, (today_str,)).fetchall()
    
    for bill in overdue_bills:
        days_overdue = (today_date_obj - datetime.strptime(bill['due_date'], '%Y-%m-%d')).days
        
        # Check if reminder was sent recently
        last_reminder = bill['last_reminder_date']
        if last_reminder:
            days_since_reminder = (datetime.now() - datetime.strptime(last_reminder, '%Y-%m-%d')).days
            if days_since_reminder < 7:  # Don't spam - wait 7 days between reminders
                continue
        
        subject = f"⚠️ Payment Overdue - Bill #{bill['bill_number']}"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Payment Overdue Notice</h1>
            </div>
            <div style="background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px;">Dear <strong>{bill['name']}</strong>,</p>
                <p>This is a reminder that your payment is <strong style="color: #dc2626;">{days_overdue} days overdue</strong>.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;"><strong>Bill Number:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">{bill['bill_number']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;"><strong>Due Date:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">{bill['due_date']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>Amount Due:</strong></td>
                            <td style="padding: 10px; text-align: right; font-size: 20px; color: #dc2626;"><strong>{format_currency(bill['due_amount'])}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <p style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px;">
                    <strong>⚠️ Important:</strong> Please arrange payment at the earliest to avoid service interruption and late fees.
                </p>
                
                <p style="margin-top: 30px;">For payment queries, please contact us.</p>
                <p style="color: #6b7280; font-size: 14px;">Thank you,<br><strong>{business_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        send_email_async(bill['email'], subject, body)
        
        # Update reminder count and date
        conn.execute("""
            UPDATE monthly_bills 
            SET last_reminder_date = ?, reminder_count = reminder_count + 1
            WHERE bill_id = ?
        """, (today, bill['bill_id']))
        
        conn.execute("""
            INSERT INTO email_log (customer_id, email_type, sent_date, status, message)
            VALUES (?, 'overdue_notice', ?, 'sent', ?)
        """, (bill['customer_id'], today, f"Overdue by {days_overdue} days"))
    
    conn.commit()
    conn.close()

def check_credit_limit_exceeded():
    """Check customers exceeding credit limit"""
    conn = get_db_conn(app.config['DATABASE'])
    business_name = get_setting('business_name')
    
    customers = conn.execute("""
        SELECT c.*, 
               COALESCE(SUM(b.due_amount), 0) as total_due
        FROM customers c
        LEFT JOIN monthly_bills b ON c.customer_id = b.customer_id AND b.status = 'Unpaid'
        GROUP BY c.customer_id
        HAVING total_due > c.credit_limit
    """).fetchall()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for customer in customers:
        exceeded_by = customer['total_due'] - customer['credit_limit']
        
        # Check if a credit limit exceeded email was sent recently
        last_credit_alert = conn.execute("""
            SELECT sent_date FROM email_log
            WHERE customer_id = ? AND email_type = 'credit_limit_exceeded'
            ORDER BY sent_date DESC LIMIT 1
        """, (customer['customer_id'],)).fetchone()

        if last_credit_alert:
            last_alert_date = datetime.strptime(last_credit_alert['sent_date'], '%Y-%m-%d')
            if (datetime.now() - last_alert_date).days < 7:
                # Skip sending if an alert was sent within the last 7 days
                continue

        subject = "⚠️ Credit Limit Exceeded - Immediate Action Required"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Credit Limit Alert</h1>
            </div>
            <div style="background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px;">Dear <strong>{customer['name']}</strong>,</p>
                <p>Your outstanding balance has exceeded your approved credit limit.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;"><strong>Credit Limit:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">{format_currency(customer['credit_limit'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;"><strong>Current Balance:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right; color: #dc2626;">{format_currency(customer['total_due'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>Exceeded By:</strong></td>
                            <td style="padding: 10px; text-align: right; font-size: 20px; color: #dc2626;"><strong>{format_currency(exceeded_by)}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <p style="background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 4px;">
                    <strong>⚠️ Action Required:</strong> Please clear pending dues immediately to continue services. New orders may be held until your balance is brought within the credit limit.
                </p>
                
                <p style="margin-top: 30px;">For payment arrangements or credit limit increase requests, please contact us.</p>
                <p style="color: #6b7280; font-size: 14px;">Thank you,<br><strong>{business_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        send_email_async(customer['email'], subject, body)
        
        conn.execute("""
            INSERT INTO email_log (customer_id, email_type, sent_date, status, message)
            VALUES (?, 'credit_limit_exceeded', ?, 'sent', ?)
        """, (customer['customer_id'], today, f"Exceeded by {format_currency(exceeded_by)}"))
    
    conn.commit()
    conn.close()

# --- AI Cooldown Management ---
last_ai_call = {}

def check_ai_cooldown(customer_id, analysis_type='analysis'):
    """Check if AI call is allowed (30 second cooldown)"""
    current_time = time.time()
    key = f"{customer_id}_{analysis_type}"
    
    if key in last_ai_call:
        elapsed = current_time - last_ai_call[key]
        if elapsed < 30:
            remaining = 30 - elapsed
            return {
                'allowed': False,
                'remaining': int(remaining),
                'message': f'⏳ AI cooldown active. Please wait {int(remaining)} seconds before next analysis.'
            }
    
    last_ai_call[key] = current_time
    return {'allowed': True}

def ai_analyze_customer(customer_id):
    """Use Gemini AI to analyze customer payment behavior"""
    # Check cooldown
    cooldown_check = check_ai_cooldown(customer_id, 'analysis')
    if not cooldown_check['allowed']:
        return f"**{cooldown_check['message']}**\n\nThis prevents API rate limiting. The cooldown will reset automatically."
    
    api_key = get_setting('gemini_api_key')
    if not api_key:
            conn = get_db_conn(app.config['DATABASE'])    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    
    transactions = conn.execute("""
        SELECT * FROM transactions 
        WHERE customer_id = ? 
        ORDER BY transaction_date DESC LIMIT 50
    """, (customer_id,)).fetchall()
    
    bills = conn.execute("""
        SELECT * FROM monthly_bills 
        WHERE customer_id = ? 
        ORDER BY bill_date DESC LIMIT 12
    """, (customer_id,)).fetchall()
    
    conn.close()
    
    # Prepare data summary
    total_transactions = len(transactions)
    paid_on_time = sum(1 for t in transactions if t['status'] == 'Paid')
    total_billed = sum(b['total_amount'] for b in bills)
    total_paid = sum(b['paid_amount'] for b in bills)
    avg_days_to_pay = 0
    
    transaction_summary = "\n".join([
        f"Date: {t['transaction_date']}, Type: {t['transaction_type']}, Amount: {format_currency(t['total_amount'])}, Status: {t['status']}"
        for t in transactions[:20]
    ])
    
    prompt = f"""
    As a business financial analyst, analyze this customer's payment behavior and provide actionable insights:
    
    **Customer Information:**
    - Name: {customer['name']}
    - Credit Limit: {format_currency(customer['credit_limit'])}
    - Payment Terms: {customer['payment_days_limit']} days
    - Customer Since: {customer['registration_date']}
    
    **Financial Summary:**
    - Total Transactions: {total_transactions}
    - Total Amount Billed (last 12 months): {format_currency(total_billed)}
    - Total Amount Paid: {format_currency(total_paid)}
    - Outstanding: {format_currency(total_billed - total_paid)}
    - Payment Success Rate: {(paid_on_time/total_transactions*100) if total_transactions > 0 else 0:.1f}%
    
    **Recent Transaction History (last 20):**
    {transaction_summary}
    
    Please provide:
    1. **Payment Reliability Score (1-10):** Rate the customer's payment reliability
    2. **Risk Assessment:** Classify as Low/Medium/High risk with reasoning
    3. **Payment Pattern Analysis:** Identify trends and behaviors
    4. **Credit Limit Recommendation:** Should it be increased, decreased, or maintained?
    5. **Action Items:** Specific recommendations for managing this customer relationship
    6. **Red Flags:** Any warning signs to watch for
    7. **Positive Indicators:** Strong points about this customer
    
    Format your response in clear sections with emojis for visual clarity.
    """
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "⚠️ AI analysis returned an unexpected response format."
        else:
            return f"⚠️ AI Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

def ai_generate_collection_strategy(customer_id):
    """Generate AI-powered debt collection strategy"""
    # Check cooldown
    cooldown_check = check_ai_cooldown(customer_id, 'collection_strategy')
    if not cooldown_check['allowed']:
        return f"**{cooldown_check['message']}**\n\nThis prevents API rate limiting. The cooldown will reset automatically."
    
    api_key = get_setting('gemini_api_key')
        if not api_key:
            return "AI not configured"
    
        conn = get_db_conn(app.config['DATABASE'])    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    overdue_bills = conn.execute("""
        SELECT * FROM monthly_bills 
        WHERE customer_id = ? AND status = 'Unpaid' AND due_date < date('now')
        ORDER BY due_date ASC
    """, (customer_id,)).fetchall()
    conn.close()
    
    if not overdue_bills:
        return "No overdue bills for this customer."
    
    total_overdue = sum(b['due_amount'] for b in overdue_bills)
    oldest_bill = overdue_bills[0]
    days_overdue = (datetime.now() - datetime.strptime(oldest_bill['due_date'], '%Y-%m-%d')).days
    
    prompt = f"""
    Create a professional and empathetic debt collection strategy for:
    
    Customer: {customer['name']}
    Total Overdue: {format_currency(total_overdue)}
    Oldest Bill: {days_overdue} days overdue
    Number of Overdue Bills: {len(overdue_bills)}
    
    Provide:
    1. Communication approach (tone, channel)
    2. Payment plan suggestion
    3. Email template
    4. Follow-up schedule
    5. Escalation steps if needed
    
    Keep it professional, empathetic, and effective for Indian business context.
    """
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"AI Error: {response.status_code}"
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Authentication Routes ---
@app.route('/setup-2fa')
def setup_2fa():
    totp_secret = app.config['TOTP_SECRET']
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name='admin@recordbook',
        issuer_name='Record Book System'
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_img = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('setup_2fa.html', totp_secret=totp_secret, qr_code=qr_code_img)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        totp = pyotp.TOTP(app.config['TOTP_SECRET'])
        
        if totp.verify(code, valid_window=1):
            session['logged_in'] = True
            session['login_time'] = datetime.now().isoformat()
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid authentication code. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged in successfully.', 'success')
    return redirect(url_for('login'))

# --- Main Routes ---
@app.route('/')
@login_required
def dashboard():
    conn = get_db_conn(app.config['DATABASE'])
    
    # Dashboard statistics
    total_customers = conn.execute("SELECT COUNT(*) as count FROM customers WHERE status='Active'").fetchone()['count']
    total_unpaid = conn.execute("SELECT COALESCE(SUM(due_amount), 0) as total FROM monthly_bills WHERE status = 'Unpaid'").fetchone()['total']
    overdue_count = conn.execute("SELECT COUNT(*) as count FROM monthly_bills WHERE status = 'Unpaid' AND due_date < date('now')").fetchone()['count']
    this_month_revenue = conn.execute("SELECT COALESCE(SUM(paid_amount), 0) as total FROM monthly_bills WHERE strftime('%Y-%m', bill_date) = strftime('%Y-%m', 'now')").fetchone()['total']
    
    # Recent transactions
    recent_transactions = conn.execute("""
        SELECT t.*, c.name as customer_name 
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        ORDER BY t.transaction_date DESC LIMIT 10
    """).fetchall()
    
    # Top customers by outstanding
    top_debtors = conn.execute("""
        SELECT c.name, c.customer_id, COALESCE(SUM(b.due_amount), 0) as outstanding
        FROM customers c
        LEFT JOIN monthly_bills b ON c.customer_id = b.customer_id AND b.status = 'Unpaid'
        GROUP BY c.customer_id
        HAVING outstanding > 0
        ORDER BY outstanding DESC
        LIMIT 5
    """).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         active_page='dashboard',
                         total_customers=total_customers,
                         total_unpaid=total_unpaid,
                         overdue_count=overdue_count,
                         this_month_revenue=this_month_revenue,
                         recent_transactions=recent_transactions,
                         top_debtors=top_debtors,
                         format_currency=format_currency,
                         current_date=datetime.now())

@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    conn = get_db_conn(app.config['DATABASE'])
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form.get('address', '')
        gst_number = request.form.get('gst_number', '')
        credit_limit = float(request.form.get('credit_limit', 5000))
        payment_days = int(request.form.get('payment_days', 30))
        
        try:
            conn.execute("""
                INSERT INTO customers (name, email, phone, address, gst_number, credit_limit, payment_days_limit, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, address, gst_number, credit_limit, payment_days, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            flash(f'✅ Customer "{name}" added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('❌ Error: Email already exists!', 'error')
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
        
        conn.close()
        return redirect(url_for('customers'))
    
    # Get all customers with outstanding balance
    customers_list = conn.execute("""
        SELECT c.*, 
               COALESCE(SUM(CASE WHEN b.status = 'Unpaid' THEN b.due_amount ELSE 0 END), 0) as outstanding_balance,
               COUNT(CASE WHEN b.status = 'Unpaid' AND b.due_date < date('now') THEN 1 END) as overdue_bills
        FROM customers c
        LEFT JOIN monthly_bills b ON c.customer_id = b.customer_id
        GROUP BY c.customer_id
        ORDER BY c.name
    """).fetchall()
    
    conn.close()
    return render_template('customers.html', active_page='customers', customers=customers_list, format_currency=format_currency)

@app.route('/customer/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    conn = get_db_conn(app.config['DATABASE'])
    
    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    transactions = conn.execute("""
        SELECT * FROM transactions 
        WHERE customer_id = ? 
        ORDER BY transaction_date DESC
    """, (customer_id,)).fetchall()
    
    bills = conn.execute("""
        SELECT * FROM monthly_bills 
        WHERE customer_id = ? 
        ORDER BY bill_date DESC
    """, (customer_id,)).fetchall()
    
    # Calculate summary stats
    total_billed = sum(b['total_amount'] for b in bills)
    total_paid = sum(b['paid_amount'] for b in bills)
    total_outstanding = sum(b['due_amount'] for b in bills if b['status'] == 'Unpaid')
    
    conn.close()
    
    return render_template('customer_detail.html', 
                         active_page='customers',
                         customer=customer,
                         transactions=transactions,
                         bills=bills,
                         total_billed=total_billed,
                         total_paid=total_paid,
                         total_outstanding=total_outstanding,
                         format_currency=format_currency)

####################################################################
# Add after existing imports
import re
from datetime import datetime, timedelta

# Natural Language Search
@app.route('/nl-search', methods=['POST'])
@login_required
def nl_search():
    """AI-powered natural language search"""
    data = request.json
    query = data['query'].lower()
    
    # Check cooldown
    cooldown_check = check_ai_cooldown('nl_search', 'search')
    if not cooldown_check['allowed']:
        return jsonify({
            'error': f"⏳ Please wait {cooldown_check['remaining']} seconds"
        })
    
    api_key = get_setting('gemini_api_key')
    if not api_key:
        return jsonify({'error': 'AI not configured'})
    
    conn = get_db_conn()
    
    # Get context for AI
    customers = conn.execute("SELECT name FROM customers LIMIT 20").fetchall()
    customer_names = [c['name'] for c in customers]
    
    prompt = f"""
    You are a SQL query generator for an Indian business record book system.
    
    User query: "{query}"
    
    Available customer names: {', '.join(customer_names)}
    
    Database schema:
    - transactions(customer_id, transaction_type, amount, total_amount, transaction_date, status, description)
    - monthly_bills(customer_id, bill_month, total_amount, due_amount, status, due_date)
    - customers(customer_id, name, email, credit_limit)
    
    Generate a response in this JSON format:
    {{
        "query_type": "select/summary",
        "sql_query": "SELECT ... FROM ...",
        "explanation": "Human-readable explanation"
    }}
    
    Rules:
    1. For "show/find" queries: Generate SELECT query
    2. For "total/sum" queries: Use SUM() aggregation
    3. For "last month": Use date functions
    4. Customer names are case-insensitive
    5. Return ONLY valid JSON, no markdown
    """
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # Execute the query
                try:
                    sql_query = parsed['sql_query']
                    # CRITICAL SECURITY CHECK: Ensure only SELECT queries are executed
                    if not sql_query.strip().upper().startswith("SELECT"):
                        conn.close()
                        return jsonify({'error': 'AI attempted to execute a non-SELECT query. This action is blocked for security reasons.'})

                    results = conn.execute(sql_query).fetchall()
                    conn.close()
                    
                    # Format results
                    if results:
                        result_html = '<table class="w-full"><thead><tr>'
                        for key in results[0].keys():
                            result_html += f'<th class="text-left px-2 py-1">{key}</th>'
                        result_html += '</tr></thead><tbody>'
                        
                        for row in results:
                            result_html += '<tr class="border-t border-gray-700">'
                            for value in row:
                                result_html += f'<td class="px-2 py-1">{value}</td>'
                            result_html += '</tr>'
                        result_html += '</tbody></table>'
                        
                        return jsonify({
                            'results': f"<p class='mb-2'>{parsed['explanation']}</p>{result_html}"
                        })
                    else:
                        return jsonify({
                            'results': f"<p>{parsed['explanation']}</p><p class='text-yellow-400 mt-2'>No results found.</p>"
                        })
                except Exception as e:
                    conn.close()
                    return jsonify({'error': f'Query error: {str(e)}'})
            else:
                conn.close()
                return jsonify({'error': 'Could not parse AI response'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)})

# Quick Customer Insight
@app.route('/customer-quick-insight/<int:customer_id>')
@login_required
def customer_quick_insight(customer_id):
    """Quick AI insight for customer (1 sentence)"""
    conn = get_db_conn()
    
    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    recent_trans = conn.execute("""
        SELECT COUNT(*) as count, AVG(total_amount) as avg_amount
        FROM transactions 
        WHERE customer_id = ? AND transaction_date > date('now', '-3 months')
    """, (customer_id,)).fetchone()
    
    conn.close()
    
    count = recent_trans['count']
    avg = recent_trans['avg_amount'] or 0
    
    if count > 10:
        insight = f"💎 High-value customer! {count} transactions in 3 months, avg ₹{avg:.0f}"
    elif count > 5:
        insight = f"✅ Regular customer with {count} recent transactions"
    elif count > 0:
        insight = f"🆕 New customer with {count} transactions so far"
    else:
        insight = "🆕 Brand new customer - no transaction history"
    
    return jsonify({'insight': insight})

# Smart Transaction Suggestions
@app.route('/smart-transaction-suggestions/<int:customer_id>')
@login_required
def smart_transaction_suggestions(customer_id):
    """Suggest common transaction amounts/descriptions"""
    conn = get_db_conn()
    
    # Get most common transactions
    suggestions = conn.execute("""
        SELECT amount, description, COUNT(*) as frequency
        FROM transactions
        WHERE customer_id = ? AND transaction_type = 'Sale'
        GROUP BY amount, description
        ORDER BY frequency DESC
        LIMIT 3
    """, (customer_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'suggestions': [
            {'amount': s['amount'], 'description': s['description']}
            for s in suggestions
        ]
    })

# AI Generate Description
@app.route('/ai-generate-description', methods=['POST'])
@login_required
def ai_generate_description():
    """AI generates transaction description"""
    data = request.json
    customer_id = data['customer_id']
    trans_type = data['type']
    amount = data['amount']
    
    # Check cooldown
    cooldown_check = check_ai_cooldown(f'desc_{customer_id}', 'description')
    if not cooldown_check['allowed']:
        return jsonify({
            'description': f"⏳ Cooldown active ({cooldown_check['remaining']}s remaining)"
        })
    
    api_key = get_setting('gemini_api_key')
    if not api_key:
        return jsonify({'description': 'AI not configured'})
    
    conn = get_db_conn()
    customer = conn.execute("SELECT name FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    
    # Get recent descriptions for context
    recent = conn.execute("""
        SELECT description FROM transactions
        WHERE customer_id = ? AND description IS NOT NULL
        ORDER BY transaction_date DESC LIMIT 5
    """, (customer_id,)).fetchall()
    
    conn.close()
    
    recent_desc = [r['description'] for r in recent if r['description']]
    
    prompt = f"""
    Generate a brief, professional transaction description for:
    - Customer: {customer['name']}
    - Type: {trans_type}
    - Amount: ₹{amount}
    
    Recent descriptions for context: {', '.join(recent_desc) if recent_desc else 'None'}
    
    Generate ONE short description (5-10 words max). No explanation, just the description.
    """
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result['candidates'][0]['content']['parts'][0]['text'].strip()
            # Remove quotes if present
            description = description.replace('"', '').replace("'", '')
            return jsonify({'description': description})
    except:
        pass
    
    return jsonify({'description': f'{trans_type} for {customer["name"]}'})

# Update transactions route to pass tax_rate
@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    conn = get_db_conn()
    
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        transaction_type = request.form['transaction_type']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        payment_mode = request.form.get('payment_mode', '')
        reference_number = request.form.get('reference_number', '')
        
        tax_rate = float(get_setting('tax_rate') or 18.0)
        tax_amount = 0
        total_amount = amount
        transaction_status = 'Paid' # Default for payments/refunds
        due_date = None

        if transaction_type == 'Sale/Credit':
            tax_amount = amount * (tax_rate / 100)
            total_amount = amount + tax_amount
            transaction_status = 'Unpaid'
            
            # Get customer's payment days limit for due date
            customer = conn.execute("SELECT payment_days_limit FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
            if customer:
                payment_days_limit = customer['payment_days_limit']
                due_date = (datetime.now() + timedelta(days=payment_days_limit)).strftime('%Y-%m-%d')

        elif transaction_type == 'Refund':
            # For refunds, tax might be negative or zero depending on business logic
            # For simplicity, we'll assume it's a direct refund of the amount
            total_amount = -amount # Represent refund as negative total
            transaction_status = 'Paid' # Refund is a completed action

        try:
            conn.execute("""
                INSERT INTO transactions (customer_id, transaction_type, amount, tax_amount, total_amount,
                                        description, transaction_date, due_date, status, payment_mode, reference_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, transaction_type, amount, tax_amount, total_amount,
                  description, datetime.now().strftime('%Y-%m-%d'), due_date, transaction_status, payment_mode, reference_number))
            conn.commit()
            flash(f'✅ {transaction_type} transaction recorded successfully!', 'success')
        except Exception as e:
            flash(f'❌ Error recording transaction: {str(e)}', 'error')
        
        conn.close()
        return redirect(url_for('transactions'))
    
    all_customers = conn.execute("SELECT customer_id, name, credit_limit FROM customers WHERE status='Active' ORDER BY name").fetchall()
    
    # Get outstanding balance for each customer
    customers_with_balance = []
    for customer in all_customers:
        outstanding = conn.execute("""
            SELECT COALESCE(SUM(due_amount), 0) as total
            FROM monthly_bills
            WHERE customer_id = ? AND status = 'Unpaid'
        """, (customer['customer_id'],)).fetchone()['total']
        
        customers_with_balance.append({
            'customer_id': customer['customer_id'],
            'name': customer['name'],
            'credit_limit': customer['credit_limit'],
            'outstanding_balance': outstanding
        })
    
    all_transactions = conn.execute("""
        SELECT t.*, c.name as customer_name 
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        ORDER BY t.transaction_date DESC
        LIMIT 100
    """).fetchall()
    
    tax_rate = float(get_setting('tax_rate') or 18.0)
    
    conn.close()
    return render_template('transactions.html', 
                         active_page='transactions',
                         customers=customers_with_balance,
                         transactions=all_transactions,
                         today=datetime.now().strftime('%Y-%m-%d'),
                         tax_rate=tax_rate,
                         format_currency=format_currency)
####################################################################

@app.route('/bills/generate', methods=['POST'])
@login_required
def generate_bills():
    conn = get_db_conn()
    month = request.form.get('month', datetime.now().strftime('%Y-%m'))
    tax_rate = float(get_setting('tax_rate') or 18.0)
    
    customers = conn.execute("SELECT * FROM customers WHERE status = 'Active'").fetchall()
    bills_generated = 0
    
    for customer in customers:
        # Check if bill already exists for this month
        existing = conn.execute("""
            SELECT COUNT(*) as cnt FROM monthly_bills 
            WHERE customer_id = ? AND bill_month = ?
        """, (customer['customer_id'], month)).fetchone()
        
        if existing['cnt'] > 0:
            continue
        
        unpaid_transactions = conn.execute("""
            SELECT SUM(amount) as subtotal, SUM(tax_amount) as tax
            FROM transactions
            WHERE customer_id = ? AND status = 'Unpaid' 
            AND strftime('%Y-%m', transaction_date) = ?
        """, (customer['customer_id'], month)).fetchone()
        
        subtotal = unpaid_transactions['subtotal'] or 0
        tax_amount = unpaid_transactions['tax'] or 0
        total_amount = subtotal + tax_amount
        
        if total_amount > 0:
            bill_number = generate_bill_number()
            bill_date = datetime.now().strftime('%Y-%m-%d')
            due_date = (datetime.now() + datetime.timedelta(days=customer['payment_days_limit'])).strftime('%Y-%m-%d')
            
            conn.execute("""
                INSERT INTO monthly_bills (customer_id, bill_number, bill_month, subtotal, tax_amount, 
                                         total_amount, due_amount, bill_date, due_date, sent_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer['customer_id'], bill_number, month, subtotal, tax_amount, 
                  total_amount, total_amount, bill_date, due_date, bill_date))
            
            # Send bill via email
            subject = f"📄 Monthly Bill - {month} | {bill_number}"
            body = generate_bill_email(customer, bill_number, month, subtotal, tax_amount, total_amount, due_date)
            send_email_async(customer['email'], subject, body)
            
            bills_generated += 1
    
    conn.commit()
    conn.close()
    flash(f'✅ {bills_generated} bills generated and sent for {month}', 'success')
    return redirect(url_for('bills'))

def generate_bill_email(customer, bill_number, month, subtotal, tax_amount, total_amount, due_date):
    """Generate professional bill email"""
    business_name = get_setting('business_name')
    business_address = get_setting('business_address')
    business_phone = get_setting('business_phone')
    business_email = get_setting('business_email')
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
        <div style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📄 INVOICE</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">{business_name}</p>
            </div>
            
            <!-- Bill Details -->
            <div style="padding: 30px;">
                <div style="display: table; width: 100%; margin-bottom: 30px;">
                    <div style="display: table-cell; width: 50%; vertical-align: top;">
                        <h3 style="margin: 0 0 10px 0; color: #333;">Bill To:</h3>
                        <p style="margin: 5px 0; color: #666;"><strong style="color: #333;">{customer['name']}</strong></p>
                        <p style="margin: 5px 0; color: #666;">{customer['email']}</p>
                        <p style="margin: 5px 0; color: #666;">{customer['phone']}</p>
                        {f'<p style="margin: 5px 0; color: #666;">{customer["address"]}</p>' if customer['address'] else ''}
                        {f'<p style="margin: 5px 0; color: #666;">GST: {customer["gst_number"]}</p>' if customer['gst_number'] else ''}
                    </div>
                    <div style="display: table-cell; width: 50%; vertical-align: top; text-align: right;">
                        <p style="margin: 5px 0; color: #666;"><strong>Invoice #:</strong> {bill_number}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>Date:</strong> {datetime.now().strftime('%d %b %Y')}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>Period:</strong> {month}</p>
                        <p style="margin: 5px 0; color: #dc2626;"><strong>Due Date:</strong> {due_date}</p>
                    </div>
                </div>
                
                <!-- Amount Breakdown -->
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background: #f9fafb; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #374151; color: white;">
                            <th style="padding: 15px; text-align: left;">Description</th>
                            <th style="padding: 15px; text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 15px; border-bottom: 1px solid #e5e7eb;">Subtotal</td>
                            <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; text-align: right;">{format_currency(subtotal)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 15px; border-bottom: 1px solid #e5e7eb;">Tax (GST)</td>
                            <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; text-align: right;">{format_currency(tax_amount)}</td>
                        </tr>
                        <tr style="background: #f3f4f6;">
                            <td style="padding: 20px;"><strong style="font-size: 18px;">Total Amount Due</strong></td>
                            <td style="padding: 20px; text-align: right;"><strong style="font-size: 24px; color: #059669;">{format_currency(total_amount)}</strong></td>
                        </tr>
                    </tbody>
                </table>
                
                <!-- Payment Instructions -->
                <div style="background: #dbeafe; border-left: 4px solid #3b82f6; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1e40af;">💳 Payment Instructions</h3>
                    <p style="margin: 5px 0; color: #1e3a8a;">Please make payment before <strong>{due_date}</strong></p>
                    <p style="margin: 5px 0; color: #1e3a8a;">Reference: <strong>{bill_number}</strong></p>
                </div>
                
                <!-- Footer -->
                <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 14px;">
                    <p style="margin: 5px 0;">{business_name}</p>
                    {f'<p style="margin: 5px 0;">{business_address}</p>' if business_address else ''}
                    {f'<p style="margin: 5px 0;">📞 {business_phone} | ✉️ {business_email}</p>' if business_phone or business_email else ''}
                    <p style="margin: 15px 0 5px 0; font-size: 12px;">Thank you for your business!</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/bills')
@login_required
def bills():
    conn = get_db_conn()
    
    all_bills = conn.execute("""
        SELECT b.*, c.name as customer_name, c.email
        FROM monthly_bills b
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.bill_date DESC
    """).fetchall()
    
    conn.close()
    return render_template('bills.html', 
                         active_page='bills', 
                         bills=all_bills,
                         today=datetime.now().strftime('%Y-%m-%d'),
                         current_month=datetime.now().strftime('%Y-%m'),
                         format_currency=format_currency)

@app.route('/ai-analysis/<int:customer_id>')
@login_required
def ai_analysis(customer_id):
    analysis = ai_analyze_customer(customer_id)
    return jsonify({'analysis': analysis})

@app.route('/ai-collection-strategy/<int:customer_id>')
@login_required
def ai_collection_strategy(customer_id):
    strategy = ai_generate_collection_strategy(customer_id)
    return jsonify({'strategy': strategy})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_db_conn()
    
    if request.method == 'POST':
        # Add extra 2FA check for settings page
        verify_code = request.form.get('verify_code')
        totp = pyotp.TOTP(app.config['TOTP_SECRET'])
        
        if not totp.verify(verify_code, valid_window=1):
            flash('❌ Invalid authentication code for settings change', 'error')
            return redirect(url_for('settings'))
        
        # Rest of settings update code...
        settings_keys = ['smtp_server', 'smtp_port', 'smtp_email', 'smtp_password', 
                        'gemini_api_key', 'business_name', 'business_address', 
                        'business_phone', 'business_email', 'business_gst', 'tax_rate',
                        'currency_symbol', 'bill_prefix', 'reminder_days_before', 
                        'reminder_days_after', 'business_logo_url']
        
        for key in settings_keys:
            value = request.form.get(key, '')
            conn.execute("UPDATE settings SET setting_value = ? WHERE setting_key = ?", (value, key))
        
        conn.commit()
        flash('✅ Settings saved successfully!', 'success')
        conn.close()
        return redirect(url_for('settings'))
    
    all_settings = {}
    settings_rows = conn.execute("SELECT * FROM settings").fetchall()
    for row in settings_rows:
        all_settings[row['setting_key']] = row['setting_value']
    
    conn.close()
    return render_template('settings.html', active_page='settings', settings=all_settings)
    
@app.route('/check-notifications')
@login_required
def check_notifications():
    """Manually trigger notification check"""
    check_overdue_payments()
    check_credit_limit_exceeded()
    flash('✅ Notification check completed! Emails sent to relevant customers.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/test-email')
@login_required
def test_email():
    """Test email configuration"""
    smtp_email = get_setting('smtp_email')
    if not smtp_email:
        flash('❌ Email not configured. Please set up SMTP settings.', 'error')
        return redirect(url_for('settings'))
    
    subject = "Test Email - Record Book System"
    body = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>✅ Email Configuration Test</h2>
        <p>Your email settings are working correctly!</p>
        <p>You can now send automated bills and notifications.</p>
    </body>
    </html>
    """
    
    send_email_async(smtp_email, subject, body)
    flash(f'✅ Test email sent to {smtp_email}. Please check your inbox.', 'success')
    return redirect(url_for('settings'))

@app.route('/export-ledger/<int:customer_id>')
@login_required
def export_ledger(customer_id):
    """Export customer ledger as CSV"""
    conn = get_db_conn()
    
    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    transactions = conn.execute("""
        SELECT transaction_date, transaction_type, description, amount, tax_amount, 
               total_amount, status, due_date 
        FROM transactions 
        WHERE customer_id = ? 
        ORDER BY transaction_date ASC
    """, (customer_id,)).fetchall()
    
    conn.close()
    
    # Create CSV data
    csv_data = f"Customer Ledger - {customer['name']}\n"
    csv_data += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    csv_data += "Date,Type,Description,Amount,Tax,Total,Status,Due Date\n"
    
    for trans in transactions:
        csv_data += f"{trans['transaction_date']},{trans['transaction_type']},{trans['description'] or ''},"
        csv_data += f"{trans['amount']},{trans['tax_amount']},{trans['total_amount']},{trans['status']},{trans['due_date'] or ''}\n"
    
    # Return as downloadable file
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"ledger_{customer['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    )

@app.route('/dashboard-stats')
@login_required
def dashboard_stats():
    """API endpoint for real-time dashboard stats"""
    conn = get_db_conn()
    
    stats = {
        'total_customers': conn.execute("SELECT COUNT(*) as c FROM customers WHERE status='Active'").fetchone()['c'],
        'total_unpaid': conn.execute("SELECT COALESCE(SUM(due_amount), 0) as t FROM monthly_bills WHERE status='Unpaid'").fetchone()['t'],
        'overdue_count': conn.execute("SELECT COUNT(*) as c FROM monthly_bills WHERE status='Unpaid' AND due_date < date('now')").fetchone()['c'],
        'this_month_revenue': conn.execute("SELECT COALESCE(SUM(paid_amount), 0) as t FROM monthly_bills WHERE strftime('%Y-%m', bill_date) = strftime('%Y-%m', 'now')").fetchone()['t']
    }
    
    conn.close()
    return jsonify(stats)
# Add after other imports
from functools import wraps
import hashlib

# New route for alerts page
@app.route('/alerts')
@login_required
def alerts():
    conn = get_db_conn()
    customers = conn.execute("""
        SELECT c.*, 
               COALESCE(SUM(CASE WHEN b.status = 'Unpaid' THEN b.due_amount ELSE 0 END), 0) as outstanding_balance
        FROM customers c
        LEFT JOIN monthly_bills b ON c.customer_id = b.customer_id
        GROUP BY c.customer_id
        HAVING outstanding_balance > 0
        ORDER BY outstanding_balance DESC
    """).fetchall()
    conn.close()
    
    return render_template('alerts.html', active_page='alerts', customers=customers, format_currency=format_currency)

# Generate AI alert emails
@app.route('/generate-alert-emails', methods=['POST'])
@login_required
def generate_alert_emails():
    data = request.json
    customers = data['customers']
    
    # Check cooldown
    cooldown_check = check_ai_cooldown('alert_system', 'bulk_alert')
    if not cooldown_check['allowed']:
        return jsonify({
            'cooldown': True,
            'remaining': cooldown_check['remaining']
        })
    
    api_key = get_setting('gemini_api_key')
    if not api_key:
        return jsonify({'error': 'AI not configured'})
    
    # Build comprehensive prompt
    customer_list = "\n".join([
        f"- {c['name']}: Outstanding ₹{c['outstanding']}, Email: {c['email']}"
        for c in customers
    ])
    
    prompt = f"""
    Create a polite, professional payment reminder email for Indian business customers.
    
    Customers to remind:
    {customer_list}
    
    Requirements:
    1. Polite and respectful tone
    2. Mention outstanding amount
    3. Request for payment
    4. Offer assistance if needed
    5. Professional closing
    6. Keep it brief (150-200 words)
    
    Format as HTML email body (use simple inline styles, no external CSS).
    Make it suitable for Indian business context.
    """
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            email_template = result['candidates'][0]['content']['parts'][0]['text']
            
            # Generate individual emails
            emails = {}
            for customer in customers:
                emails[customer['id']] = {
                    'to': customer['email'],
                    'subject': 'Payment Reminder - Outstanding Balance',
                    'body': email_template.replace('[Customer Name]', customer['name'])
                                         .replace('[Amount]', f"₹{customer['outstanding']}")
                }
            
            return jsonify({
                'success': True,
                'preview': email_template,
                'emails': emails
            })
    except Exception as e:
        return jsonify({'error': str(e)})

# Send alert emails with 2FA
@app.route('/send-alert-emails', methods=['POST'])
@login_required
def send_alert_emails():
    data = request.json
    code = data['code']
    emails = data['emails']
    
    # Verify TOTP
    totp = pyotp.TOTP(app.config['TOTP_SECRET'])
    if not totp.verify(code, valid_window=1):
        return jsonify({'success': False, 'error': 'Invalid authentication code'})
    
    # Send emails
    sent_count = 0
    for email_data in emails.values():
        send_email_async(email_data['to'], email_data['subject'], email_data['body'])
        sent_count += 1
    
    return jsonify({'success': True, 'sent': sent_count})

#########################################################################################
# --- Add this new import at the top of app.py ---
import cli_logic

@app.route('/web-cli', methods=['GET', 'POST'])
@login_required
def web_cli():
    output = "Welcome to the Web CLI. Type 'help' for commands.\n"
    
    if request.method == 'POST':
        command_text = request.form.get('command', '').strip()
        parts = command_text.split()
        
        if not parts:
            output = "Please enter a command."
            return render_template('web_cli.html', output=output)
        
        cmd = parts[0].lower()
        
        # --- This is where we call the logic functions ---
        try:
            if cmd == 'help':
                output = (
                    "Available Commands:\n"
                    "  list         - View all customers\n"
                    "  find [email] - Find a customer by email\n"
                    "  toggle [id]  - Activate/Deactivate a customer\n"
                    "  edit [id] [field] [new_value] - Edit customer details\n"
                    "  edit-trans [id] [field] [new_value] - Edit transaction details\n"
                    "  edit-bill [id] [field] [new_value] - Edit monthly bill details\n"
                )
            
            elif cmd == 'list':
                customers = cli_logic.get_all_customers()
                output = "--- All Customers ---\n"
                for c in customers:
                    output += f"ID: {c['customer_id']} | Name: {c['name']} | Status: {c['status']}\n"
            
            elif cmd == 'toggle':
                customer_id = int(parts[1])
                output = cli_logic.toggle_customer_status(customer_id)
            
            elif cmd == 'find':
                email = parts[1]
                customer = cli_logic.find_customer_by_email(email)
                if customer:
                    output = "--- Customer Found ---\n"
                    # Convert row to a simple dict to iterate
                    output += json.dumps(dict(customer), indent=2)
                else:
                    output = f"No customer found with email: {email}"
            
            elif cmd == 'edit':
                if len(parts) < 4:
                    output = "Error: 'edit' command needs 3 arguments.\n"
                    output += "Syntax: edit [id] [field] [new_value]"
                else:
                    customer_id = int(parts[1])
                    field = parts[2].lower()
                    
                    # Re-join all remaining parts to form the new value
                    # This allows for values with spaces, like an address
                    new_value = " ".join(parts[3:])
                    
                    # Remove surrounding quotes if user added them
                    if new_value.startswith('"') and new_value.endswith('"'):
                        new_value = new_value[1:-1]
                        
                    output = cli_logic.edit_customer_details(customer_id, field, new_value)
            
            elif cmd == 'edit-trans':
                if len(parts) < 4:
                    output = "Error: 'edit-trans' command needs 3 arguments.\n"
                    output += "Syntax: edit-trans [id] [field] [new_value]"
                else:
                    transaction_id = int(parts[1])
                    field = parts[2].lower()
                    
                    # Re-join all remaining parts
                    new_value = " ".join(parts[3:])
                    
                    # Remove surrounding quotes if user added them
                    if new_value.startswith('"') and new_value.endswith('"'):
                        new_value = new_value[1:-1]
                        
                    output = cli_logic.edit_transaction_details(transaction_id, field, new_value)
            
            elif cmd == 'edit-bill':
                if len(parts) < 4:
                    output = "Error: 'edit-bill' command needs 3 arguments.\n"
                    output += "Syntax: edit-bill [id] [field] [new_value]"
                else:
                    bill_id = int(parts[1])
                    field = parts[2].lower()
                    
                    # Re-join all remaining parts
                    new_value = " ".join(parts[3:])
                    
                    # Remove surrounding quotes if user added them
                    if new_value.startswith('"') and new_value.endswith('"'):
                        new_value = new_value[1:-1]
                        
                    output = cli_logic.edit_bill_details(bill_id, field, new_value)

            else:
                output = f"Error: Command '{cmd}' not recognized."
                
        except IndexError:
            output = f"Error: Command '{cmd}' requires more arguments."
        except ValueError:
            output = "Error: Invalid argument. Expected a number."
        except Exception as e:
            output = f"An unexpected error occurred: {e}"
            
    return render_template('web_cli.html', output=output, active_page='web-cli')
#########################################################################################

# --- Main Execution ---
if __name__ == "__main__":
    initialize_database(app.config['DATABASE'])
    print("\n" + "="*50)
    print("🚀 Indian Record Book System Starting...")
    print("="*50)
    print(f"📍 Access URL: http://127.0.0.1:5000")
    print(f"🔐 Setup 2FA: http://127.0.0.1:5000/setup-2fa")
    print(f"🔑 Login: http://127.0.0.1:5000/login")
    print("="*50 + "\n")
    
    # Start background task for periodic notification checks
    def background_notifier():
        while True:
            time.sleep(3600)  # Check every hour
            try:
                check_overdue_payments()
                check_credit_limit_exceeded()
            except Exception as e:
                print(f"Background task error: {e}")
    
    Thread(target=background_notifier, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
