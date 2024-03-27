# PROGRAMA COM O RECONHECIMENTO DE IMAGEM INTEGRADO NO JOGO
# NÃO INTERAGE COM A INTERFACE WEB

import chess
import chess.engine
import moveValidation
import reconhecimento_imagem as ri

def play():
    stockfish_path = "./stockfishEngine/stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real

    # objeto ChessEngine
    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:

        board = chess.Board()

        while not board.is_game_over():
            print('A B C D E F G H\n----------------')
            print(board)
            print('----------------\nA B C D E F G H')
            if board.turn == chess.WHITE:
                # move_uci = input("Sua jogada (UCI): ")
                move_uci = ri.compare_image()
                print("Sua jogada:")
                print(move_uci)
            else:
                result = engine.play(board, chess.engine.Limit(time=2.0))
                move_uci = result.move.uci()
                print("Jogada do robô:")
                print(move_uci)

            # if move_uci in board.legal_moves:
            legal_moves = list(board.legal_moves)
            # print(board.legal_moves)
            # print(legal_moves)

            if moveValidation.isMoveLegal(legal_moves,move_uci):
                board.push_uci(move_uci)
            else:
                print(f"O movimento {move_uci} não é válido.")
            # else:
            #     print(f"O movimento {move_uci} é ilegal")

        print("Fim do jogo")
        print("Resultado:", board.result())

if __name__ == "__main__":
    play()