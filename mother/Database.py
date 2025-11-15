import time
import threading

#exemplo de database aula teórica
class Database:
    dados : dict
    quantos : int
    lock : threading.Lock


    def __init__(self):
        self.dados = dict()
        self.quantos = 0
        self.lock = threading.Lock()
    
    def insere(self, mensagem : str):
        try:
            self.lock.acquire()
            self.quantos += 1
            self.dados[mensagem] = self.quantos
        finally:
            self.lock.release()

    def apaga(self, mensagem : str):
        if mensagem in self.dados:
            self.dados.pop(mensagem)
            self.quantos -= 1

    def show(self):
       
        try:
            self.lock.acquire()
            novo = dict(self.dados)   
        finally:
            self.lock.release()

        for mensagem, quantos in novo.items():
            print(f"mensagem {quantos}: {mensagem}")
            time.sleep(2)  