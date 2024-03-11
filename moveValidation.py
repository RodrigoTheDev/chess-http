import chess

def isMoveLegal(movimentos_legais, movimento_uci):
    return any(move.uci() == movimento_uci for move in movimentos_legais)
