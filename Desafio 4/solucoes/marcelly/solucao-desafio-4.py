#Autor(a): Marcelly Fonseca da Cruz

import pandas as pd
from datetime import datetime
import os

#esta linha de código vai me retornar o caminho absoluto de meu script atual, pois eu quero que os arquivos sejam salvos na pasta 'marcelly'
caminho_base = os.path.dirname(os.path.abspath(__file__))

#Etapa 2: O decorador para Auditoria --> etapa 2 vem primeiro pois vou precisar dos decoradores nos métodos sacar e depositar da classe Conta.
def log_transacao(f):
    def wrapper(self, *args, **kwargs):
        resultado = f(self, *args, **kwargs)

        operacao = f.__name__ #Nome da operação (sacar ou depositar)
        valor = args[0] #valor da transação
        conta = self.numero_conta #número da conta em que a operacao foi feita

        #Salvando o arquivo .log no caminho desejado
        arquivo_log = os.path.join(caminho_base, 'historico_transacoes.log')
        with open(arquivo_log, 'a', encoding='utf-8') as file:
            file.write(f"{datetime.now()} - Conta: {conta} - Operação: {operacao} - Valor: R$ {valor:.2f}\n")

        return resultado
    return wrapper

#Etapa1: Modelagem Com Classes
class Cliente:
    def __init__(self, nome: str, cpf: str, data_nascimento: str):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        
class Conta:
    def __init__(self, numero_conta: int, cliente: Cliente, saldo: float = 0):
        self.numero_conta = numero_conta
        self.cliente = cliente
        self.saldo = saldo

    @log_transacao
    def depositar(self, valor):
        self.saldo += valor

    @log_transacao
    def sacar(self, valor):
        if valor <= self.saldo:
            self.saldo -=valor
            return True
        else:
            print('Saldo insuficiente para saque.')
            return False
        
    def consultar_saldo(self):
        print(f"Saldo Atual: R$ {self.saldo:.2f}")


#Etapa 3: Persistência dos Dados
clientes = {}

contas = {}

def carregar_dados():
    try:
        #Indicando o caminho para salvar os arquivos csv
        arquivo_clientes = os.path.join(caminho_base, 'clientes.csv')
        arquivo_contas = os.path.join(caminho_base, 'contas.csv')

        if os.path.exists(arquivo_clientes):
            #lê o arquivo
            df_clientes = pd.read_csv(arquivo_clientes, encoding='utf-8')

            #transforma para dicionário
            registros_clientes = df_clientes.to_dict(orient='records')

            #Passa por cada registro do arquivo clientes.csv e cria objeto do tipo Cliente
            for linha in registros_clientes:
                cliente = Cliente(linha['nome'], linha['cpf'], linha['data_nascimento'])
                clientes[linha['cpf']] = cliente #Tenho que fazer isso pois é pelo cpf que eu vou encontrar o meu cliente

        if os.path.exists(arquivo_contas):
            #Lê o arquivo
            df_conta = pd.read_csv(arquivo_contas, encoding='utf-8')

            #Transforma para dicionário
            registros_conta = df_conta.to_dict(orient='records')

            #Passa por cada registro do arquivo contas.csv e cria objeto do tipo Conta
            for linha in registros_conta:
                cliente_conta = clientes.get(linha['cpf'])#pega o cpf do cliente para identificá-lo
                conta = Conta(linha['numero_conta'], cliente_conta, linha['saldo']) #Veja que na criação do objeto conta eu coloco 'cliente_conta' pois é ele que vai me trazer um cliente
                contas[linha['numero_conta']] = conta #Tenho que fazer isso pois é pelo número da conta que eu vou encontrar a conta

    except FileNotFoundError:
        print('Arquivo clientes.csv e contas.csv não encontrados.')
    
def salvar_dados():
    arquivo_clientes = os.path.join(caminho_base, 'clientes.csv')
    arquivo_contas = os.path.join(caminho_base, 'contas.csv')

    #Cria a lista uma lista de dicionários com os dados do cliente
    lista_clientes = [{'nome': cliente.nome, 'cpf': cliente.cpf, 'data_nascimento': cliente.data_nascimento} for cliente in clientes.values()]

    #tranforma o dicionário em Dataframe
    df_clientes = pd.DataFrame(lista_clientes)

    #Salva o Dataframe no arquivo csv
    df_clientes.to_csv(arquivo_clientes, index=False, encoding='utf-8')


    #Cria a lista uma lista de dicionários com os dados das contas
    lista_contas = [{'numero_conta': conta.numero_conta, 'cpf': conta.cliente.cpf, 'saldo': conta.saldo} for conta in contas.values()]

    #tranforma o dicionário em Dataframe
    df_contas = pd.DataFrame(lista_contas)

    #Salva o Dataframe no arquivo csv
    df_contas.to_csv(arquivo_contas, index=False, encoding='utf-8')
    

#Etapa 4: Fluxo Principal (Menu Interativo)
def menu():
    carregar_dados()
    while True:
        print('\n--------- Seja Bem-Vindo ao PyBank! O Que Deseja Fazer? ----------')
        print("1 - Criar Novo Cliente")
        print("2 - Criar Nova Conta (a conta só pode ser criada se há um cliente existente)")
        print("3 - Acessar Conta")
        print("4 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input('Insira o nome do cliente: ')
            cpf = input('Insira o cpf do cliente: ')
            data_nascimento = input('Insira a data de nascimento do cliente: ')

            if cpf in clientes:
               print('O cliente já existe.')
            else:
               clientes[cpf] = Cliente(nome, cpf, data_nascimento) #Lembre-se que o cpf é o id do cliente
               salvar_dados()
               print('Cliente Cadastrado Com Sucesso!')

        elif opcao == '2':
            #Como eu quero criar uma conta, eu vou verificar se o cliente existe
            cpf_cliente = input('Insira o CPF do cliente: ')
            cliente = clientes.get(cpf_cliente)

            if not cliente:
                print('O cliente não foi encontrado. Cadastre-o primeiro.')

           #Se há um cliente existente, cria a conta
            else:
                numero_conta = max(contas.keys(), default=0) + 1
                contas[numero_conta] = Conta(numero_conta, cliente)
                salvar_dados()

                print(f"Conta criada com sucesso! Número da conta {numero_conta}")

        elif opcao == '3':
            #Para acessar a conta é necessário o numero da conta
            numero_da_conta = int(input('Insira o número da sua conta: '))
            conta = contas.get(numero_da_conta)

            if not conta:
                print("Conta não encontrada")
                continue

            while True:
                print('\n--------------- Acesso à Conta. O Que Deseja Fazer? ------------------')
                print("1 - Depositar")
                print("2 - Sacar")
                print("3 - Consultar Saldo")
                print("4 - Voltar ao menu principal")
                opcao = input("Escolha uma opção: ")

                if opcao == '1':
                    valor = float(input('Insira um valor para depositar: R$ '))
                    conta.depositar(valor)
                    salvar_dados()

                    print('Depósito realizado com sucesso!')

                elif opcao == '2':
                    valor = float(input('Insira o valor que deseja sacar: R$ '))
                    if conta.sacar(valor): #Vai dar True
                        salvar_dados()
                        print('Saque realizado com sucesso!')

                elif opcao == '3':
                    conta.consultar_saldo()
                else:
                    break
        else:
            salvar_dados()
            print('Saindo do Sistema...')
            break

menu()