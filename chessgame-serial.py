# PROGRAMA COM O RECONHECIMENTO DE IMAGEM INTEGRADO NO JOGO
# NÃO INTERAGE COM A INTERFACE WEB

import chess
import chess.engine
import serial
import moveValidation, sendserial as snd

try:
    ser = serial.Serial(
        port='COM7',        # Replace with your serial port
        baudrate=9600,      # Ensure this matches the receiving end
        timeout=1           # Set a timeout for blocking operations
    )
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# Function to send data
def send_data(data):
    try:
        ser.write(data.encode())  # Encode and send the string
        print(f"Sent: {data}")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

# Função que verifica o quadrado destino já possui uma peça (ajuda na comunicação do arduino)
def hasPiece(board, target):
    # Convert the string to a square index
    square = chess.parse_square(target)

    # Get the piece at that square
    piece = board.piece_at(square)

    return (piece != None)

def play():
    stockfish_path = "./stockfishEngine/stockfish-windows-x86-64-avx2.exe"  # Substitua pelo caminho real

    # objeto ChessEngine
    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:

        board = chess.Board()

        while not board.is_game_over():
            # print('A B C D E F G H\n----------------')
            print(board)
            # print('----------------\nA B C D E F G H')

            if board.turn == chess.WHITE:
                move_uci = input("Sua jogada (UCI): ")
                print("Sua jogada:")
                print(move_uci)
            else:
                result = engine.play(board, chess.engine.Limit(time=2.0))
                move_uci = result.move.uci()
                send = move_uci # String a ser enviada para o serial

                if hasPiece(board, f"{move_uci[2]}{move_uci[3]}"):
                    send += "s"

                print(f"Enviando para o serial: {send}")


                send_data(send)
                try:
                    response = ser.readline().decode().strip()  # Read a line from the serial port
                    print(f"Received: {response}")
                except serial.SerialException as e:
                    print(f"Error reading from serial port: {e}")

            # if move_uci in board.legal_moves:
            legal_moves = list(board.legal_moves)
            # print(board.legal_moves)
            # print(legal_moves)

            # Optionally, read response

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


