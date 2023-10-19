import numpy as np
import time
import itertools
import sys
import statistics
import copy
from gym_customizedEnv.envs.Heuristicas.instancia import Instancia
from gym_customizedEnv.envs.Heuristicas.solucao import Solucao
import random

# construtor
class Heuristicas:
    
    tempo_Neh = 0;
    tempo_PIFH = 0;
    def __init__(self, instancia):
        self.instancia = instancia
        self.solucoes = []


    def mostraTempoExecucaoFuncao(self):
        print("tempo gasto no NEH durante a execuçao:{} ".format(self.tempo_Neh))
        print("tempo gasto no PIFH durante a execuçao:{} ".format(self.tempo_PIFH))

    def solucao_inicial(self, op_p_linha = 0):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        # inicialmente cria o p_linha
        if op_p_linha == 0:
            p_linha = self.cria_p_linha()
        elif op_p_linha == 1:
            p_linha = self.cria_p_linha_id_01()
        else:
            res = random.sample(range(1,self.instancia.n_tarefas+1),self.instancia.n_tarefas)
            p_linha = []
            for i in range(self.instancia.n_tarefas):
                p_linha.append((res[i], 0))
        # aloca as tarefas nas máquinas
        for j in p_linha:
            self.insereTarefaMelhorMaquina(solucao, j[0])
        # define o CompletionTime
        solucao.calcula_completion_time(self.instancia)
        # cria o d_linha
        d_linha = self.cria_d_linha(solucao)

        # aloca as tarefas nos veiculos
        for j in d_linha:
            #self.insereTarefaMelhorRota(solucao, j[0])
            self.insereTarefaMelhorRota_1(solucao, j[0])

        # testa a solução e verifica se é uma solução valida!
        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
            solucao.calcula_funcaoObjetivo(self.instancia)
            # solucao.imprimir_solucao()
            # print("Valor da Funcao objetivo: {}".format(solucao.FO))
            # add a solução valida no vetor de soluções
            #self.solucoes.append(solucao)
            return solucao
        else:
            return None
    #busca local no p_linha alinhado a busca local do d_linha com restart
    def busca_local_2(self, solucao,tamanho_best = 5, bl_d_linha_com_restar = True, tempo_limite = 3600):
        best_solutions = []
        tempo_inicio = time.time()
        p_linha = copy.deepcopy(solucao.ordemInsercaoMaquinas)

        solucao.cria_id()
        best = copy.deepcopy(solucao)
        best_solutions.append(copy.deepcopy(solucao))
        op = 0
        should_restart = True
        while(should_restart):
            should_restart = False
            if(op == 0): #swap
                tamanho = len(p_linha)
                for i in range(tamanho - 1):
                    for j in range(i + 1, tamanho):
                        tempo_fim = time.time()
                        if(tempo_fim - tempo_inicio > tempo_limite):
                            if (best.verifica_solucao_valida(self.instancia)):
                                best.calcula_funcaoObjetivo(self.instancia)
                                return best , best_solutions
                            else:
                                print("\n\n\n ERRo \n\n\n\n")

                        elemento = p_linha[i]
                        p_linha[i] = p_linha[j]
                        p_linha[j] = elemento
                        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        for k in p_linha:
                            self.insereTarefaMelhorMaquina(solucao, k[0])

                        solucao.calcula_completion_time(self.instancia)
                        solucaoInvalida = False
                        # cria o d_linha
                        d_linha = self.cria_d_linha(solucao)
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False):
                            solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                            if bl_d_linha_com_restar:
                                solucao, n_u = self.busca_local_d_linha(solucao, tempo_inicio, tempo_limite, best_solutions, tamanho_best)                       
                            else:
                                solucao, n_u = self.busca_local_d_linha_sem_restart(solucao, tempo_inicio, tempo_limite, best_solutions, tamanho_best)                       

                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            if (solucao.FO < best.FO):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break
                            

                        elemento = p_linha[i]
                        p_linha[i] = p_linha[j]
                        p_linha[j] = elemento

                    if should_restart == True:
                        break
                if should_restart == False and op == 0 :
                    should_restart = True
                    op = 1

            else: #insertion
                tamanho = len(p_linha)
                for i in range(tamanho - 1):
                    elemento = p_linha[i]
                    p_linha.remove(elemento)
                    for j in range(tamanho):
                        tempo_fim = time.time()
                        if(tempo_fim - tempo_inicio > tempo_limite):
                            if (best.verifica_solucao_valida(self.instancia)):
                                best.calcula_funcaoObjetivo(self.instancia)
                                return best , best_solutions
                            else:
                                print("\n\n\n ERRo \n\n\n\n")

                        if i == j:
                            continue
                        p_linha.insert(j, elemento)

                        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        for k in p_linha:
                            self.insereTarefaMelhorMaquina(solucao, k[0])

                        solucao.calcula_completion_time(self.instancia)
                        
                        solucaoInvalida = False
                        # cria o d_linha
                        d_linha = self.cria_d_linha(solucao)
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if (solucaoInvalida == False):
                            
                            solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
                            
                            if bl_d_linha_com_restar:
                                solucao, n_u = self.busca_local_d_linha(solucao,  tempo_inicio, tempo_limite,best_solutions, tamanho_best)                       
                            else:                 
                                solucao, n_u  = self.busca_local_d_linha_sem_restart(solucao, tempo_inicio, tempo_limite,best_solutions, tamanho_best)
                
                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            if (solucao.FO < best.FO):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break

                            

                        p_linha.remove(elemento)
                    
                    if should_restart == False:
                        p_linha.insert(i, elemento)

                    if should_restart == True:
                        break

        if (best.verifica_solucao_valida(self.instancia)):
            best.calcula_funcaoObjetivo(self.instancia)
            return best , best_solutions

    #busca local no p_linha alinhado a busca local do d_linha sem restart
    def busca_local_2_semRestart(self, solucao, tamanho_best = 5, tempo_limite=3600):
        best_solutions = []
        tempo_inicio = time.time()
        
        p_linha = solucao.ordemInsercaoMaquinas

        solucao.cria_id()
        best = copy.deepcopy(solucao)
        best_solutions.append(copy.deepcopy(solucao))
        
        #swap
        tamanho = len(p_linha)
        for i in range(tamanho - 1):
            for j in range(i + 1, tamanho):
                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")


                elemento = p_linha[i]
                p_linha[i] = p_linha[j]
                p_linha[j] = elemento
                solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                for k in p_linha:
                    self.insereTarefaMelhorMaquina(solucao, k[0])

                solucao.calcula_completion_time(self.instancia)
                
                solucaoInvalida = False
                # cria o d_linha
                d_linha = self.cria_d_linha(solucao)
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;

                melhorou = False;
                if(solucaoInvalida == False):    
                    solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    solucao, n_u  = self.busca_local_d_linha_sem_restart(solucao, tempo_inicio, tempo_limite,best_solutions, tamanho_best)                       
                            
                    if tamanho_best > 0:    
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True
                if melhorou == False:                
                    elemento = p_linha[i]
                    p_linha[i] = p_linha[j]
                    p_linha[j] = elemento

                    
        #insertion
        tamanho = len(p_linha)
        for i in range(tamanho - 1):
            elemento = p_linha[i]
            p_linha.remove(elemento)
            melhorou = False
            for j in range(tamanho):
                if i == j:
                    continue

                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")


                p_linha.insert(j, elemento)

                solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                for k in p_linha:
                    self.insereTarefaMelhorMaquina(solucao, k[0])

                solucao.calcula_completion_time(self.instancia)
                solucaoInvalida = False
                # cria o d_linha
                d_linha = self.cria_d_linha(solucao)
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;
                if(solucaoInvalida == False):
                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                    solucao, n_u = self.busca_local_d_linha_sem_restart(solucao, tempo_inicio, tempo_limite, best_solutions, tamanho_best)
                    
                    if tamanho_best > 0:        
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True

                    p_linha.remove(elemento)
                    
            p_linha.insert(i, elemento)
            if(melhorou == True):
                p_linha = copy.deepcopy(best.ordemInsercaoMaquinas)
                   

        if (best.verifica_solucao_valida(self.instancia)):
            best.calcula_funcaoObjetivo(self.instancia)
            return best , best_solutions


    def busca_local_1 (self, solucao):
        solucao = self.busca_local_p_linha(solucao)
        solucao = self.busca_local_d_linha(solucao)
        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.calcula_funcaoObjetivo(self.instancia)
            solucao.cria_id()
            vetor = []
            return solucao, vetor

    #apenas a busca local no p_linha
    def busca_local_p_linha(self, solucao, p_linha_inicial = [], flag = 0, best_solutions = [], tamanho_best = 5):
        p_linha = solucao.ordemInsercaoMaquinas
        best = copy.deepcopy(solucao)
        op = 0
        should_restart = True
        while(should_restart):
            should_restart = False
            if(op == 0): #swap
                tamanho = len(p_linha)
                for i in range(tamanho - 1):
                    for j in range(i + 1, tamanho):
                        elemento = p_linha[i]
                        p_linha[i] = p_linha[j]
                        p_linha[j] = elemento
                        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        for k in p_linha:
                            self.insereTarefaMelhorMaquina(solucao, k[0])

                        solucao.calcula_completion_time(self.instancia)
                        solucaoInvalida = False
                        # cria o d_linha
                        d_linha = self.cria_d_linha(solucao)
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False):
                            solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            #solucao.calcula_funcaoObjetivo(self.instancia)
                            if(solucao.FO < best.FO ):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break
                        elemento = p_linha[i]
                        p_linha[i] = p_linha[j]
                        p_linha[j] = elemento

                    if should_restart == True:
                        break
                if should_restart == False and op == 0 :
                    should_restart = True
                    op = 1

            else: #insertion
                tamanho = len(p_linha)
                for i in range(tamanho - 1):
                    elemento = p_linha[i]
                    p_linha.remove(elemento)
                    for j in range(tamanho):
                        if i == j:
                            continue
                        p_linha.insert(j, elemento)

                        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        for k in p_linha:
                            self.insereTarefaMelhorMaquina(solucao, k[0])

                        solucao.calcula_completion_time(self.instancia)
                        solucaoInvalida = False
                        # cria o d_linha
                        d_linha = self.cria_d_linha(solucao)
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False):
                            solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                            #solucao.calcula_funcaoObjetivo(self.instancia)
                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            if (solucao.FO < best.FO):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break

                        p_linha.remove(elemento)
                        #p_linha.insert(i, elemento)
                    if should_restart == False:
                        p_linha.insert(i, elemento)

                    if should_restart == True:
                        break

        return best

    def busca_local_p_linha_semRestart(self, solucao, tamanho_best = 5, tempo_limite = 3600):
        best_solutions = []
        tempo_inicio = time.time()
        
        p_linha = solucao.ordemInsercaoMaquinas

        solucao.cria_id()
        best = copy.deepcopy(solucao)
        best_solutions.append(copy.deepcopy(solucao))
        
        #swap
        tamanho = len(p_linha)
        for i in range(tamanho - 1):
            for j in range(i + 1, tamanho):
                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")


                elemento = p_linha[i]
                p_linha[i] = p_linha[j]
                p_linha[j] = elemento
                solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                for k in p_linha:
                    self.insereTarefaMelhorMaquina(solucao, k[0])

                solucao.calcula_completion_time(self.instancia)
                
                solucaoInvalida = False
                # cria o d_linha
                d_linha = self.cria_d_linha(solucao)
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;

                melhorou = False;
                if(solucaoInvalida == False):    
                    solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    if tamanho_best > 0:    
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True
                if melhorou == False:                
                    elemento = p_linha[i]
                    p_linha[i] = p_linha[j]
                    p_linha[j] = elemento

                    
        #insertion
        tamanho = len(p_linha)
        for i in range(tamanho - 1):
            elemento = p_linha[i]
            p_linha.remove(elemento)
            melhorou = False
            for j in range(tamanho):
                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")

                if i == j:
                    continue
                p_linha.insert(j, elemento)

                solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                for k in p_linha:
                    self.insereTarefaMelhorMaquina(solucao, k[0])

                solucao.calcula_completion_time(self.instancia)
                solucaoInvalida = False
                # cria o d_linha
                d_linha = self.cria_d_linha(solucao)
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;
                if(solucaoInvalida == False):
                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                    if tamanho_best > 0:
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True

                    p_linha.remove(elemento)
                    
            p_linha.insert(i, elemento)
            if(melhorou == True):
                p_linha = copy.deepcopy(best.ordemInsercaoMaquinas)
                   

        if (best.verifica_solucao_valida(self.instancia)):
            best.calcula_funcaoObjetivo(self.instancia)
            return best , best_solutions


    def busca_local_d_linha(self, s,  tempo_inicio, tempo_limite = 3600, best_solutions = [], tamanho_best = 5):
        solucao = copy.deepcopy(s)

        best = copy.deepcopy(solucao)
        d_linha = copy.deepcopy(solucao.ordemInsercaoRotas)

        op = 0
        should_restart = True
        while (should_restart):         
            should_restart = False
            if (op == 0):  # swap
                tamanho = len(d_linha)
                for i in range(tamanho - 1):
                    for j in range(i + 1, tamanho):
                        tempo_fim = time.time()
                        #print("bl d_linha swap", tempo_fim - tempo_inicio," tempo limite: ",tempo_limite)
                        if(tempo_fim - tempo_inicio > tempo_limite):
                            if (best.verifica_solucao_valida(self.instancia)):
                                best.calcula_funcaoObjetivo(self.instancia)
                                return best , best_solutions
                            else:
                                print("\n\n\n ERRo \n\n\n\n")

                        elemento = d_linha[i]
                        d_linha[i] = d_linha[j]
                        d_linha[j] = elemento

                        solucao.reset_rota()
                        solucaoInvalida = False
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False):            
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
                            
                            #solucao.calcula_funcaoObjetivo(self.instancia)
                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            if (solucao.FO < best.FO):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break
                        
                        elemento = d_linha[i]
                        d_linha[i] = d_linha[j]
                        d_linha[j] = elemento

                    if should_restart == True:
                        break
                if should_restart == False and op == 0:
                    should_restart = True
                    op = 1

            else:  # insertion
                tamanho = len(d_linha)
                for i in range(tamanho - 1):
                    elemento = d_linha[i]
                    d_linha.remove(elemento)
                    for j in range(tamanho):
                        tempo_fim = time.time()
                        #print("bl d_linha insert", tempo_fim - tempo_inicio," tempo limite: ",tempo_limite)
                        if(tempo_fim - tempo_inicio > tempo_limite):
                            if (best.verifica_solucao_valida(self.instancia)):
                                best.calcula_funcaoObjetivo(self.instancia)
                                return best , best_solutions
                            else:
                                print("\n\n\n ERRo \n\n\n\n")
                        if i == j:
                            continue
                        d_linha.insert(j, elemento)

                        solucao.reset_rota()
                        solucaoInvalida = False
                        for k in d_linha:
                            if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False):            
                           
                            solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)

                            #solucao.calcula_funcaoObjetivo(self.instancia)
                            if tamanho_best > 0:
                                self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                            if (solucao.FO < best.FO):
                                best = copy.deepcopy(solucao)
                                op = 0
                                should_restart = True
                                break
                            
                                
                        d_linha.remove(elemento)
                    if should_restart == False :
                        d_linha.insert(i, elemento)

                    if should_restart == True:
                        break

        return best , best_solutions

    def busca_local_d_linha_sem_restart(self, s, tempo_inicio, tempo_limite=3600,  best_solutions = [], tamanho_best = 5):
        solucao = copy.deepcopy(s)
        best = copy.deepcopy(solucao)
        d_linha = solucao.ordemInsercaoRotas

        # swap
        tamanho = len(d_linha)
        for i in range(tamanho - 1):
            for j in range(i + 1, tamanho):
                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")
                
                
                elemento = d_linha[i]
                d_linha[i] = d_linha[j]
                d_linha[j] = elemento

                solucao.reset_rota()
                solucaoInvalida = False
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;
                melhorou = False
                if(solucaoInvalida == False):            
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    if tamanho_best > 0:
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True
                if(melhorou == False):        
                    elemento = d_linha[i]
                    d_linha[i] = d_linha[j]
                    d_linha[j] = elemento

                    

        # insertion
        tamanho = len(d_linha)
        for i in range(tamanho - 1):
            elemento = d_linha[i]
            d_linha.remove(elemento)
            melhorou = False
            for j in range(tamanho):
                tempo_fim = time.time()
                if(tempo_fim - tempo_inicio > tempo_limite):
                    if (best.verifica_solucao_valida(self.instancia)):
                        best.calcula_funcaoObjetivo(self.instancia)
                        return best , best_solutions
                    else:
                        print("\n\n\n ERRo \n\n\n\n")

                if i == j:
                    continue
                d_linha.insert(j, elemento)

                solucao.reset_rota()
                solucaoInvalida = False
                for k in d_linha:
                    if(self.insereTarefaMelhorRota(solucao, k[0]) == False):
                        solucaoInvalida = True
                        break;
                if(solucaoInvalida == False):            
                    solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
                    if tamanho_best > 0:
                        self.verifica_melhor_solucao(solucao, best_solutions, tamanho_best)
                    #solucao.calcula_funcaoObjetivo(self.instancia)
                    if (solucao.FO < best.FO):
                        best = copy.deepcopy(solucao)
                        melhorou = True
                                        
                d_linha.remove(elemento)
                   
            d_linha.insert(i, elemento)
            if(melhorou == True):
                d_linha = copy.deepcopy(best.ordemInsercaoRotas)

        return best , best_solutions

    # metodos
    def heuristica1(self):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        #inicialmente cria o p_linha
        p_linha = self.cria_p_linha()
        
        #aloca as tarefas nas máquinas
        for j in p_linha:
            self.insereTarefaMelhorMaquina(solucao,j[0])
        #define o CompletionTime
        solucao.calcula_completion_time(self.instancia)
        #cria o d_linha
        d_linha = self.cria_d_linha(solucao)

        #aloca as tarefas nos veiculos
        for j in d_linha:
            self.insereTarefaMelhorRota(solucao,j[0])

        #testa a solução e verifica se é uma solução valida!
        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.calcula_funcaoObjetivo(self.instancia)
            # solucao.imprimir_solucao()
            # print("Valor da Funcao objetivo: {}".format(solucao.FO))
            #add a solução valida no vetor de soluções
            self.solucoes.append(solucao)


        #Parte 2 -> Apos criar a primeira solução é feita as permutações dos vetores p_linha e d_linha
        #swap P-vetor
        p_vetor = []
        p_vetor =  self.swap_vetor(p_linha)
        for p_item in p_vetor:
            solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
            for j in p_item:
                self.insereTarefaMelhorMaquina(solucao,j[0])
            solucao.calcula_completion_time(self.instancia)

            # cria o d_linha_aux
            d_linha_aux = self.cria_d_linha(solucao)

            # aloca as tarefas nos veiculos
            for j in d_linha_aux:
                self.insereTarefaMelhorRota(solucao,j[0])

            # testa a solução e verifica se é uma solução valida!
            if (solucao.verifica_solucao_valida(self.instancia)):
                solucao.calcula_funcaoObjetivo(self.instancia)
                # solucao.imprimir_solucao()
                # print("Valor da Funcao objetivo: {}".format(solucao.FO))
                # add a solução valida no vetor de soluções
                self.solucoes.append(copy.deepcopy(solucao))

                #faz a permutação do d_linha_Aux
                d_vetor = []
                d_vetor  = self.swap_vetor(d_linha_aux)
                for d_item in d_vetor:
                    solucao.reset_rota()
                    # aloca as tarefas nos veiculos
                    for j in d_item:
                        self.insereTarefaMelhorRota(solucao,j[0])
                    if (solucao.verifica_solucao_valida(self.instancia)):
                        solucao.calcula_funcaoObjetivo(self.instancia)
                        # solucao.imprimir_solucao()
                        # print("Valor da Funcao objetivo: {}".format(solucao.FO))
                        # add a solução valida no vetor de soluções
                        self.solucoes.append(copy.deepcopy(solucao))
                    else:
                        print("solucao Invalida heuristica1 -> 002")

                # faz o insertion do d_linha_Aux
                d_vetor = []
                d_vetor = self.insertion_vetor(d_linha_aux)
                for d_item in d_vetor:
                    solucao.reset_rota()
                    # aloca as tarefas nos veiculos
                    for j in d_item:
                        self.insereTarefaMelhorRota(solucao,j[0])
                    if (solucao.verifica_solucao_valida(self.instancia)):
                        solucao.calcula_funcaoObjetivo(self.instancia)
                        # solucao.imprimir_solucao()
                        #print("Valor da Funcao objetivo: {}".format(solucao.FO))
                        # add a solução valida no vetor de soluções
                        self.solucoes.append(copy.deepcopy(solucao))
                    else:
                        print("solucao Invalida heuristica1 -> 003")
            else:
                print("solucao Invalida heuristica1 -> 001")

        # insertion P-vetor
        p_vetor = []
        p_vetor = self.insertion_vetor(p_linha)
        for p_item in p_vetor:
                solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                for j in p_item:
                    self.insereTarefaMelhorMaquina(solucao, j[0])
                solucao.calcula_completion_time(self.instancia)

                # cria o d_linha_aux
                d_linha_aux = self.cria_d_linha(solucao)

                # aloca as tarefas nos veiculos
                for j in d_linha_aux:
                    self.insereTarefaMelhorRota(solucao, j[0])

                # testa a solução e verifica se é uma solução valida!
                if (solucao.verifica_solucao_valida(self.instancia)):
                    solucao.calcula_funcaoObjetivo(self.instancia)
                    # solucao.imprimir_solucao()
                    #print("Valor da Funcao objetivo: {}".format(solucao.FO))
                    # add a solução valida no vetor de soluções
                    self.solucoes.append(copy.deepcopy(solucao))

                    # faz a permutação do d_linha_Aux
                    d_vetor = []
                    d_vetor = self.swap_vetor(d_linha_aux)
                    for d_item in d_vetor:
                        solucao.reset_rota()
                        # aloca as tarefas nos veiculos
                        for j in d_item:
                            self.insereTarefaMelhorRota(solucao, j[0])
                        if (solucao.verifica_solucao_valida(self.instancia)):
                            solucao.calcula_funcaoObjetivo(self.instancia)
                            # solucao.imprimir_solucao()
                            #print("Valor da Funcao objetivo: {}".format(solucao.FO))
                            # add a solução valida no vetor de soluções
                            self.solucoes.append(copy.deepcopy(solucao))
                        else:
                            print("solucao Invalida heuristica1 -> 005")

                    # faz o insertion do d_linha_Aux
                    d_vetor = []
                    d_vetor = self.insertion_vetor(d_linha_aux)
                    for d_item in d_vetor:
                        solucao.reset_rota()
                        # aloca as tarefas nos veiculos
                        for j in d_item:
                            self.insereTarefaMelhorRota(solucao, j[0])
                        if (solucao.verifica_solucao_valida(self.instancia)):
                            solucao.calcula_funcaoObjetivo(self.instancia)
                            # solucao.imprimir_solucao()
                            # print("Valor da Funcao objetivo: {}".format(solucao.FO))
                            # add a solução valida no vetor de soluções
                            self.solucoes.append(copy.deepcopy(solucao))
                        else:
                            print("solucao Invalida heuristica1 -> 006")
                else:
                    print("solucao Invalida heuristica1 -> 004")


    def melhorSolucao(self):
        print("\n\n\n")
        print("Quantidade de Solucoes Encontradas: {}".format(len(self.solucoes)))

        solucao = Solucao(self.instancia.n_tarefas,self.instancia.n_maquinas, self.instancia.n_veiculos)
        solucao.FO = sys.maxsize
        for s in self.solucoes:
            if(s.FO < solucao.FO):
                solucao = copy.deepcopy(s)
        return solucao

    def insertion_vetor (self, vetor):
        original  = vetor
        retorno = []
        tamanho = len(vetor)
        for i in range(tamanho - 1):
            elemento = vetor[i]
            vetor.remove(elemento)
            for j in range (i+1 , tamanho):
                vetor.insert (j,elemento)
                retorno.append(vetor.copy())
                vetor.remove(elemento)
            vetor.insert(i, elemento)
        return retorno

    def swap_vetor (self, vetor):
        retorno = []
        tamanho = len(vetor)
        for i in range(tamanho - 1):
            for j in range (i+1 , tamanho):
                elemento = vetor[i]
                vetor[i] = vetor[j]
                vetor[j] = elemento
                retorno.append(vetor.copy())
                elemento = vetor[i]
                vetor[i] = vetor[j]
                vetor[j] = elemento
        return retorno


    #PFIH
    #Versão 2 - Otimizada
    def insereTarefaMelhorRota(self,solucao,tarefa):
        inicio = time.time()
        
        melhor_veiculo = 0
        melhor_posicao = 0
        menor_wt = -1
        wt_veiculo = 0
       
        
        for i in range(0,self.instancia.n_veiculos):
            if(solucao.ocupacao_veiculo[i] + self.instancia.tamanho_tarefa[tarefa] <= self.instancia.capacidade_veiculo[i]):
                for j in range(1, len(solucao.rotas[i])+1):
                    solucao.rotas[i].insert(j,tarefa)
                    FO = 0#solucao.wtVeiculos[i]

                    start_veiculo = max(solucao.completionTime[tarefa],solucao.tempoInicioVeiculo[i])
                    dt_Entrega = start_veiculo
                    for t in range(1, len(solucao.rotas[i])):
                        t_Ant = solucao.rotas[i][t-1]
                        t_ =  solucao.rotas[i][t]
                        dt_Entrega += self.instancia.tempo_viagem[t_][t_Ant] * self.instancia.velocidade_veiculos[i] 
                        atraso = dt_Entrega - self.instancia.data_entrega[t_]
                        if (atraso > 0):
                            FO += atraso * self.instancia.penalidade_atraso[t_]
                     
                    wt_veic_aux = FO
                    for t in range(0,self.instancia.n_veiculos):
                        if(t!=i):
                            FO += solucao.wtVeiculos[t]
                
                    if(menor_wt > FO or menor_wt == -1):
                        menor_wt = FO
                        wt_veiculo = wt_veic_aux
                        melhor_veiculo = i
                        melhor_posicao = j
                    del (solucao.rotas[i][j])
            
                    
        
        if(menor_wt != -1):
            solucao.rotas[melhor_veiculo].insert(melhor_posicao, tarefa)
            solucao.ocupacao_veiculo[melhor_veiculo] += self.instancia.tamanho_tarefa[tarefa]
            #atualiza os valores
            solucao.wtVeiculos[melhor_veiculo] = wt_veiculo
            solucao.tempoInicioVeiculo[melhor_veiculo] = max(solucao.completionTime[tarefa],solucao.tempoInicioVeiculo[melhor_veiculo])
            solucao.FO = sum(solucao.wtVeiculos)
            
            fim = time.time()
            #print("Tempo NEH{}".format(inicio-fim))
            self.tempo_PIFH += fim - inicio


            return True
        else:
            fim = time.time()
            #print("Tempo NEH{}".format(inicio-fim))
            self.tempo_PIFH += fim - inicio

            return False

        
        

    #PFIH
    #Versão 1 - primeira implementacao
    def insereTarefaMelhorRota_1(self,solucao,tarefa):
        inicio = time.time()
        
        melhor_veiculo = 0
        melhor_posicao = 0
        menor_wt = -1
        for i in range(0,self.instancia.n_veiculos):
            if(solucao.ocupacao_veiculo[i] + self.instancia.tamanho_tarefa[tarefa] <= self.instancia.capacidade_veiculo[i]):
                for j in range(1, len(solucao.rotas[i])+1):
                    solucao.rotas[i].insert(j,tarefa)
                    solucao.calcula_tempoSaidaVeiculo()
                    solucao.calcula_dataEntrega(self.instancia)
                    solucao.calcula_atrasoTarefas(self.instancia)
                    solucao.calcula_funcaoObjetivo_somenteFo(self.instancia)
                    
                    if(menor_wt > solucao.FO or menor_wt == -1):
                        menor_wt = solucao.FO
                        melhor_veiculo = i
                        melhor_posicao = j
                    del (solucao.rotas[i][j])
                    #fim - original

        if(menor_wt != -1):
            solucao.rotas[melhor_veiculo].insert(melhor_posicao, tarefa)
            solucao.ocupacao_veiculo[melhor_veiculo] += self.instancia.tamanho_tarefa[tarefa]
            solucao.calcula_tempoSaidaVeiculo()
            solucao.calcula_dataEntrega(self.instancia)
            solucao.calcula_atrasoTarefas(self.instancia)

           # print(self.solucao.rotas)
        #else:
            #print("insereTarefaMelhorRota: A tarefa não pode ser incluida em nenhuma rota.")

        fim = time.time()
        #print("Tempo NEH{}".format(inicio-fim))
        self.tempo_PIFH += fim - inicio
        
    #TODO:TOCAR dividir o n de clientes / n de veiculos
    #TODO:Não está finalizad a função
    #Insere as tarefas de acordo com o d_linha, porem insere até encher o veiculo
    def insereTarefaVeiculos(self,solucao, d_linha):
        veiculo = 0
        for j in range(0,len(d_linha)):
            melhor_posicao = 0
            menor_wt = -1

            if( self.instancia.capacidade_veiculo[veiculo] >= solucao.ocupacao_veiculo[veiculo] + self.instancia.tamanho_tarefa[d_linha[j][0]] ):
                self.insereTarefaMelhorRotaVeiculo(solucao, d_linha[j][0], veiculo)
            else:
                if(veiculo + 1 < self.instancia.n_veiculos):
                    veiculo += 1
                    self.insereTarefaMelhorRotaVeiculo(solucao, d_linha[j][0], veiculo)
                else:
                    print("insereTarefaVeiculos: tarefa {} nao adicionada na rota".format(d_linha[j][0]))

    #Insere a tarefa na rota na melhor posição de um veiculo especifico
    def insereTarefaMelhorRotaVeiculo(self,solucao, tarefa,veiculo):
        menor_wt = -1;
        melhor_posicao = 0
        for j in range(1, len(solucao.rotas[veiculo])+1):
            solucao.rotas[veiculo].insert(j,tarefa)
            solucao.calcula_tempoSaidaVeiculo_unico(veiculo)
            solucao.calcula_dataEntrega_veiculo(self.instancia,veiculo)
            solucao.calcula_atrasoTarefas(self.instancia)
            solucao.calcula_funcaoObjetivo_somenteFo(self.instancia)
            if(menor_wt > solucao.FO or menor_wt == -1):
                menor_wt = solucao.FO
                melhor_posicao = j
            del (solucao.rotas[veiculo][j])
        if (menor_wt != -1):
            solucao.rotas[veiculo].insert(melhor_posicao, tarefa)
            solucao.ocupacao_veiculo[veiculo] += self.instancia.tamanho_tarefa[tarefa]
            print(solucao.rotas)
        else:
            print("insereTarefaMelhorRota: A tarefa não pode ser incluida em nenhuma rota.")

    #algoritmo NEH
    def  insereTarefaMelhorMaquina(self,solucao,tarefa):
        inicio = time.time()
        melhor_maquina = 0
        melhor_posicao = 0
        menor_makespan = -1
        menor_completionTime = -1
        for i in range(0,self.instancia.n_maquinas):
            for j in range(len(solucao.sequenciaTarefas[i]), len(solucao.sequenciaTarefas[i])+1):
                solucao.sequenciaTarefas[i].insert(j,tarefa)
                solucao.calcula_completion_time(self.instancia)
                makespan = max(solucao.completionTime)
                completionTime = solucao.completionTime[tarefa]
                if(menor_completionTime > completionTime or menor_completionTime == -1):
                    melhor_posicao = j
                    melhor_maquina = i
                    menor_makespan = makespan
                    menor_completionTime = solucao.completionTime[tarefa]
                elif (menor_completionTime == completionTime):
                    if(menor_makespan >  makespan):
                        menor_makespan = makespan
                        melhor_posicao = j
                        melhor_maquina = i
                        menor_completionTime = solucao.completionTime[tarefa]

#                if(menor_makespan >  makespan or menor_makespan == -1):
#                    melhor_posicao = j
#                    melhor_maquina = i
#                    menor_makespan = makespan
#                    menor_completionTime = solucao.completionTime[tarefa]
#                elif (menor_makespan == makespan):
#                    if(menor_completionTime > completionTime):
#                        menor_makespan = makespan
 #                       melhor_posicao = j
#                        melhor_maquina = i
#                        menor_completionTime = solucao.completionTime[tarefa]

                del(solucao.sequenciaTarefas[i][j])

        solucao.sequenciaTarefas[melhor_maquina].insert(melhor_posicao,tarefa)
        fim = time.time()
        #print("Tempo NEH{}".format(inicio-fim))
        self.tempo_Neh += fim - inicio
        #print(solucao.sequenciaTarefas)

    # corresponde a mediana do tempo de processamento + a mediana do tempo de setup
    def cria_p_linha(self):
        p_linha = []
        for j in range(1, self.instancia.n_tarefas + 1):
            # calcula a mediana do tempo de procesasmento
            tps = []
            setups = []
            for i in range(0, self.instancia.n_maquinas):
                tps.append(self.instancia.tempo_processamento[i][j])
                for k in range(1, self.instancia.n_tarefas + 1):
                    setups.append(self.instancia.tempo_setup[i][k][j])
            # TODO: verificar se vai adicionar o tempo de viagem entre o cliente e o deposito
            # TODO: lembrar que o tempo de viagem varia para cada veiculo.
            mediana = statistics.median(tps) + statistics.median(setups)
            p_linha.append((j, mediana))
        # ordenar p_linha
        # TODO: Se a mediana for igual, a tarefa com menor tempo de processamento.
        p_linha.sort(key=lambda x: x[1], reverse=True)
        # print(p_linha)
        return p_linha

    # Cria o p linha com base nas rotas
    #a ideia é montar a rotas(utiliza o p_linha inicial como completion time) e a partir das rotas definir o novo p_linha 
    #(qe será a ordem que as tarefas a serem inseridas nas máquinas)
    def cria_p_linha_id_01(self):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        completion_time = self.cria_p_linha()
        
        for j in completion_time:
            solucao.completionTime[j[0]] = int(j[1])
        
        d_linha = self.cria_d_linha(solucao)
        #d_linha = []
        #for j in range(1, self.instancia.n_tarefas + 1):
        #    aux = solucao.completionTime[j] - self.instancia.data_entrega[j]
        #    d_linha.append((j, aux))
        #d_linha.sort(key=lambda x: x[1], reverse=True)

        #monta a solução do segundo estagio
        for j in d_linha:
            self.insereTarefaMelhorRota(solucao,j[0])
        #calcular datas de entrgas
        
        #verificar se todas as tarefas estão nas rotas
        cont = 0
        for i in solucao.rotas:
            cont += len(i);
        if cont != self.instancia.n_veiculos + self.instancia.n_tarefas:
            print ("Erro criar p_linha versao 1")

        solucao.calcula_tempoSaidaVeiculo()
        solucao.calcula_dataEntrega(self.instancia)
        

        p_linha = []

        for j in range(1, self.instancia.n_tarefas+1):
            aux =  solucao.dataEntrega[j] - self.instancia.data_entrega[j]
            p_linha.append((j, aux))
        #data de entregas - data limiete te entregas
        #decrescente
        p_linha.sort(key=lambda x: x[1], reverse=True)# + atraso primeiro


        return p_linha


    #corresponde a dirença entre tempo de conlusão e data de entrega
    def cria_d_linha(self, solucao):#solução inicial
        d_linha = []

        for j in range(1, self.instancia.n_tarefas + 1):
            aux = self.instancia.data_entrega[j] - solucao.completionTime[j]
            #aux = (self.instancia.data_entrega[j] - solucao.completionTime[j])/ self.instancia.penalidade_atraso[j]
            #aux = self.instancia.data_entrega[j]
            #TODO: verificar o aux igual
            d_linha.append((j, aux))

        d_linha.sort(key=lambda x: x[1])
        return d_linha


    #faz a verificação da melhor solução, caso melhor atualiza e preenche o vetor com as 'n' soluções
    #se trocou a solução a função retorna true
    def verifica_melhor_solucao(self, solucao, best_solutions, tamanho_best):
        solucao.cria_id()    
        add = True

        if len(best_solutions) == 0:
             best_solutions.append(copy.deepcopy(solucao))
             return

        pior = best_solutions[0]
        for s in best_solutions:
            if solucao.idSolucao == s.idSolucao:
                add = False
                break
            if pior.FO < s.FO:
                pior = s
            
        if len(best_solutions) < tamanho_best and add:
            best_solutions.append(copy.deepcopy(solucao))
        elif add:
            if solucao.FO < pior.FO:     
                best_solutions.remove(pior)
                best_solutions.append(copy.deepcopy(solucao))

        #teste integridade das instancia
        #s = self.cria_solucao_p_linha_d_linha(solucao.ordemInsercaoMaquinas, solucao.ordemInsercaoRotas)
        #if(solucao.idSolucao != s.idSolucao):
        #    print("algo de errado aconteceu ao montar a solucao a parti do p e d Linha")

    #Cria uma solução a partir do d_linha e p_linha
    #ao final uma solução é retornada
    def cria_solucao(self, p_linha, d_linha):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
        solucao.ordemInsercaoRotas = copy.deepcopy(d_linha)
        for k in p_linha:
            self.insereTarefaMelhorMaquina(solucao, k[0])

        solucao.calcula_completion_time(self.instancia)
        for k in d_linha:
            self.insereTarefaMelhorRota(solucao, k[0])

        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.calcula_funcaoObjetivo(self.instancia)
            solucao.cria_id()

        return solucao

    def cria_solucao_p_linha(self, p_linha):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
        for k in p_linha:
            self.insereTarefaMelhorMaquina(solucao, k[0])

        solucao.calcula_completion_time(self.instancia)
        # cria o d_linha
        d_linha = self.cria_d_linha(solucao)
        for k in d_linha:
            self.insereTarefaMelhorRota(solucao, k[0])

        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.calcula_funcaoObjetivo(self.instancia)
            solucao.cria_id()

        return solucao

    def cria_solucao_p_linha_d_linha(self, p_linha, d_linha):
        solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        solucao.ordemInsercaoMaquinas = copy.deepcopy(p_linha)
        for k in p_linha:
            self.insereTarefaMelhorMaquina(solucao, k[0])

        solucao.calcula_completion_time(self.instancia)
        #print(d_linha)
        #

        #print("novo d_linha")
        # cria o d_linha
        #d_linha = self.cria_d_linha(solucao)
        #print(d_linha)
        for k in d_linha:
            self.insereTarefaMelhorRota(solucao, k[0])

        if (solucao.verifica_solucao_valida(self.instancia)):
            solucao.calcula_funcaoObjetivo(self.instancia)
            solucao.cria_id()

        return solucao

    def pfrelink(self, a, b ):
        tempoExecucao = 0
        if a.FO < b.FO :
            solucao_a = copy.deepcopy(b)
            solucao_b = copy.deepcopy(a)
        else: 
            solucao_a = copy.deepcopy(a)
            solucao_b = copy.deepcopy(b)

        inicio = []
        fim = []
        n_iteracoes = 0
        for i in range(0, a.n_tarefas):
            fim.append((solucao_b.ordemInsercaoMaquinas[i][0], i))
            valor = solucao_a.ordemInsercaoMaquinas[i][0]
            posicao = 0
            for j in range(0,a.n_tarefas):
                if solucao_b.ordemInsercaoMaquinas[j][0] == valor :
                    posicao = j
                    break
            inicio.append((valor, posicao))
            if posicao != i:
                n_iteracoes += 1
        it = 0
        best = copy.deepcopy(solucao_b)
       
        while it < n_iteracoes - 1 :
            bestFO = -1
            ORM = []
            for i in range(0, a.n_tarefas):
                #faz a troca 
                if i != inicio[i][1]:
                    #copia o vetor inicio para ordemInsercaoMaquinas
                    ordemInsercaoMaquinas = copy.deepcopy(inicio)
                    # faz a troca 
                    pos_f = ordemInsercaoMaquinas[i][1] 
                    ele = ordemInsercaoMaquinas[i]
                   
                    ordemInsercaoMaquinas[i] = ordemInsercaoMaquinas[pos_f]
                    ordemInsercaoMaquinas[pos_f] = ele
                    
                    #criar uma nova solucao com a troca 
                    solucao = self.cria_solucao_p_linha(ordemInsercaoMaquinas)
                    
                    if bestFO == -1:
                        bestFO = solucao.FO
                        ORM = copy.deepcopy(ordemInsercaoMaquinas)
                    elif bestFO > solucao.FO :
                        bestFO = solucao.FO
                        ORM = copy.deepcopy(ordemInsercaoMaquinas)

                    inicioTempo = time.time()
        
                    #Faz a busca local na solucao
                    
                    solucao = self.busca_local_2(solucao) 
                    #solucao = self.busca_local_1(solucao)
                    #solucao = self.busca_local_2_semRestart(solucao)
                    
                    #print(solucao[0].idSolucao)
                    fimTempo = time.time()
                    
                    tempoExecucao += fimTempo - inicioTempo
                    
                    if best.FO > solucao[0].FO :
                        best = copy.deepcopy(solucao[0])
                    if n_iteracoes - it == 2 :
                        break
                 
            inicio = copy.deepcopy(ORM)
            it+=1
       
        
        return best


        