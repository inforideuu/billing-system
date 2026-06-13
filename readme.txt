# Billing System - Setup & Run Guide

Follow these simple steps to run this Django project on your system using VS Code.

## Prerequisites
1. Make sure **Python** is installed on your computer.
2. Make sure your local database server is running:
   - Type: PostgreSQL
   - Name: `retail_billing_db`
   - User: `postgres`
   - Password: `annamalai238`

---

## Steps to Run in VS Code

### 1. Open Project
Open the project folder in Visual Studio Code (`File > Open Folder...`).

### 2. Open Terminal
Open a new Terminal inside VS Code (`Terminal > New Terminal` or press `Ctrl + ` ` `).

### 3. Activate Virtual Environment
The project includes a configured virtual environment folder (`venv`). Activate it using:

**On Windows Powershell:**
```powershell
.\venv\Scripts\activate
```

**On Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

### 4. Install Dependencies
Ensure required packages (including new ones like Pillow) are up to date:
```bash
pip install django psycopg2-binary cryptography pillow sqlparse
```

### 5. Apply Database Migrations (Optional but Recommended)
To ensure all database tables and recent updates are set up:
```bash
python manage.py migrate
```

### 6. Start the Server
Execute the development server run command:
```bash
python manage.py runserver
```

### 7. View in Browser
Click the link outputted in terminal or open your browser manually to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---
*Project verified running and mobile-friendly.*
