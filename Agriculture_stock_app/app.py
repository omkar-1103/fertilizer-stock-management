from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'fertilizer_stock.db'

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_type TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            manufacturing_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            price REAL NOT NULL,
            supplier_name TEXT,
            batch_number TEXT,
            storage_location TEXT,
            date_added TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home page - Display all products
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Add new product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        category = request.form['category']
        quantity = request.form['quantity']
        unit = request.form['unit']
        manufacturing_date = request.form['manufacturing_date']
        expiry_date = request.form['expiry_date']
        price = request.form['price']
        supplier_name = request.form['supplier_name']
        batch_number = request.form['batch_number']
        storage_location = request.form['storage_location']
        date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO products 
                     (product_name, product_type, category, quantity, unit, 
                      manufacturing_date, expiry_date, price, supplier_name, 
                      batch_number, storage_location, date_added)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (product_name, product_type, category, quantity, unit,
                      manufacturing_date, expiry_date, price, supplier_name,
                      batch_number, storage_location, date_added))
        conn.commit()
        conn.close()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_product.html')

# View single product details
@app.route('/view/<int:id>')
def view_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if product is None:
        flash('Product not found!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('view_product.html', product=product)

# Update product
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    
    if product is None:
        flash('Product not found!', 'danger')
        conn.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        category = request.form['category']
        quantity = request.form['quantity']
        unit = request.form['unit']
        manufacturing_date = request.form['manufacturing_date']
        expiry_date = request.form['expiry_date']
        price = request.form['price']
        supplier_name = request.form['supplier_name']
        batch_number = request.form['batch_number']
        storage_location = request.form['storage_location']
        
        conn.execute('''UPDATE products SET 
                     product_name=?, product_type=?, category=?, quantity=?, unit=?,
                     manufacturing_date=?, expiry_date=?, price=?, supplier_name=?,
                     batch_number=?, storage_location=?
                     WHERE id=?''',
                     (product_name, product_type, category, quantity, unit,
                      manufacturing_date, expiry_date, price, supplier_name,
                      batch_number, storage_location, id))
        conn.commit()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('update_product.html', product=product)

# Delete product
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!', 'warning')
    return redirect(url_for('index'))

# Search functionality
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = get_db_connection()
    products = conn.execute('''SELECT * FROM products 
                            WHERE product_name LIKE ? OR category LIKE ? OR supplier_name LIKE ?
                            ORDER BY id DESC''',
                            ('%' + query + '%', '%' + query + '%', '%' + query + '%')).fetchall()
    conn.close()
    return render_template('index.html', products=products, search_query=query)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
