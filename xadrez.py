from flask import Flask, render_template, session, request, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/')
def index():  
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        session['dificuldade'] = int(request.form['dificuldade'])
        return redirect(url_for('jogar'))
    else:
        return render_template('config.html')

@app.route('/jogar')
def jogar():
    df = request.args.get('df')
    
    if df == 'true':    
        numeros = [0, 1, 2, 3]  
        pesos = [1, 2, 5, 7]  
        random.seed()   
        numero_aleatorio = random.choices(numeros, weights=pesos, k=1)[0]
        
        session['dificuldade'] = numero_aleatorio
        dificuldade = numero_aleatorio
    else:
        dificuldade = session.get('dificuldade', None)
    
        
    return render_template('jogar.html', dificuldade=dificuldade)

if __name__ == '__main__':
    app.run(debug=True)
