from flask import Flask, render_template, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/')
def index():  
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        session['dificuldade'] = int(request.form['dificuldade'])
        return redirect(url_for('index'))
    else:
        return render_template('config.html')

@app.route('/jogar')
def jogar():
    dificuldade = session.get('dificuldade', None)
    
    if dificuldade == None:
        session['dificuldade'] == 0
  
    return render_template('jogar.html', dificuldade=dificuldade)
    

if __name__ == '__main__':
    app.run(debug=True)
