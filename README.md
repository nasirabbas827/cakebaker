# cakebaker_final

A web‑based bakery management system that lets administrators manage cake inventory, track orders, and view sales records, while customers can browse cakes, customize orders, and manage their shopping cart.

---

## Overview

`cakebaker_final` is a lightweight Flask application (HTML front‑end with Python back‑end) designed for small‑to‑medium bakeries. It provides:

* An admin dashboard for CRUD operations on cake products.  
* Order management with detailed views for both customers and staff.  
* Simple sales reporting.  
* A responsive UI built with HTML/CSS.

---

## Features

| ✅ | Feature |
|---|---------|
| **Admin** | Login, add/edit/delete cakes, view orders, see order details, generate sales records. |
| **Customer** | Browse cakes, add to cart, customize requests, place orders, view order history. |
| **Data** | SQLite database (`Database/homebakers_db.sql`) with tables for users, cakes, orders, and custom requests. |
| **Responsive UI** | Clean, mobile‑friendly templates using plain HTML & CSS. |
| **File Uploads** | Supports image uploads for cake listings (`static/uploads/`). |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.9+, Flask |
| **Database** | SQLite (SQL script provided) |
| **Frontend** | HTML5, CSS3 |
| **Templates** | Jinja2 (Flask templating) |
| **Static Assets** | CSS (`static/css/style.css`), images (`static/uploads/`) |

---

## Installation

> **Prerequisite:** Python 3.8+ and `git` installed on your machine.

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/cakebaker_final.git
   cd cakebaker_final
   ```

2. **Create a virtual environment & install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt   # (If a requirements file is not present, install Flask manually)
   pip install Flask
   ```

3. **Set up the database**

   ```bash
   # Ensure SQLite is installed (usually bundled with Python)
   sqlite3 homebakers_db.sqlite < Database/homebakers_db.sql
   ```

4. **Configure environment variables**

   Create a `.env` file (or export variables in your shell) with at least the following:

   ```env
   FLASK_APP=main.py
   FLASK_ENV=development
   SECRET_KEY=YOUR_OWN_API_KEY   # Replace with a strong secret key
   ```

5. **Run the application**

   ```bash
   flask run
   ```

   The app will be accessible at `http://127.0.0.1:5000/`.

---

## Usage

### Admin

1. Navigate to `/adminlogin` and log in with the admin credentials created in the database.  
2. Use the dashboard to:
   * **Add / Edit Cakes** – upload images, set price, description, etc.  
   * **View Orders** – see a list of all orders, click for details.  
   * **Sales Records** – generate simple sales reports.

### Customer

1. Visit the home page (`/`) to browse available cakes.  
2. Click **Add to Cart** on any cake, then go to `/cart` to review selections.  
3. Proceed to **Make Order** (`/make_order`) to finalize the purchase.  
4. After ordering,