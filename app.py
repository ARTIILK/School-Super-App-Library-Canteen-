import customtkinter as ctk # This is no longer needed
import sqlite3
from tkinter import ttk  # This is no longer needed
from tkinter import messagebox  # This is no longer needed
import os
import datetime

# --- NEW IMPORTS for Web App & Advanced Analytics ---
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Not needed for web
import io
import base64

# --- Database Setup (Same as before) ---
DB_FILE = "super_app.db"

def initialize_database():
    """Creates the database file and all necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # --- Library Tables ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            student_id TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Issued',
            FOREIGN KEY (book_id) REFERENCES books (book_id)
        )
    """)
    
    # --- Canteen Tables ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canteen_sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
        )
    """)
    
    conn.commit()
    conn.close()

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Helper function to get DB connection ---
def get_db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn

# --- Main Dashboard Route ---
@app.route('/')
def index():
    # This will be our main dashboard
    return render_template('analytics.html', active_page='analytics', graph_canteen=get_canteen_graph(), graph_library=get_library_graph())

# --- Library Routes ---
@app.route('/library', methods=['GET', 'POST'])
def library():
    conn = get_db_conn()
    
    if request.method == 'POST':
        # Logic to add a new book
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']
        
        if title and author and quantity:
            try:
                conn.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
                             (title, author, int(quantity)))
                conn.commit()
            except Exception as e:
                print(f"Error adding book: {e}") # Show error to user
        
        conn.close()
        return redirect(url_for('library'))

    # GET Request: Load and display all books
    books_cursor = conn.execute("SELECT * FROM books ORDER BY title")
    books = books_cursor.fetchall()
    conn.close()
    return render_template('library.html', active_page='library', books=books)

# --- Canteen Routes ---
@app.route('/canteen', methods=['GET', 'POST'])
def canteen():
    conn = get_db_conn()
    
    if request.method == 'POST':
        # Logic to add a new menu item
        name = request.form['name']
        price = request.form['price']
        
        if name and price:
            try:
                conn.execute("INSERT INTO menu_items (name, price) VALUES (?, ?)",
                             (name, float(price)))
                conn.commit()
            except Exception as e:
                print(f"Error adding item: {e}") # Show error to user

        conn.close()
        return redirect(url_for('canteen'))

    # GET Request: Load and display all menu items
    menu_cursor = conn.execute("SELECT * FROM menu_items ORDER BY name")
    menu_items = menu_cursor.fetchall()
    conn.close()
    return render_template('canteen.html', active_page='canteen', menu_items=menu_items)


# --- Analytics Routes & Functions ---
@app.route('/analytics')
def analytics():
    # This page will show the graphs
    canteen_graph_data = get_canteen_graph()
    library_graph_data = get_library_graph()
    return render_template('analytics.html', active_page='analytics', graph_canteen=canteen_graph_data, graph_library=library_graph_data)

def get_canteen_graph():
    try:
        conn = get_db_conn()
        canteen_query = """
            SELECT mi.name, SUM(cs.quantity) as total_sold
            FROM canteen_sales cs
            JOIN menu_items mi ON cs.item_id = mi.item_id
            GROUP BY cs.item_id
            ORDER BY total_sold DESC
        """
        df_canteen = pd.read_sql_query(canteen_query, conn)
        conn.close()

        if df_canteen.empty:
            return None

        plt.figure(figsize=(6, 5), facecolor="#1f2937") # Match dark theme
        ax = df_canteen.plot(kind='bar', x='name', y='total_sold', legend=False, color="#3b82f6")
        
        # Style for dark mode
        ax.set_title("Top Selling Canteen Items", color="white")
        ax.set_ylabel("Quantity Sold", color="white")
        ax.set_xlabel("Item", color="white")
        ax.set_facecolor("#1f2937")
        ax.tick_params(colors="white")
        ax.spines['bottom'].set_color("white")
        ax.spines['left'].set_color("white")
        ax.spines['top'].set_color("none")
        ax.spines['right'].set_color("none")
        
        plt.tight_layout()

        # Save graph to memory and encode as base64
        img = io.BytesIO()
        plt.savefig(img, format='png', transparent=True)
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return f"data:image/png;base64,{graph_url}"
        
    except Exception as e:
        print(f"Canteen graph error: {e}")
        return None

def get_library_graph():
    try:
        conn = get_db_conn()
        library_query = """
            SELECT b.title, COUNT(bi.book_id) as issue_count
            FROM book_issues bi
            JOIN books b ON bi.book_id = b.book_id
            GROUP BY bi.book_id
            ORDER BY issue_count DESC
        """
        df_library = pd.read_sql_query(library_query, conn)
        conn.close()

        if df_library.empty:
            return None

        plt.figure(figsize=(6, 5), facecolor="#1f2937") # Match dark theme
        ax = df_library.plot(kind='barh', x='title', y='issue_count', legend=False, color="#059669")
        
        # Style for dark mode
        ax.set_title("Most Issued Books", color="white")
        ax.set_xlabel("Times Issued", color="white")
        ax.set_ylabel("Book Title", color="white")
        ax.set_facecolor("#1f2937")
        ax.tick_params(colors="white")
        ax.spines['bottom'].set_color("white")
        ax.spines['left'].set_color("white")
        ax.spines['top'].set_color("none")
        ax.spines['right'].set_color("none")
        ax.invert_yaxis()
        
        plt.tight_layout()

        # Save graph to memory and encode as base64
        img = io.BytesIO()
        plt.savefig(img, format='png', transparent=True)
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return f"data:image/png;base64,{graph_url}"

    except Exception as e:
        print(f"Library graph error: {e}")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    initialize_database()
    app.run(debug=True) # debug=True helps you see errors
