from site import venv

import numpy as np
import gym_customizedEnv.envs.Heuristicas.instancia

class Solucao:
    tempo_execucao = -1
    n_tarefas = 0
    n_veiculos = 0
    n_maquinas = 0


    sequenciaTarefas = []# Sequencimaneto das tarefas.
    completionTime= [] #
    tempoInicioVeiculo = []
    dataEntrega = []
    atrasoTarefa = []
    rotas = []
    ocupacao_veiculo = []
    FO = -1
    idSolucao = ""
    ordemInsercaoMaquinas = [] #p_linha
    ordemInsercaoRotas = [] #d_linha
    wtVeiculos = [] #atraso por veiculos
    #construtor
    def __init__(self, n_tarefas, n_maquinas, n_veicuos):
        self.n_tarefas = n_tarefas
        self.n_maquinas = n_maquinas
        self.n_veiculos = n_veicuos
        self.aloca_vetores()
        
        #print("init")


    #def __call__(self):
    #    print("call ")

    #metodos
    def aloca_vetores(self):
        self.sequenciaTarefas = [] #np.zeros((self.n_maquinas, 1))
        for i in range(self.n_maquinas):
            self.sequenciaTarefas.append([0])

        self.rotas = []  # np.zeros((self.n_maquinas, 1))
        for i in range(self.n_veiculos):
            self.rotas.append([0])

        self.ocupacao_veiculo = np.zeros((self.n_veiculos, 1))

        self.completionTime = np.zeros(self.n_tarefas + 1)
        self.tempoInicioVeiculo = np.zeros(self.n_veiculos)
        self.dataEntrega = np.zeros(self.n_tarefas+1)
        self.atrasoTarefa = np.zeros(self.n_tarefas+1)
        self.wtVeiculos = np.zeros(self.n_veiculos)

    def imprimir_solucao(self):
        print("numero maquinas: {}".format(self.n_maquinas))
        print("numero tarefas: {}".format(self.n_tarefas))
        print("numero veiculo: {}".format(self.n_veiculos))
        print("Sequenciamento das tarefas")
        print(self.sequenciaTarefas)
        print("Completion time")
        print(self.completionTime)
        print("Datas de entrega")
        print(self.dataEntrega)
        print("Atraso")
        print(self.atrasoTarefa)
        print("Rotas")
        print(self.rotas)
        print("tempo de inicio")
        print(self.tempoInicioVeiculo)

    def calcula_completion_time(self, instancia):
        for i in range(0, len(self.sequenciaTarefas)):
            for j in range(1, len(self.sequenciaTarefas[i])):
                tarefaAnterior = self.sequenciaTarefas[i][j-1]
                tarefa = self.sequenciaTarefas[i][j]
                self.completionTime[tarefa] = self.completionTime[tarefaAnterior] + instancia.tempo_setup[i][tarefaAnterior][tarefa] + instancia.tempo_processamento[i][tarefa]

    def calcula_completion_time_maquina(self, instancia, maquina):
        for j in range(1, len(self.sequenciaTarefas[maquina])):
            tarefaAnterior = self.sequenciaTarefas[maquina][j-1]
            tarefa = self.sequenciaTarefas[maquina][j]
            self.completionTime[tarefa] = self.completionTime[tarefaAnterior] + instancia.tempo_setup[maquina][tarefaAnterior][tarefa] + instancia.tempo_processamento[maquina][tarefa]


    def calcula_tempoSaidaVeiculo(self) :
        for v in range(0, len(self.rotas)):
            maior = 0
            for t in range(0, len(self.rotas[v])):
                tarefa = self.rotas[v][t]
                if(self.completionTime[tarefa] > maior):
                    maior = self.completionTime[tarefa]

            self.tempoInicioVeiculo[v] = maior

    def calcula_tempoSaidaVeiculo_unico(self,veiculo) :
        maior = 0
        for t in range(0, len(self.rotas[veiculo])):
            tarefa = self.rotas[veiculo][t]
            if(self.completionTime[tarefa] > maior):
                maior = self.completionTime[tarefa]

        self.tempoInicioVeiculo[veiculo] = maior

    def calcula_dataEntrega(self, instancia):
        for v in range(0, len(self.rotas)):
            soma = self.tempoInicioVeiculo[v]
            self.dataEntrega[0] = 0
            for t in range(1, len(self.rotas[v])):
                tarefaAnterior = self.rotas[v][t-1]
                tarefa =  self.rotas[v][t]
                soma += instancia.tempo_viagem[tarefa][tarefaAnterior] * instancia.velocidade_veiculos[v]
                self.dataEntrega[tarefa] = soma

    def calcula_dataEntrega_veiculo(self, instancia,veiculo):
        soma = self.tempoInicioVeiculo[veiculo]
        self.dataEntrega[0] = 0
        for t in range(1, len(self.rotas[veiculo])):
            tarefaAnterior = self.rotas[veiculo][t-1]
            tarefa =  self.rotas[veiculo][t]
            soma += instancia.tempo_viagem[tarefa][tarefaAnterior] * instancia.velocidade_veiculos[veiculo]
            self.dataEntrega[tarefa] = soma


    def calcula_atrasoTarefas(self, instancia):
        self.atrasoTarefa[0] = 0;
        for j in range(1, self.n_tarefas+1):
            if (self.dataEntrega[j] - instancia.data_entrega[j] > 0):
                self.atrasoTarefa[j] = self.dataEntrega[j] - instancia.data_entrega[j];
            else:
                self.atrasoTarefa[j] = 0


    def calcula_funcaoObjetivo(self, instancia):
        self.calcula_completion_time(instancia)
        self.calcula_tempoSaidaVeiculo()
        self.calcula_dataEntrega(instancia)
        self.calcula_atrasoTarefas(instancia)
        self.FO = 0
        for j in range(1, self.n_tarefas+1):
            self.FO += self.atrasoTarefa[j] * instancia.penalidade_atraso[j]

    def calcula_funcaoObjetivo_somenteFo(self, instancia):
        self.FO = 0
        for j in range(1, self.n_tarefas+1):
            self.FO += self.atrasoTarefa[j] * instancia.penalidade_atraso[j]

    def verifica_solucao_valida_original(self, instancia):
        #Verifica a Se todas as tarefas estão nas maquinas
        tarefas = []
        totalTarefas = 0
        for i in range(0, self.n_maquinas):
            totalTarefas += len(self.sequenciaTarefas[i])
            for j in range(1, len(self.sequenciaTarefas[i])):
                tarefas.append(self.sequenciaTarefas[i][j])
        tarefas_alocadas = set(tarefas)
        if (len(tarefas_alocadas) != self.n_tarefas):
            print("Solucao Invalida - Nem todas as tarefas estão alocas as máquinas")
            return False

        if(totalTarefas != self.n_tarefas + self.n_maquinas ):
            print("Tarefas repetidas na solução (maquinas)")
            return False
        
        # Verifica a Se todas as tarefas estão nas rotas;
        tarefas = []
        totalTarefas = 0
        for i in range(0, self.n_veiculos):
            totalTarefas += len(self.rotas[i])
            for j in range(1, len(self.rotas[i])):
                tarefas.append(self.rotas[i][j])
        tarefas_alocadas = set(tarefas)
        if (len(tarefas_alocadas) != self.n_tarefas):
            print("Solucao Invalida - Nem todas as tarefas estão em alguma rota")
            return False
        
        if(totalTarefas != self.n_tarefas + self.n_veiculos):
            print("Tarefas repetidas na solução (Rotas)")
            return False
        

        #Verifica a Se alguma rota extrapola a capacidade do veiculo;
        for v in range(0, self.n_veiculos):
            demanda = 0;
            for i in range(0, len(self.rotas[v])):
                tarefa = self.rotas[v][i]
                demanda += instancia.tamanho_tarefa[tarefa]
            if (demanda > instancia.capacidade_veiculo[v]):
                print("Solucao Invalida - Capacidade do veiculo excedido")
                return False

        return True

    def verifica_solucao_valida(self, instancia):
        #Verifica a Se todas as tarefas estão nas maquinas
        tarefas = []
        #totalTarefas = 0
        #for i in range(0, self.n_maquinas):
        #    totalTarefas += len(self.sequenciaTarefas[i])
        #    for j in range(1, len(self.sequenciaTarefas[i])):
        #        tarefas.append(self.sequenciaTarefas[i][j])
        #tarefas_alocadas = set(tarefas)
        #if (len(tarefas_alocadas) != self.n_tarefas):
        #    print("Solucao Invalida - Nem todas as tarefas estão alocas as máquinas")
        #    return False

        #if(totalTarefas != self.n_tarefas + self.n_maquinas ):
        #    print("Tarefas repetidas na solução (maquinas)")
        #    return False
        
        # Verifica a Se todas as tarefas estão nas rotas;
        tarefas = []
        totalTarefas = 0
        for i in range(0, self.n_veiculos):
            totalTarefas += len(self.rotas[i])
            for j in range(1, len(self.rotas[i])):
                tarefas.append(self.rotas[i][j])
        tarefas_alocadas = set(tarefas)
        if (len(tarefas_alocadas) != self.n_tarefas):
            print("Solucao Invalida - Nem todas as tarefas estão em alguma rota")
            return False
        
        if(totalTarefas != self.n_tarefas + self.n_veiculos):
            print("Tarefas repetidas na solução (Rotas)")
            return False
        

        #Verifica a Se alguma rota extrapola a capacidade do veiculo;
        #for v in range(0, self.n_veiculos):
        #    demanda = 0;
        #    for i in range(0, len(self.rotas[v])):
        #        tarefa = self.rotas[v][i]
        #        demanda += instancia.tamanho_tarefa[tarefa]
        #    if (demanda > instancia.capacidade_veiculo[v]):
        #        print("Solucao Invalida - Capacidade do veiculo excedido")
        #        return False

        return True


    def reset_rota(self):
        self.rotas = []  # np.zeros((self.n_maquinas, 1))
        for i in range(self.n_veiculos):
            self.ocupacao_veiculo[i] = 0
            self.rotas.append([0])
        self.wtVeiculos = np.zeros(self.n_veiculos)
        self.tempoInicioVeiculo = np.zeros(self.n_veiculos)
        self.dataEntrega = np.zeros(self.n_tarefas+1)
    
    def cria_id(self):
        self.idSolucao = str(int(self.FO))
        self.idSolucao += "."
        for i in range(0, self.n_maquinas):
            for j in self.sequenciaTarefas[i]:
                self.idSolucao += str(i)
                self.idSolucao += str(j)
        for v in range(0, self.n_veiculos):
            for j in self.rotas[v]:
                self.idSolucao += str(v)
                self.idSolucao += str(j)


    def cria_id_Solucao_VND(self):
        self.idSolucao = ""
        for j in self.ordemInsercaoMaquinas:
             self.idSolucao += str(j[0])
             self.idSolucao += "."
        self.idSolucao += "."
        for j in self.ordemInsercaoRotas:
             self.idSolucao += str(j[0])
             self.idSolucao += "."