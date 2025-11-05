import sqlite3

DB_FILE = "record_book.db"

def get_db_conn():
    """Helper function to get a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_customers():
    """
    Fetches all customers.
    Returns a list of customer rows (as dictionaries).
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, name, email, phone, status FROM customers ORDER BY name")
    customers = cursor.fetchall()
    conn.close()
    return customers

def get_customer_by_id(customer_id):
    """
    Fetches a single customer.
    Returns a customer row or None.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def toggle_customer_status(customer_id):
    """
    Toggles a customer's status between 'Active' and 'Inactive'.
    Returns a success or error message string.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # First, get the customer to check their current status
    customer = get_customer_by_id(customer_id)
    if not customer:
        conn.close()
        return f"Error: No customer found with ID: {customer_id}"

    # Determine the new status
    new_status = "Active" if customer['status'] == 'Inactive' else 'Inactive'
    
    try:
        cursor.execute("UPDATE customers SET status = ? WHERE customer_id = ?", (new_status, customer_id))
        conn.commit()
        conn.close()
        return f"Success: Customer {customer['name']} (ID: {customer_id}) status changed to {new_status}."
    except Exception as e:
        conn.close()
        return f"Error: Could not update customer. {e}"

def find_customer_by_email(email):
    """
    Finds a customer by email.
    Returns the customer row or None.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def edit_transaction_details(transaction_id, field_to_edit, new_value):
    """
    Edits a single field for a transaction.
    Returns a success or error message string.
    """
    # Whitelist of allowed fields.
    # We block changing 'customer_id' or 'transaction_type' to protect data integrity.
    allowed_fields = [
        'amount', 'tax_amount', 'total_amount', 'description', 
        'transaction_date', 'due_date', 'status', 
        'payment_mode', 'reference_number'
    ]
    
    field_to_edit = field_to_edit.lower()
    if field_to_edit not in allowed_fields:
        return f"Error: Editing '{field_to_edit}' is not allowed on transactions."

    conn = get_db_conn()
    cursor = conn.cursor()
    
    # We can safely use f-string for the field name
    # *because* we checked it against the 'allowed_fields' list.
    sql_query = f"UPDATE transactions SET {field_to_edit} = ? WHERE transaction_id = ?"
    
    try:
        cursor.execute(sql_query, (new_value, transaction_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return f"Error: No transaction found with ID: {transaction_id}"
            
        conn.commit()
        conn.close()
        return f"Success: Transaction {transaction_id}'s {field_to_edit} updated to '{new_value}'."
    
    except sqlite3.IntegrityError as e:
        conn.close()
        return f"Database Error: {e}. Check if the value is valid (e.g., date format)."
    except Exception as e:
        conn.close()
        return f"Error: Could not update transaction. {e}"

def edit_customer_details(customer_id, field_to_edit, new_value):
    """
    Edits a single field for a customer.
    Returns a success or error message string.
    """
    allowed_fields = [
        'name', 'email', 'phone', 'address', 'gst_number',
        'credit_limit', 'payment_days_limit', 'status', 'reminder_preference'
    ]
    
    field_to_edit = field_to_edit.lower()
    if field_to_edit not in allowed_fields:
        return f"Error: Editing '{field_to_edit}' is not allowed on customers."

    conn = get_db_conn()
    cursor = conn.cursor()
    
    sql_query = f"UPDATE customers SET {field_to_edit} = ? WHERE customer_id = ?"
    
    try:
        cursor.execute(sql_query, (new_value, customer_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return f"Error: No customer found with ID: {customer_id}"
            
        conn.commit()
        conn.close()
        return f"Success: Customer {customer_id}'s {field_to_edit} updated to '{new_value}'."
    
    except sqlite3.IntegrityError as e:
        conn.close()
        return f"Database Error: {e}. Check if the value is valid (e.g., unique email)."
    except Exception as e:
        conn.close()
        return f"Error: Could not update customer. {e}"

def edit_bill_details(bill_id, field_to_edit, new_value):
    """
    Edits a single field for a monthly bill.
    Returns a success or error message string.
    """
    allowed_fields = [
        'bill_month', 'subtotal', 'tax_amount', 'total_amount', 
        'paid_amount', 'due_amount', 'bill_date', 'due_date', 
        'status', 'sent_date', 'last_reminder_date', 'reminder_count'
    ]
    
    field_to_edit = field_to_edit.lower()
    if field_to_edit not in allowed_fields:
        return f"Error: Editing '{field_to_edit}' is not allowed on monthly bills."

    conn = get_db_conn()
    cursor = conn.cursor()
    
    sql_query = f"UPDATE monthly_bills SET {field_to_edit} = ? WHERE bill_id = ?"
    
    try:
        cursor.execute(sql_query, (new_value, bill_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return f"Error: No bill found with ID: {bill_id}"
            
        conn.commit()
        conn.close()
        return f"Success: Bill {bill_id}'s {field_to_edit} updated to '{new_value}'."
    
    except sqlite3.IntegrityError as e:
        conn.close()
        return f"Database Error: {e}. Check if the value is valid (e.g., date format)."
    except Exception as e:
        conn.close()
        return f"Error: Could not update bill. {e}"