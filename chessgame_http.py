import chess
import chess.engine
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import moveValidation

class ChessGame:
    def __init__(self):
        self.stockfish_path = "./stockfishEngine/stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        self.move_event = threading.Event()
        self.app = Flask(__name__)

        # CORS
        # A LINHA ABAIXO HABILITA O ACESSO DA ROTA PARA TODOS NA REDE, DESCOMENTE POR SUA PRÓPRIA CONTA E RISCO
        # CORS(self.app, resources={r"/movimento": {"origins": "*"}})

        @self.app.route('/movimento', methods=['POST'])
        def receber_movimento():
            data = request.get_json()

            # Valida movimento
            try:
                move_uci = data['movimento']
                if moveValidation.isMoveLegal(list(self.board.legal_moves), move_uci):
                    self.board.push_uci(move_uci)
                    self.move_event.set()  # movimento recebido
                    return jsonify({"mensagem": "Movimento aplicado com sucesso."})
                else:
                    return jsonify({"erro": f"O movimento {move_uci} não é válido."})
            except KeyError:
                return jsonify({"erro": "Formato de requisição inválido."})

        def aguardar_movimento():
            while not self.board.is_game_over():
                self.move_event.wait()  # Aguardando sinal
                self.move_event.clear()  # Limpando sinal para próxima espera
                print("Tabuleiro atualizado:\n", self.board)

                if self.board.turn == chess.BLACK and not self.board.is_game_over():
                    result = self.engine.play(self.board, chess.engine.Limit(time=2.0))
                    move_uci = result.move.uci()
                    print("Jogada do robô:")
                    print(move_uci)
                    self.board.push_uci(move_uci)
                    self.move_event.set()  # Movimento feito pelo robô

        # Iniciar a thread para aguardar movimentos
        self.thread = threading.Thread(target=aguardar_movimento)
        self.thread.start()

    def iniciar_servidor(self):
        # Iniciar o servidor Flask
        self.app.run(debug=True)

if __name__ == "__main__":
    chess_game = ChessGame()
    chess_game.iniciar_servidor()
