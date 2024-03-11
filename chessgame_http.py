import chess
import chess.engine
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import moveValidation



stockfish_path = "./stockfishEngine/stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
move_event = threading.Event()
app = Flask(__name__)

# CORS
# A LINHA ABAIXO HABILITA O ACESSO DA ROTA PARA TODOS NA REDE, DESCOMENTE POR SUA PRÓPRIA CONTA E RISCO
CORS(app, resources={r"/movimento": {"origins": "*"}})

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
    while not board.is_game_over():
        move_event.wait()  # Aguardando sinal
        move_event.clear()  # Limpando sinal para próxima espera
        print("Tabuleiro atualizado:\n", board)

        if board.turn == chess.BLACK and not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=2.0))
            move_uci = result.move.uci()
            print("Jogada do robô:")
            print(move_uci)
            board.push_uci(move_uci)
            move_event.set()  # Movimento feito pelo robô

# Iniciar a thread para aguardar movimentos
thread = threading.Thread(target=aguardar_movimento)
thread.start()

def iniciar_servidor():
    # Iniciar o servidor Flask
    app.run(debug=True)

if __name__ == "__main__":
    iniciar_servidor()
