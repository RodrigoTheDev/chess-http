from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/jogar')
def jogar():
    return render_template('jogar.html')

if __name__ == '__main__':
    app.run(debug=True)
