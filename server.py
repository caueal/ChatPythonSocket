import threading
import socket
import argparse
import os

class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        if self.host is None or self.port is None:
            print("Host or port not provided.")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind((self.host, self.port))
        except Exception as e:
            print("Error binding socket:", e)
            return

        # Continuação do código aqui...

        sock.listen(1)
        print('Server listening at', sock.getsockname())

        while True:

            #aceitando novas conexões
            sc,sockname = sock.accept()
            print(F"Accepted connection from {sc.getpeername()} to {sc.getsockname()}")

            #Criando uma nova thread
            server_socket = ServerSocket(sc, sockname, self)

            #Iniciando uma nova thread
            server_socket.start()

            #Adicionando a thread para uma conexao ativa
            self.connections.append(server_socket)
            print("Pronto para receber mensagem de", sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:

            #mandar para todos cliente conectados aceitaram o source
            if connection.sockname != source:
                connection.send(message)


    def remove_connection(self, connection):

        self.connections.remove(connection)


class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server


    def run(self):

        while True:
            message = self.sc.recv(1024).decode('ascii')

            if message:
                print(f"{self.sockname} says {message}")
                self.server.broadcast(message, self.sockname)

            else:
                print(f"{self.sockname} disconectado")
                self.sc.close()
                server.remove_connection(self)
                return


    def send(self, message):

        self.sc.sendall(message.encode('ascii'))


    def exit(server):

        while True:
            ipt = input("")
            if ipt == "q":
                print("Fechando todas as conexões")
                for connection in server.connections:
                    connection.sc.close()

                print("Fechando o servidor")
                os.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Descrição do que o script faz.')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    parser.add_argument('-p', '--port', type=int, default=1060, help='Porta do servidor')

    # Parseando os argumentos
    args = parser.parse_args()

    # Criar e iniciar uma instância do servidor
    server = Server(args.host, args.port)
    server.start()

    # Aguardar a finalização do servidor
    server.join()