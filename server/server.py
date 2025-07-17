from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/data')
def data():
    return jsonify({'a': 1, 'b': 2, 'c': 3})

if __name__ == '__main__':
    app.run(debug=True)
