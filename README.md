School Super App (Library & Canteen)

This is a full-stack web application built with Python (Flask) to manage a school's library and canteen. It provides a simple, modern web interface for managing books and menu items, and features an advanced analytics dashboard to visualize data.

This project is designed as a CBSE Class 12th Computer Science project, demonstrating skills in Python, web development, database management, and data visualization.

🚀 Features

Modular Design: A clean, multi-page application with a persistent navigation sidebar.

Library Management:

Add new books (title, author, quantity) to the database.

View a real-time list of all books in the library.

Canteen Management:

Add new menu items (name, price) to the database.

View a real-time, formatted list of all items available in the canteen.

Advanced Analytics Dashboard:

Dynamically generates graphs using Pandas and Matplotlib.

Visualizes "Top Selling Canteen Items" with a bar chart.

Visualizes "Most Issued Books" with a horizontal bar chart.

Interface styled for a modern, dark-mode theme.

💻 Technologies Used

Backend:

Python 3

Flask: A lightweight web framework for running the server and handling all logic.

SQLite3: A file-based database (part of the Python standard library) for all data storage.

Data & Analytics:

Pandas: For querying the database and preparing data for plotting.

Matplotlib: For generating the data visualization graphs.

Frontend:

HTML5: For the structure of all web pages.

Tailwind CSS: For all styling, providing a modern, responsive, utility-first design.

Jinja2: Flask's templating engine for dynamically inserting Python data into the HTML pages.

📁 Project Structure

/your_project_folder/
│
├── app.py           (Your main Flask application file)
│
├── templates/       (Folder for all HTML files)
│   │
│   ├── layout.html      (The base layout/sidebar)
│   ├── analytics.html   (The analytics page)
│   ├── library.html     (The library page)
│   └── canteen.html     (The canteen page)
│
├── super_app.db     (The SQLite database file, created automatically)
│
└── README.md        (This file!)


⚙️ Setup and Installation

1. Prerequisites

Python 3.x installed.

pip (Python's package installer).

2. Install Dependencies

Open your terminal and run the following command to install the required Python libraries:

pip install Flask pandas matplotlib


3. Database Initialization

The database (super_app.db) and all its tables will be created automatically in the same folder as app.py when you run the application for the first time.

🏃 How to Run the Application

Open your terminal.

Navigate to the project folder (the one containing app.py).

Run the application with the following command:

python app.py


You will see an output like this:

 * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)


Open your web browser (like Chrome, Firefox, or Brave) and go to the following address:

http://127.0.0.1:5000

The "School Super App" will now be live in your browser.
