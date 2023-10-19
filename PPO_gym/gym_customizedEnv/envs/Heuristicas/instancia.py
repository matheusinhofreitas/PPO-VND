#class A(object):
#    def __init__(self):
#        print("init")
#    def __call__(self):
#        print("call ")

#a = A() #imprime init
#a() #imprime call
import os 
import pickle
import numpy as np
import statistics
import math
import copy

class Instancia:
    local = ''
    nome = ''
    grupo = 0
    n_tarefas = 0
    n_veiculos = 0
    n_maquinas = 0

    LB = 0
    UB = 0
    tempo_viagem = []# tempo_viagem[local_j][local_k]. = IGUAL A DISTANCIA
    tempo_processamento= [] # tempoProcessamento[maquina][tarefa].
    tempo_setup = [] # tempo_setup[maquina][tarefa][tarefa].
    penalidade_atraso = [] # penalidade_atraso[tarefa].
    data_entrega = []# data_entrega[tarefa].
    tamanho_tarefa = []# tamanho_tarefa[tarefa].
    capacidade_veiculo = []# capacidade_veiculo[veiculo].
    velocidade_veiculos = []#Velocidade do veiculo
    #informações sobre as instancias
    capacidade_total = 0
    demanda_total = 0
    setup_min = 0
    setup_max = 0
    raio = 0
    circulos = 0
    tempo_processamento_min = 0
    tempo_processamento_max = 0
    demanda_min = 0
    demanda_max = 0
    priority_factor = 0
    range_factor_R = 0
    u_factor = 0.5
    alpha = 0.1
    replicacao = 0


    #estatisticas da Instancia
    tp_medio = 0
    setup_medio = 0
    distancia_media = 0
    demanda_media = 0
    capacidade_media = 0

    #Valores para normalização dos dados
    menor_completion_time = []# menor completion time de uma tarefa
    maior_completion_time = []# maior completion time de uma tarefa

    menor_data_entrega = []# menor data de entrega de uma tarefa
    maior_data_entrega = []# maior data de entrega de uma tarefa

    menor_atraso_ponderado = []# menor atraso ponderado de uma tarefa
    maior_atraso_ponderado = []# maior atraso ponderado de uma tarefa

    #construtor
    def __init__(self, local):
        self.local = local
        self.carregar_instancia()
        self.calcula_estatistica()
        #self.imprimir_instancia()
        self.calcula_valores_para_normalizacao()
        self.LB = np.sum(self.menor_atraso_ponderado)
        self.UB = np.sum(self.maior_atraso_ponderado)
        #print("init")
    


    #metodos
    def calcula_valores_para_normalizacao(self):
        #inicia os vetores 
        self.menor_completion_time = np.zeros(self.n_tarefas + 1) # menor completion time de uma tarefa
        self.maior_completion_time = np.zeros(self.n_tarefas + 1) # maior completion time de uma tarefa
        self.menor_data_entrega = np.zeros(self.n_tarefas + 1) # menor data de entrega de uma tarefa
        self.maior_data_entrega = np.zeros(self.n_tarefas + 1) # maior data de entrega de uma tarefa
        self.menor_atraso_ponderado = np.zeros(self.n_tarefas + 1) # menor atraso ponderado de uma tarefa
        self.maior_atraso_ponderado = np.zeros(self.n_tarefas + 1) # maior atraso ponderado de uma tarefa

        #calcula o menor completion time para uma tarefa
        #o menor completion time de uma tarefa é se ela é processada primeiro na maquina que possui 
        #o menor tempo de processamento da tarefa j
        for j in range(0, self.n_tarefas + 1):
            menor = 100 #o maior tempo de processamento é 99
            for i in range(0,self.n_maquinas):
                if menor > self.tempo_processamento[i][j]:
                    menor = self.tempo_processamento[i][j]
            self.menor_completion_time[j] = menor

        #calcula o menor data de entrega para uma tarefa
        #A menor data de entrega de uma tarefa j é igual ao completion Time da tarefa j + a distancia entre a tarefa e o deposito.
        for j in range(0, self.n_tarefas + 1):
            self.menor_data_entrega[j] = self.menor_completion_time[j] + self.tempo_viagem[0][j]

        #calcula o menor atraso ponderado para uma tarefa
        #O menor Atraso ponderado de uma tarefa j é igual a data de entrega da tarefa j * a penalidade de atraso da tarefa j.
        for j in range(0, self.n_tarefas + 1):
            if self.menor_data_entrega[j] > self.data_entrega[j]:
                self.menor_atraso_ponderado[j] = (self.menor_data_entrega[j] - self.data_entrega[j]) * self.penalidade_atraso[j]
            else:
                self.menor_atraso_ponderado[j] = 0

        #-----------------------Calculo dos maiores valores -----------------------------------
        #calcula o maior completion time para uma tarefa
        #o maior completion time de uma tarefa é se ela é a ultima tarefa a ser processada em 1 máquina
        #Para calcular dividimos o n_tarefas pelo n_máquinas, e colocamos a tarefa j na ultima possição da máquina
        #Todas as tarefas que vem antes da tarefa j são processadas nas máquinas com os maiores tempos de processamentos e setups da instancia.
        n_tarefas_por_maquina = math.ceil(self.n_tarefas/self.n_maquinas)
        maior_tp = np.zeros(self.n_tarefas + 1) # maior tempo de processamento de uma tarefa
        #pega o maior tempo de processamento de uma tarefa j
        for j in range(0, self.n_tarefas + 1):
            maior = -1
            for i in range(0,self.n_maquinas):
                if maior < self.tempo_processamento[i][j]:
                    maior = self.tempo_processamento[i][j]
            maior_tp[j] = maior

        maior_setup = np.zeros(self.n_tarefas + 1) # maior tempo de setup de uma tarefa
        #pega o maior tempo de setup de uma tarefa k
        for k in range(0, self.n_tarefas + 1):
            maior = -1
            for j in range(0, self.n_tarefas + 1):
                for i in range(0,self.n_maquinas):
                    if maior < self.tempo_setup[i][j][k]:
                        maior = self.tempo_setup[i][j][k]
            maior_setup[k] = maior
        
        # maior tempo de processamento + setup de uma tarefa
        maior_tp_setup = np.zeros(self.n_tarefas + 1) 
        for j in range(0, self.n_tarefas + 1):
            maior_tp_setup[j] = maior_tp[j] + maior_setup[j]   

        #print(maior_tp_setup)

        maior_tp_setup_ordenado = []
        for j in range(0 , len(maior_tp_setup)):
            tupla = (j, maior_tp_setup[j])
            maior_tp_setup_ordenado.append(tupla)

        maior_tp_setup_ordenado = sorted(maior_tp_setup_ordenado, key=lambda x: x[1], reverse=True)
        #print("maior_tp_setup_ordenado")
        #print(maior_tp_setup_ordenado)
        
        #Determina o maior completion Time para uma tarefa j
        #TODO: Ver com o Thiago se tem que tirar a tarefa j caso ela seja uma das n_tarefas_por_maquina primeiras...
        #OBS: Foi feito como descrito acima...
        for j in range(1, self.n_tarefas + 1):
            tarefa_somada = False
            for i in range(0, n_tarefas_por_maquina - 1):
                if maior_tp_setup_ordenado[i][0] == j:
                    tarefa_somada = True    
                self.maior_completion_time[j] += int(maior_tp_setup_ordenado[i][1])    
            if tarefa_somada:
                self.maior_completion_time[j] += maior_tp_setup_ordenado[n_tarefas_por_maquina-1][1]
            else:
                self.maior_completion_time[j] += maior_tp_setup[j] 
            
        #print("Maiores Completion Time:")
        #print(self.maior_completion_time)
        #print("Datas de entregas")
        #print(self.data_entrega)

    
        #Determinar o maior data de entrega de uma tarefa j.
        #inicialmente é definido a maior distancia dos clientes j para os outros clientes
        #print("Distancias")
        #print(self.tempo_viagem)
        maior_distancia = np.zeros(self.n_tarefas + 1) 
        for j in range(0, self.n_tarefas + 1):
            maior = 0
            for k in range(0, self.n_tarefas + 1):
                if maior < self.tempo_viagem[j][k]:
                    maior = self.tempo_viagem[j][k]                 
            maior_distancia[j] = maior
        #print("Maior distancia")
        #print(maior_distancia)
        
        maior_distancia_ordenado = []
        for j in range(0 , len(maior_distancia)):
            tupla = (j, maior_distancia[j])
            maior_distancia_ordenado.append(tupla)

        maior_distancia_ordenado = sorted(maior_distancia_ordenado, key=lambda x: x[1], reverse=True)
        #print("maior distancia ordenado")
        #print(maior_distancia_ordenado)
        #Calcular os tempos de entrega para isso vamos dividir o numero de tarefas por veiculo
       # o tempo de partida do veiculo é igual ao maior completion time dentre todas as tarefas
       # O tempo de entrega será definido utilizando as maiores distancias e colocando a tarefa j como ultima
       # a ser entregue. Neste caso eu considero que todas as tarefas serão entregues pelo ultimo veiculo
       #logo a data de partida do veiculo é igual ao maior Completion Time dentre todas as tarefas.
        
        #self.n_veiculos = 2
        n_tarefas_por_veiculos = math.ceil(self.n_tarefas/self.n_veiculos)
        #print("n_tarefas_por_veiculos", n_tarefas_por_veiculos)
        
        for j in range(1, self.n_tarefas + 1):
            self.maior_data_entrega[j] = max(self.maior_completion_time) #tempo de inicio da viagem
            self.maior_data_entrega[j] += maior_distancia[0] #distancia entre o deposito e o cliente 
            for i in range(0, n_tarefas_por_veiculos - 2):
                self.maior_data_entrega[j] += int(maior_distancia_ordenado[i][1])    
            
            self.maior_data_entrega[j] += maior_distancia[j] 

        #calcula o maior atraso ponderado para cada tarefa
        for j in range(1, self.n_tarefas + 1):
            if self.maior_data_entrega[j] > self.data_entrega[j]:
                self.maior_atraso_ponderado[j] = (self.maior_data_entrega[j] - self.data_entrega[j]) * self.penalidade_atraso[j]


    def calcula_estatistica (self):
        self.tp_medio = np.average(self.tempo_processamento)
        self.setup_medio = np.average(self.tempo_setup)
        self.distancia_media = np.average(self.tempo_viagem)
        self.demanda_media = np.average(self.tamanho_tarefa)
        self.capacidade_media = np.average(self.capacidade_veiculo)

    def carregar_instancia(self):
        aux_nome = self.local.split('/')
        aux_nome = aux_nome[len(aux_nome)-1].split('.')
        self.nome = aux_nome[0]
        arquivo = open(self.local, 'r')

        #numero de maquinas
        linha = arquivo.readline()
        linha = linha.strip()
        aux = linha.split(':')
        self.n_maquinas = (int)(aux[1])


        #numero Tarefas
        linha = arquivo.readline()
        linha = linha.strip()
        aux = linha.split(':')
        self.n_tarefas = (int)(aux[1])


        #numero veiculos
        linha = arquivo.readline()
        linha = linha.strip()
        aux = linha.split(':')
        self.n_veiculos = (int)(aux[1])


        linha = arquivo.readline() #Capacidade_Total
        linha = arquivo.readline() #Demanda total
        linha = arquivo.readline() #setup min
        linha = arquivo.readline() #setup max
        linha = arquivo.readline() #Raio
        linha = arquivo.readline() #circulos
        linha = arquivo.readline() #TP min
        linha = arquivo.readline() #TP max
        linha = arquivo.readline() #Demanda_Min
        linha = arquivo.readline() #Priority_Factor
        linha = arquivo.readline() #Range_Factor_R
        linha = arquivo.readline() #U_factor
        linha = arquivo.readline() #Alpha
        linha = arquivo.readline() #Alpha



        #ENTRADA ANTIGAS
        #Tempos de processamento
        linha = arquivo.readline()
        self.tempo_processamento = np.zeros((self.n_maquinas, (self.n_tarefas + 1)))
        for j in range(0, self.n_tarefas + 1):
            linha = arquivo.readline()
            linha = linha.strip()
            linha = linha.split("\t")
            k = 1
            for i in range(0, self.n_maquinas):
                self.tempo_processamento[i][j] = int (linha[k]);
                k = k + 2
        linha = arquivo.readline()


        # Tempos de processamento
        #linha = arquivo.readline()
        #self.tempo_processamento = np.zeros((self.n_maquinas, (self.n_tarefas + 1)))
        #for i in range(0, self.n_maquinas):
        #    linha = arquivo.readline()
        #    linha = linha.strip()
        #    linha = linha.split("\t")
        #    for j in range(0, self.n_tarefas + 1):
        #        self.tempo_processamento[i][j] = linha[j];




        #Tempos de setup
        linha = arquivo.readline()
        self.tempo_setup = np.zeros((self.n_maquinas, self.n_tarefas+1, self.n_tarefas+1))
        for i in range(0, self.n_maquinas):
            linha = arquivo.readline()
            for j in range(0, self.n_tarefas + 1):
                linha = arquivo.readline()
                linha = linha.strip()
                linha = linha.split("\t")
               # print(linha)
                for k in range(0, self.n_tarefas + 1):
                    self.tempo_setup[i][j][k] = linha[k]



        # tamanho das tarefas
        linha = arquivo.readline()
        self.tamanho_tarefa = np.zeros(self.n_tarefas + 1)
        linha = arquivo.readline()
        linha = linha.strip()
        linha = linha.split("\t")
        for j in range(0, self.n_tarefas + 1):
            self.tamanho_tarefa[j] = linha[j]



        # datas de entregas
        linha = arquivo.readline()
        self.data_entrega = np.zeros(self.n_tarefas + 1)
        linha = arquivo.readline()
        linha = linha.strip()
        linha = linha.split("\t")
        for j in range(0, self.n_tarefas + 1):
            self.data_entrega[j] = linha[j]


        # penalidade de atraso
        linha = arquivo.readline()
        self.penalidade_atraso = np.zeros(self.n_tarefas + 1)
        linha = arquivo.readline()
        linha = linha.strip()
        linha = linha.split("\t")
        for j in range(0, self.n_tarefas + 1):
            self.penalidade_atraso[j] = linha[j]



        # Capacidade dos veiculos
        linha = arquivo.readline()
        self.capacidade_veiculo = np.zeros(self.n_veiculos)
        linha = arquivo.readline()
        linha = linha.strip()
        linha = linha.split("\t")
        for j in range(0, self.n_veiculos):
            self.capacidade_veiculo[j] = linha[j]

        linha = arquivo.readline()  # Custo_Fixo_Veiculo
        linha = arquivo.readline()  # Coordenadas_Clientes
        linha = arquivo.readline()  # Coordenadas_Clientes
        for j in range(0, self.n_tarefas +1 ): #coordenadas dos clientes
            linha = arquivo.readline()

        # Tempos de viagem
        linha = arquivo.readline()
        self.tempo_viagem = np.zeros((self.n_tarefas + 1, self.n_tarefas + 1))
        for j in range(0, self.n_tarefas + 1):
            linha = arquivo.readline()
            linha = linha.strip()
            linha = linha.split("\t")
            for k in range(0, self.n_tarefas + 1):
               self.tempo_viagem[j][k] = int(linha[k])

        linha = arquivo.readline()  # Custo_Viagem
        for i in range(0, self.n_veiculos):
            linha = arquivo.readline()  # Custo_Viagem
            for j in range(0, self.n_tarefas + 1):
                linha = arquivo.readline()  # Custo_Viagem

        # Velocidade dos veiculos
        linha = arquivo.readline()
        self.velocidade_veiculos = np.zeros(self.n_veiculos)
        linha = arquivo.readline()
        linha = linha.strip()
        linha = linha.split("\t")
        for j in range(0, self.n_veiculos):
            self.velocidade_veiculos[j] = int(linha[j])


    def imprimir_instancia(self):
        print("numero maquinas: {}".format(self.n_maquinas))
        print("numero tarefas: {}".format(self.n_tarefas))
        print("numero veiculo: {}".format(self.n_veiculos))
        print("tempos de processamento")
        print(self.tempo_processamento)
        print("tempos de setup")
        print(self.tempo_setup)
        print("tamanho das tarefas")
        print(self.tamanho_tarefa)
        print("Datas de entrega")
        print(self.data_entrega)
        print("penalidade de atraso")
        print(self.penalidade_atraso)
        print("capacidade dos veiculos")
        print(self.capacidade_veiculo)
        print("tempos de Viagem")
        print(self.tempo_viagem)
        print("velocidade dos veiculos")
        print(self.velocidade_veiculos)