import serial

def enviar(data):
    connection = serial.Serial('COM7', 9600)

    connection.write(data.encode())

    connection.close()

    return 0
