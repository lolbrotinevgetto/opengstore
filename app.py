from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key='loo1brotiporeperya'

def init_db():
    db=sql.connect('games.db')
    cur=db.cursor()
    print("connected")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS games
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, platform TEXT NOT NULL, price REAL NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)""")
    
    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0]==0:
        cur.execute('INSERT INTO users (username, password) VALUES ("admin", "123")')
    
    cur.execute('SELECT COUNT(*) FROM games')
    if cur.fetchone()[0]==0:
        games_data = [
            ('Warface', 'PC', 1000.0), ("Dark Souls 3", 'PC', 2500.0),
            ('Need for Speed', 'PC', 3500.0),     ('GTA 6', 'PlayStation', 7999.0), #хочу gta6
              ('Overwatch 2', 'PC', 2500.0),
            ('PUBG Mobile', "Mobile", 1200.0), ('Cyberpunk 2077', "PC", 1999.0), 
             ('Elden Ring', 'PC', 2999.0),    ('God of War: Ragnarok', 'PS5', 4999.0), 
            ("Hogwarts Legacy", "PC", 3499.0),
        ]
        cur.executemany('INSERT INTO games (title, platform, price) VALUES (?, ?, ?)', games_data)
    db.commit()
    db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        db=sql.connect('games.db')
        cur=db.cursor()
        cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user=cur.fetchone()
        db.close()
        if user:
            session['logged_in']=True
            return redirect(url_for('index'))
        else:
            error='Неверный логин или пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    err=None
    db=sql.connect('games.db')
    cur=db.cursor()
    if request.method=='POST' and session.get('logged_in'):
        title=request.form['title']
        platform=request.form['platform']
        prst = request.form['price']
        if not title or not platform or not prst:
            err= 'Все поля должны быть заполнены'
        else:
            try:
                price = float(prst)
                if price <= 0:
                    err= "Цена должна быть больше нуля!"
                else:
                    cur.execute('INSERT INTO games (title, platform, price) VALUES (?, ?, ?)', (title, platform, price))
                    db.commit()
                    return redirect(url_for('index'))
            except ValueError:
                err= "Цена должна быть числом"
    
    cur.execute('SELECT * FROM games')
    games=cur.fetchall()
    db.close()
    return render_template('index.html', games=games, err=err, logged_in=session.get('logged_in'))

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('logged_in'):
        db = sql.connect('games.db')
        cur = db.cursor()
        cur.execute('DELETE FROM games WHERE id = ?', (id,))
        db.commit()
        db.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
