from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'homebakers_db'

mysql = MySQL(app)

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    # Handle search functionality
    search_query = request.form.get('search_query', '')
    price_min = request.form.get('price_min', '')
    price_max = request.form.get('price_max', '')
    category = request.form.get('category', '')
    size = request.form.get('size', '')

    cur = mysql.connection.cursor()

    # Fetch all unique categories for the dropdown
    cur.execute("SELECT DISTINCT categoryname FROM Cakes")
    categories = cur.fetchall()

    # Constructing the query dynamically based on search criteria
    query = "SELECT * FROM Cakes WHERE availability = 'Available'"
    params = []

    if search_query:
        query += " AND (name LIKE %s OR description LIKE %s)"
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    if price_min:
        query += " AND price >= %s"
        params.append(price_min)
    
    if price_max:
        query += " AND price <= %s"
        params.append(price_max)
    
    if category:
        query += " AND categoryname = %s"
        params.append(category)

    if size:
        query += " AND size = %s"
        params.append(size)

    cur.execute(query, params)
    cakes = cur.fetchall()
    cur.close()

    return render_template('index.html', cakes=cakes, categories=categories)


# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']  # Not hashed as requested
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, fullname, email, password_hash) VALUES (%s, %s, %s, %s)", 
                    (username, fullname, email, password))
        mysql.connection.commit()
        cur.close()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['user_id'] = user[0]  # Assuming the first field is the user ID
            session['username'] = user[1]  # Assuming the second field is the username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    # Handle search functionality
    search_query = request.form.get('search_query', '')
    price_min = request.form.get('price_min', '')
    price_max = request.form.get('price_max', '')
    category = request.form.get('category', '')
    size = request.form.get('size', '')

    cur = mysql.connection.cursor()

    # Fetch all unique categories for the dropdown
    cur.execute("SELECT DISTINCT categoryname FROM Cakes")
    categories = cur.fetchall()

    # Constructing the query dynamically based on search criteria
    query = "SELECT * FROM Cakes WHERE availability = 'Available'"
    params = []

    if search_query:
        query += " AND (name LIKE %s OR description LIKE %s)"
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    if price_min:
        query += " AND price >= %s"
        params.append(price_min)
    
    if price_max:
        query += " AND price <= %s"
        params.append(price_max)
    
    if category:
        query += " AND categoryname = %s"
        params.append(category)

    if size:
        query += " AND size = %s"
        params.append(size)

    cur.execute(query, params)
    cakes = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', username=session['username'], cakes=cakes, categories=categories)

# Add to Cart route
@app.route('/add_to_cart/<int:cake_id>', methods=['POST'])
def add_to_cart(cake_id):
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))
    
    quantity = request.form.get('quantity', 1)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Cart (user_id, cake_id, quantity, added_at) VALUES (%s, %s, %s, NOW())", 
                (session['user_id'], cake_id, quantity))
    mysql.connection.commit()
    cur.close()

    flash('Cake added to cart successfully!', 'success')
    return redirect(url_for('dashboard'))

# View Cart route
@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.cart_id, c.quantity, c.added_at, ca.name, ca.price 
        FROM Cart c 
        JOIN Cakes ca ON c.cake_id = ca.cake_id 
        WHERE c.user_id = %s
    """, (session['user_id'],))
    cart_items = cur.fetchall()
    cur.close()

    # Calculate grand total
    grand_total = sum(item[1] * item[4] for item in cart_items) if cart_items else 0

    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

# Update Cart route
@app.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    quantity = request.form.get('quantity', 1)

    cur = mysql.connection.cursor()
    cur.execute("UPDATE Cart SET quantity = %s WHERE cart_id = %s", (quantity, cart_id))
    mysql.connection.commit()
    cur.close()

    flash('Cart updated successfully!', 'success')
    return redirect(url_for('view_cart'))

# Remove From Cart route
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Cart WHERE cart_id = %s", (cart_id,))
    mysql.connection.commit()
    cur.close()

    flash('Item removed from cart successfully!', 'success')
    return redirect(url_for('view_cart'))


@app.route('/make_order', methods=['GET', 'POST'])
def make_order():
    if 'user_id' not in session:
        flash('Please log in to make an order.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        address = request.form['address']
        payment_method = request.form['payment_method']

        # Get cart items for the user
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.cake_id, c.quantity, ca.price 
            FROM Cart c 
            JOIN Cakes ca ON c.cake_id = ca.cake_id 
            WHERE c.user_id = %s
        """, (session['user_id'],))
        cart_items = cur.fetchall()
        cur.close()

        # Calculate total amount
        total_amount = sum(item[1] * item[2] for item in cart_items)  # quantity * price

        # Insert order into Orders table
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Orders (user_id, address, order_date, order_status, total_amount, payment_status, payment_method) 
            VALUES (%s, %s, NOW(), 'Pending', %s, 'Pending', %s)
        """, (session['user_id'], address, total_amount, payment_method))
        mysql.connection.commit()
        order_id = cur.lastrowid

        # Insert order items into OrderItems table
        for item in cart_items:
            cur.execute("""
                INSERT INTO OrderItems (order_id, cake_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, item[0], item[1], item[2]))
        mysql.connection.commit()
        cur.close()

        # Clear cart after order
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Cart WHERE user_id = %s", (session['user_id'],))
        mysql.connection.commit()
        cur.close()

        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('view_orders'))

    # GET request: show order form with cart items
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.cake_id, c.quantity, ca.name, ca.price 
        FROM Cart c 
        JOIN Cakes ca ON c.cake_id = ca.cake_id 
        WHERE c.user_id = %s
    """, (session['user_id'],))
    cart_items = cur.fetchall()
    cur.close()

    return render_template('make_order.html', cart_items=cart_items)

@app.route('/view_orders')
def view_orders():
    if 'user_id' not in session:
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.order_id, o.order_date, o.total_amount, o.order_status, 
               o.payment_status, o.payment_method 
        FROM Orders o 
        WHERE o.user_id = %s
    """, (session['user_id'],))

    orders = cur.fetchall()
    cur.close()

    return render_template('view_orders.html', orders=orders)


@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    if 'user_id' not in session:
        flash('Please log in to view order details.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT oi.order_item_id, c.name, oi.quantity, oi.price 
        FROM OrderItems oi 
        JOIN Cakes c ON oi.cake_id = c.cake_id 
        WHERE oi.order_id = %s
    """, (order_id,))
    order_items = cur.fetchall()
    cur.close()

    return render_template('order_details.html', order_items=order_items, order_id=order_id)


@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if 'user_id' not in session:
        flash('Please log in to delete an order.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Orders WHERE order_id = %s AND user_id = %s", (order_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Order deleted successfully!', 'success')
    return redirect(url_for('view_orders'))

from flask import request, flash, redirect, url_for
import os
from datetime import datetime

@app.route('/pay_order/<int:order_id>', methods=['POST'])
def pay_order(order_id):
    if 'user_id' not in session:
        flash('Please log in to pay for an order.', 'warning')
        return redirect(url_for('login'))

    # Handle file upload
    if 'transaction_picture' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('view_orders'))

    file = request.files['transaction_picture']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('view_orders'))

    # Allow only certain file extensions
    if file and allowed_file(file.filename):
        # Save the file to a directory
        filename = secure_filename(file.filename)
        file_path = os.path.join('static/uploads', filename)  # Adjust the path as necessary
        file.save(file_path)

        # Database operations
        cur = mysql.connection.cursor()

        # Update the Orders table
        cur.execute("""
            UPDATE Orders 
            SET payment_status = 'Paid', order_status = 'Confirmed' 
            WHERE order_id = %s AND user_id = %s
        """, (order_id, session['user_id']))
        
        # Insert into Transactions table
        cur.execute("""
            INSERT INTO Transactions (order_id, transaction_date, transaction_picture, amount)
            VALUES (%s, %s, %s, (SELECT total_amount FROM Orders WHERE order_id = %s))
        """, (order_id, datetime.now(), filename, order_id))

        mysql.connection.commit()
        cur.close()

        flash('Payment processed successfully!', 'success')
    else:
        flash('Invalid file type', 'danger')

    return redirect(url_for('view_orders'))

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/customization_request/<int:order_id>', methods=['GET', 'POST'])
def customization_request(order_id):
    if 'user_id' not in session:
        flash('Please log in to request customization.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Handle new customization request
    if request.method == 'POST':
        size = request.form['size']
        design_details = request.form['design_details']
        additional_description = request.form['additional_description']

        cur.execute("""
            INSERT INTO CustomizationRequests (order_id, size, design_details, additional_description, created_at) 
            VALUES (%s, %s, %s, %s, NOW())
        """, (order_id, size, design_details, additional_description))
        mysql.connection.commit()

        flash('Customization request submitted successfully!', 'success')
        return redirect(url_for('view_orders'))

    # Fetch existing customization requests for the order
    cur.execute("SELECT * FROM CustomizationRequests WHERE order_id = %s", (order_id,))
    customization_requests = cur.fetchall()

    cur.close()

    return render_template('customization_request.html', order_id=order_id, customization_requests=customization_requests)

# Route for deleting a customization request
@app.route('/delete_customization/<int:request_id>', methods=['POST'])
def delete_customization(request_id):
    if 'user_id' not in session:
        flash('Please log in to delete a customization request.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM CustomizationRequests WHERE request_id = %s", (request_id,))
    mysql.connection.commit()
    cur.close()

    flash('Customization request deleted successfully!', 'success')
    return redirect(url_for('view_orders'))



# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# Admin login route
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()
        cur.close()
        
        if admin:
            session['admin_id'] = admin[0]  # Assuming first column is admin ID
            session['admin_username'] = admin[1]  # Assuming second column is username
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')

    return render_template('admin/adminlogin.html')

# Admin homepage route
@app.route('/admin/home')
def admin_home():
    if 'admin_id' not in session:
        flash('Please log in as admin to access this page.', 'warning')
        return redirect(url_for('adminlogin'))
    
    return render_template('admin/home.html')

# Admin logout route
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin has been logged out.', 'info')
    return redirect(url_for('adminlogin'))


import os
from werkzeug.utils import secure_filename

# Path for saving images
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Route for adding cakes
@app.route('/admin/add_cake', methods=['GET', 'POST'])
def add_cake():
    if request.method == 'POST':
        categoryname = request.form['categoryname']
        name = request.form['name']
        description = request.form['description']
        size = request.form['size']
        price = request.form['price']
        availability = request.form['availability']
        
        # Handling the image upload
        image = request.files['image']
        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
        
        # Insert cake data into the Cakes table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Cakes (categoryname, name, description, size, price, image, availability) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (categoryname, name, description, size, price, image_filename, availability))
        mysql.connection.commit()
        cur.close()

        flash('Cake added successfully!', 'success')
        return redirect(url_for('view_cakes'))

    return render_template('admin/add_cake.html')

# Route for viewing all cakes
@app.route('/admin/view_cakes')
def view_cakes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Cakes")
    cakes = cur.fetchall()
    cur.close()
    return render_template('admin/view_cakes.html', cakes=cakes)

# Route for deleting a cake
@app.route('/admin/delete_cake/<int:cake_id>')
def delete_cake(cake_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Cakes WHERE cake_id = %s", (cake_id,))
    mysql.connection.commit()
    cur.close()
    flash('Cake deleted successfully!', 'success')
    return redirect(url_for('view_cakes'))

# Route for editing a cake (GET the current data and POST the update)
@app.route('/admin/edit_cake/<int:cake_id>', methods=['GET', 'POST'])
def edit_cake(cake_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Cakes WHERE cake_id = %s", (cake_id,))
    cake = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        categoryname = request.form['categoryname']
        name = request.form['name']
        description = request.form['description']
        size = request.form['size']
        price = request.form['price']
        availability = request.form['availability']

        # Handle image upload (optional)
        image = request.files['image']
        image_filename = cake[6]  # Use the existing image if no new image is uploaded

        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)

        # Update cake data in the Cakes table
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Cakes
            SET categoryname = %s, name = %s, description = %s, size = %s, price = %s, image = %s, availability = %s
            WHERE cake_id = %s
        """, (categoryname, name, description, size, price, image_filename, availability, cake_id))
        mysql.connection.commit()
        cur.close()

        flash('Cake updated successfully!', 'success')
        return redirect(url_for('view_cakes'))

    return render_template('admin/edit_cake.html', cake=cake)

@app.route('/admin/orders', methods=['GET', 'POST'])
def admin_orders():
    if 'admin_id' not in session:
        flash('Please log in as admin to access this page.', 'warning')
        return redirect(url_for('adminlogin'))

    cur = mysql.connection.cursor()

    # Fetch all orders
    cur.execute("""
        SELECT o.order_id, o.user_id, o.order_date, o.total_amount, o.order_status, 
               o.payment_status, o.payment_method 
        FROM Orders o
    """)
    orders = cur.fetchall()

    # Update order status if a POST request is made
    if request.method == 'POST':
        order_id = request.form['order_id']
        new_status = request.form['order_status']

        cur.execute("UPDATE Orders SET order_status = %s WHERE order_id = %s", (new_status, order_id))
        mysql.connection.commit()

        flash('Order status updated successfully!', 'success')
        return redirect(url_for('admin_orders'))

    cur.close()

    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/order_details/<int:order_id>')
def view_order_details(order_id):
    if 'admin_id' not in session:
        flash('Please log in as admin to access this page.', 'warning')
        return redirect(url_for('adminlogin'))

    cur = mysql.connection.cursor()

    # Fetch order details
    cur.execute("""
        SELECT o.order_id, o.user_id, o.order_date, o.total_amount, o.order_status, 
               o.payment_status, o.payment_method 
        FROM Orders o 
        WHERE o.order_id = %s
    """, (order_id,))
    order = cur.fetchone()

    # Fetch transaction details if payment status is 'Paid'
    transactions = []
    if order and order[5] == 'Paid':
        cur.execute("SELECT * FROM Transactions WHERE order_id = %s", (order_id,))
        transactions = cur.fetchall()

    cur.close()

    return render_template('admin/order_details.html', order=order, transactions=transactions)


import csv
from flask import make_response
from io import StringIO  # Import StringIO

@app.route('/admin/sales_records', methods=['GET'])
def admin_sales_records():
    if 'admin_id' not in session:
        flash('Please log in as admin to access this page.', 'warning')
        return redirect(url_for('adminlogin'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.order_id, o.user_id, o.order_date, o.total_amount, 
               o.order_status, o.payment_status 
        FROM Orders o 
        WHERE o.payment_status = 'Paid' AND o.order_status = 'Delivered'
    """)
    sales_records = cur.fetchall()
    cur.close()

    # Check if a CSV export is requested
    if request.args.get('export') == 'csv':
        return generate_csv(sales_records)

    return render_template('admin/sales_records.html', sales_records=sales_records)

def generate_csv(data):
    # Create a StringIO object to hold the CSV data
    output = StringIO()
    writer = csv.writer(output)

    # Write the header row
    writer.writerow(['Order ID', 'User ID', 'Order Date', 'Total Amount', 'Order Status', 'Payment Status'])

    # Write the data rows
    for record in data:
        writer.writerow(record)

    # Create response object
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=sales_records.csv"
    response.headers["Content-type"] = "text/csv"

    return response

if __name__ == '__main__':
    app.run(debug=True)
