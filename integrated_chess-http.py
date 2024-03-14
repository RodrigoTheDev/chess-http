import chess
import chess.engine
from chess import Piece
from flask import Flask, render_template, session, request, redirect, url_for, jsonify

from flask_cors import CORS
import threading
import moveValidation
import random
import json

stockfish_path = "stockfishEngine\stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
move_event = threading.Event()

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Variáveis de game
_DEBUG = ''

# CORS
# A LINHA ABAIXO HABILITA O ACESSO DA ROTA PARA TODOS NA REDE, DESCOMENTE POR SUA PRÓPRIA CONTA E RISCO
CORS(app, resources={r"/*": {"origins": "*"}})



@app.route('/movimento', methods=['POST'])
def receber_movimento():
    data = request.get_json()

    # Valida movimento
    try:
        move_uci = data['movimento']
        if moveValidation.isMoveLegal(list(board.legal_moves), move_uci):
            board.push_uci(move_uci)
            move_event.set()  # movimento recebido
            return jsonify({"mensagem": "Movimento aplicado com sucesso."})
        else:
            return jsonify({"erro": f"O movimento {move_uci} não é válido."})
    except KeyError:
        return jsonify({"erro": "Formato de requisição inválido."})
    
    

def aguardar_movimento():
    global _DEBUG

    while not board.is_game_over():
        move_event.wait()  # Aguardando sinal
        move_event.clear()  # Limpando sinal para próxima espera
        print("Tabuleiro atualizado:\n", board)
        
        if board.turn == chess.BLACK and not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=5.0))
            move_uci = result.move.uci()
            print("Jogada do robô:")
            print(move_uci)
            board.push_uci(move_uci)
            move_event.set()  # Movimento feito pelo robô

            
        if board.is_checkmate():
            _DEBUG = 'robo'
            
        if board.turn == chess.WHITE and board.is_checkmate():
            _DEBUG = 'human'
            

# Iniciar a thread para aguardar movimentos
thread = threading.Thread(target=aguardar_movimento)
thread.start()

@app.route('/')
def index():  
    return render_template('index.html')

@app.route('/restart_game')
def restart_game():
    global board
    board = chess.Board()
    session['xeque'] = False
    
    return redirect(url_for('jogar'))

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
    xeque = session.get('xeque')
    
    # Lógica para determinar a origem do xeque
    origem_xeque = session.get('origem_xeque')
    
    if origem_xeque == 'robo':
        origem_xeque = 'Xeque Robo'
    elif origem_xeque == 'jogador':
        origem_xeque = 'Xeque Jogador'
        
    session['origem_xeque'] = None
    
    if df == 'true':    
        numeros = [0, 1, 2, 3]  
        pesos = [1, 2, 5, 7]  
        random.seed()   
        numero_aleatorio = random.choices(numeros, weights=pesos, k=1)[0]
        
        session['dificuldade'] = numero_aleatorio
        dificuldade = numero_aleatorio
    else:
        dificuldade = session.get('dificuldade', None)
        
    return render_template('jogar.html', dificuldade=dificuldade, xeque=xeque, origem_xeque=origem_xeque, _DEBUG=_DEBUG, )


def boardToList(board):
    rowList = []
    finalList = []
    for linha in board:
        if linha == Piece.from_symbol('P'):
            rowList.append('P')
        if linha == Piece.from_symbol('N'):
            rowList.append('N')
        if linha == Piece.from_symbol('R'):
            rowList.append('R')
        if linha == Piece.from_symbol('B'):
            rowList.append('B')
        if linha == Piece.from_symbol('Q'):
            rowList.append('Q')
        if linha == Piece.from_symbol('K'):
            rowList.append('K')
        if linha == Piece.from_symbol('p'):
            rowList.append('p')
        if linha == Piece.from_symbol('n'):
            rowList.append('n')
        if linha == Piece.from_symbol('r'):
            rowList.append('r')
        if linha == Piece.from_symbol('b'):
            rowList.append('b')
        if linha == Piece.from_symbol('q'):
            rowList.append('q')
        if linha == Piece.from_symbol('k'):
            rowList.append('k')
        if linha == None:
            rowList.append('')
            
        if len(rowList) == 8:
            finalList.append(rowList)
            
            rowList = []

    finalList.reverse()
    return finalList

@app.route('/update_board', methods=['POST'])
def update_board():
    global _DEBUG
    print(_DEBUG)

    # Obter o mapa de peças
    piece_map = board.piece_map()

    # Criar uma lista representando o tabuleiro
    board_list = [piece_map.get(square, None) for square in chess.SQUARES]

    new_pieces_json = json.dumps(boardToList(board_list))
        
    return new_pieces_json

def iniciar_servidor():
    # Iniciar o servidor Flask
    app.run(debug=True)

if __name__ == "__main__":
    iniciar_servidor()
