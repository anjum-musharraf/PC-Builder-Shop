from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'   # CHANGE THIS

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pc_builder_final'
}

def get_db():
    return mysql.connector.connect(**db_config)

# ---------- Authentication Routes ----------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (username, email, password))
            conn.commit()
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('login'))
    return render_template_string(SIGNUP_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- Dashboard (SPA with Tailwind) ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# ---------- API: Products & Search (fixed Decimal conversion) ----------
@app.route('/api/products')
def api_products():
    search = request.args.get('search', '')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    if search:
        cur.execute("SELECT * FROM products WHERE name LIKE %s", (f'%{search}%',))
    else:
        cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    conn.close()
    # Convert Decimal price to float for JSON
    for p in products:
        p['price'] = float(p['price'])
    return jsonify(products)

@app.route('/api/search')
def api_search():
    return api_products()

# ---------- API: Cart (add, remove, get, checkout) ----------
@app.route('/api/cart')
def get_cart():
    cart = session.get('cart', [])
    # Ensure prices are float and calculate total
    total = 0.0
    for item in cart:
        price = item.get('price')
        if isinstance(price, float):
            total += price
        else:
            total += float(price)
    return jsonify({'items': cart, 'total': total})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data['product_id']
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    if product:
        product['price'] = float(product['price'])  # convert to float
        cart = session.get('cart', [])
        cart.append(product)
        session['cart'] = cart
        return jsonify({'cart_count': len(cart)})
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    new_cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = new_cart
    total = sum(item.get('price', 0.0) for item in new_cart)
    return jsonify({'cart_count': len(new_cart), 'total': float(total)})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    session['cart'] = []
    return jsonify({'status': 'ok'})

# ---------- API: PC Builder (save & get builds) ----------
@app.route('/api/save-build', methods=['POST'])
def save_build():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    build_name = data.get('build_name', 'Unnamed Build')
    parts = {
        'cpu': data.get('cpu'),
        'motherboard': data.get('motherboard'),
        'gpu': data.get('gpu'),
        'ram': data.get('ram'),
        'storage': data.get('storage')
    }
    parts_json = json.dumps(parts)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO saved_builds (user_id, build_name, parts) VALUES (%s, %s, %s)",
                (user_id, build_name, parts_json))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'saved'})

@app.route('/api/get-builds')
def get_builds():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, build_name, parts, created_at FROM saved_builds WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    builds = cur.fetchall()
    for build in builds:
        build['parts'] = json.loads(build['parts'])
    cur.close()
    conn.close()
    return jsonify(builds)

# ---------- Embedded HTML for login/signup (simple Bootstrap) ----------
SIGNUP_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Sign Up - PC Builder</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light"><div class="container mt-5"><div class="row justify-content-center"><div class="col-md-6"><div class="card shadow"><div class="card-header bg-primary text-white"><h3 class="mb-0">Sign Up</h3></div><div class="card-body"><form method="post"><div class="mb-3"><label>Username</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label>Email</label><input type="email" name="email" class="form-control" required></div><div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div><button type="submit" class="btn btn-primary w-100">Sign Up</button></form><p class="mt-3 text-center">Already have an account? <a href="/login">Login</a></p></div></div></div></div></div></body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Login - PC Builder</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light"><div class="container mt-5"><div class="row justify-content-center"><div class="col-md-6"><div class="card shadow"><div class="card-header bg-primary text-white"><h3 class="mb-0">Login</h3></div><div class="card-body"><form method="post"><div class="mb-3"><label>Username</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div><button type="submit" class="btn btn-primary w-100">Login</button></form><p class="mt-3 text-center">Don't have an account? <a href="/signup">Sign Up</a></p></div></div></div></div></div></body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)