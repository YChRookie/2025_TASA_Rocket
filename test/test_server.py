from flask import Flask, render_template, jsonify
import pymysql

app = Flask(__name__)

def generate_data():
    con = pymysql.connect(
        host='localhost',
        user='root',
        password='IntScope_-2147483648~2147483647',
        database='library_system',
    )
    with con.cursor() as cur:
        cur.execute("SELECT * FROM books;")
        rows = cur.fetchall()
    return rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_data')
def send_data():
    data = generate_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
``