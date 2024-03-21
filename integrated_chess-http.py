from chess import Piece
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
from flask_cors import CORS

import chess
import chess.engine
import threading
import moveValidation
import random
import json

stockfish_path = "stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real
board = chess.Board()
engine = None
move_event = threading.Event()

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Variáveis de game
_DEBUG = ''

#Funções do STOCKFISH
def configure_stockfish(difficulty):
    """
    Configura o Stockfish com um determinado nível de dificuldade.

    Parâmetros:
    - difficulty: O nível de dificuldade desejado.

    Retorna:
    - O engine configurado.
    """
    
    global engine
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Skill Level": difficulty})
    engine.configure({"UCI_LimitStrength": False})
    engine.configure({"UCI_Elo": 3190})
    engine.configure({"Threads": 4})
    engine.configure({"Hash": 512})
      
    return engine

# CORS
# A LINHA ABAIXO HABILITA O ACESSO DA ROTA PARA TODOS NA REDE, DESCOMENTE POR SUA PRÓPRIA CONTA E RISCO
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/movimento', methods=['POST'])
def receber_movimento():
    """
    Rota para receber um movimento do jogador humano.
    """
    
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
    """
    Função para aguardar os movimentos dos jogadores e do Stockfish.
    """
    
    global _DEBUG

    while not board.is_game_over():
        move_event.wait()  # Aguardando sinal
        move_event.clear()  # Limpando sinal para próxima espera
        print("Tabuleiro atualizado:\n", board)
        
        if board.turn == chess.BLACK and not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=3.0))
            move_uci = result.move.uci()
            print("Jogada do robô:")
            print(move_uci)
            board.push_uci(move_uci)
            move_event.set()  # Movimento feito pelo robô

        if board.turn == chess.BLACK and board.is_checkmate():
            _DEBUG = 'human'
            print(_DEBUG)
            
        if board.turn == chess.WHITE and board.is_checkmate():
            _DEBUG = 'robo'
            print(_DEBUG)
            
            

# Iniciar a thread para aguardar movimentos
thread = threading.Thread(target=aguardar_movimento)
thread.start()

@app.route('/')
def index(): 
    """
    Rota para renderizar a página inicial.
    """
    global _DEBUG
    _DEBUG = ''
    return render_template('index.html')

@app.route('/restart_game')
def restart_game():
    """
    Rota para reiniciar o jogo.
    """
    global board
    board = chess.Board()
    session['xeque'] = False
    
    return redirect(url_for('jogar'))

@app.route('/config', methods=['GET', 'POST'])
def config():
    """
    Rota para configurar as opções do jogo.
    """
    if request.method == 'POST':
        session['dificuldade'] = int(request.form['dificuldade'])
        if session['dificuldade'] in range(4):
            configure_stockfish(session['dificuldade'] * 5 + 1)  # Configuração de dificuldade
        return redirect(url_for('restart_game'))
    else:
        return render_template('config.html')

@app.route('/jogar')
def jogar():
    """
    Rota para iniciar o jogo.
    """
    global engine
    engine = configure_stockfish(20)  # Configuração padrão
    df = request.args.get('df')
    xeque = session.get('xeque')
    
    if df == 'true':    
        numeros = [1, 5, 14, 20]  
        pesos = [1, 2, 5, 7]  
        random.seed()   
        numero_aleatorio = random.choices(numeros, weights=pesos, k=1)[0]
        
        configure_stockfish(numero_aleatorio)
    else:
        dificuldade = session.get('dificuldade', None)
        configure_stockfish(dificuldade)
        
    return render_template('jogar.html', xeque=xeque, _DEBUG=_DEBUG)

def boardToList(board):
    """
    Função auxiliar para converter o tabuleiro do formato de peças do Chess para uma lista.
    """
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
    """
    Rota para atualizar o estado do tabuleiro.
    """
    global _DEBUG

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
    
