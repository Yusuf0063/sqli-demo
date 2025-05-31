from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# Veritabanı kurulum fonksiyonu
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    # Örnek kullanıcılar ekle (aynı kullanıcılar tekrar eklenmesin diye basit kontrol yapılabilir)
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('user1', 'pass1')")
        conn.commit()
    conn.close()

# Ana Sayfa - Giriş Formu
@app.route('/')
def home():
    return render_template('login.html')  # login.html dosyasını templates klasöründe tutmalısın

# SQLi ile kimlik doğrulama (GET yöntemiyle, URL'de username & password görünecek)
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username', '')
    password = request.args.get('password', '')

    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchone()
    except Exception as e:
        conn.close()
        return f"SQL Hatası: {e}"
    conn.close()

    if result:
        return f"Hoşgeldin, {result[1]}!"
    else:
        return "Giriş başarısız!"

# UNION-based SQLi için test endpoint
@app.route('/search')
def search():
    user_id = request.args.get('id', '1')  # Default 1

    query = f"SELECT id, username FROM users WHERE id = {user_id}"
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except Exception as e:
        conn.close()
        return f"SQL Hatası: {e}"
    conn.close()

    # Basit şekilde sonucu ekrana yazdır
    html = "<h2>Arama Sonuçları</h2><ul>"
    for r in results:
        html += f"<li>ID: {r[0]}, Kullanıcı Adı: {r[1]}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
