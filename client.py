import threading
import socket
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            print('{}:  '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message == "Quit":
                self.sock.sendall('Server: {} saiu do chat.'.format(self.name).encode('ascii'))
                print('\nSaindo...')
                self.sock.close()
                sys.exit(0)
            else:
                self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message:
                    if self.messages:
                        self.messages.insert(tk.END, message)
                        print('\r{}\n{}: '.format(message, self.name), end='')
                    else:
                        print('\r{}\n{}: '.format(message, self.name), end='')
                else:
                    print('\n Perdemos a conexao com o server')
                    print('\nSaindo...')
                    self.sock.close()
                    sys.exit(0)
            except OSError:
                break

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):
        print('Tentando conectar a {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Conectado a {}:{}'.format(self.host, self.port))

        self.name = input('Nome: ')
        print('Bem vindo, {} ficando pronto para enviar e receber mensagens...'.format(self.name))

        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)
        send.start()
        receive.start()

        self.sock.sendall('Server: {} entrou no chat.'.format(self.name).encode('ascii'))
        print("\rPronto, para sair do chat a qualquer hora basta digitar 'Quit'\n")
        print('{}: '.format(self.name), end='')

        return receive

    def send(self, textInput):
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message).encode('ascii'))

        if message == 'Quit':
            self.sock.sendall('Server: {} saiu do chat.'.format(self.name).encode('ascii'))
            print('\nSaindo...')
            self.sock.close()
            sys.exit(0)
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

def main(host, port):
    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title("ChatBacana")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Escreva sua mensagem aqui.")

    btnSend = tk.Button(
        master=window,
        text='Mandar',
        command=lambda: client.send(textInput)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, padx=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Descrição do que o script faz.')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    parser.add_argument('-p', '--port', type=int, default=1060, help='Porta do servidor')

    args = parser.parse_args()
    main(args.host, args.port)
