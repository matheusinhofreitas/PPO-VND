import numpy as np
import time
import itertools
import sys
import statistics
import copy
import os
import math
import random

from gym_customizedEnv.envs.Heuristicas.instancia import Instancia
from gym_customizedEnv.envs.Heuristicas.solucao import Solucao
from gym_customizedEnv.envs.Heuristicas.heuristicas import Heuristicas
from gym_customizedEnv.envs.Heuristicas.read import *

#np.random.seed(42) # Set the random number generator to a fixed sequence.

class VND:
    
    
    def __init__(self, instancia):
        self.instancia = instancia
        self.solucoes = []
        self.solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        self.heuristica = Heuristicas(self.instancia)


    #def __del__(self): 
        #print('Destructor called, Employee deleted.')

    def teste(self):
        self.solucao = self.heuristica.solucao_inicial()
        self.Solver(0,2)

    def retornaSolucaoInicial(self):
        self.solucao = self.heuristica.solucao_inicial()
        if(self.solucao == None):
            self.solucao = self.heuristica.solucao_inicial(1)
        while(self.solucao == None):
           self.solucao = self.heuristica.solucao_inicial(2) 
        return self.solucao

    def vnd(self, replicacao):
        #np.random.seed(5) #tirar o seed para rodar. 

        self.solucao = self.heuristica.solucao_inicial()
        if(self.solucao == None):
            self.solucao = self.heuristica.solucao_inicial(1)
        best_solucao = copy.deepcopy(self.solucao)
        FO_inicial = best_solucao.FO

        best_solucao.cria_id_Solucao_VND()
        new_solucao = copy.deepcopy(self.solucao)
        print("Solucao Inicial: ", self.solucao.FO)
        n_it = 0
        n_it_sem_melhora = 0
        vizinhanca = np.random.randint(0, high=8);            
        while(n_it < 100):
            new_solucao = self.Solver(copy.deepcopy(new_solucao),0,vizinhanca)
            if(new_solucao.FO < best_solucao.FO):
                print("Melhorou no VND -  Vizinhanca:", vizinhanca)
                best_solucao = copy.deepcopy(new_solucao)
                n_it_sem_melhora = 0
            else:
                vizinhanca = np.random.randint(0, high=8)
                n_it_sem_melhora += 1
                new_solucao = self.pertuba_solucao(new_solucao, self.instancia)
                while(new_solucao.FO == -1):
                    new_solucao = self.pertuba_solucao(new_solucao, self.instancia)
                

            n_it += 1
        print("Solucao Apos VND: ", best_solucao.FO)
        print("Numero de Solucoes avaliadas pelo vnd: ", len(self.instancia.solucoes_Calculadas))
        Rest = open("Resultados/exec_"+str(replicacao)+"/"+str(self.instancia.nome)+".txt","w")
        Rest.write(str(self.instancia.nome)+";"+str(FO_inicial)+";"+str(best_solucao.FO)+";"+str(best_solucao.idSolucao)+"\n")
        Rest.close()        

        return self.solucao.FO, best_solucao.FO


    
    def Solver (self,solucao,LB,Escolha):
        new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        #vizinhanças para o d_linha
        if Escolha == 0:
            new_solucao = self.Swap (solucao.ordemInsercaoRotas,solucao,0,0)
        if Escolha == 1:
            new_solucao = self.Swap (solucao.ordemInsercaoRotas,solucao,1,0)
        if Escolha == 2:
            new_solucao = self.Insertion (solucao.ordemInsercaoRotas,solucao,0,0)
        if Escolha == 3:
            new_solucao = self.Insertion (solucao.ordemInsercaoRotas,solucao,1,0)
        
        #vizinhanças para o p_linha
        if Escolha == 4:
            new_solucao = self.Swap (solucao.ordemInsercaoMaquinas,solucao,0,1)
        if Escolha == 5:
            new_solucao = self.Swap (solucao.ordemInsercaoMaquinas,solucao,1,1)
        if Escolha == 6:
            new_solucao = self.Insertion (solucao.ordemInsercaoMaquinas,solucao,0,1)
        if Escolha == 7:
            new_solucao = self.Insertion (solucao.ordemInsercaoMaquinas,solucao,1,1)
        #pertuba a solucao
        if Escolha == 8:
            new_solucao = self.pertuba_solucao(solucao, self.instancia)
            while(new_solucao.FO == -1):
                    new_solucao = vnd.pertuba_solucao(solucao, self.instancia)  
            

        return new_solucao










    #realiza o swap na lista
    def swapPositions(self,list, pos1, pos2):
        list[pos1], list[pos2] = list[pos2], list[pos1]
        return list

    #realiza o insertion na lista
    def insertPositions(self,list, pos1, pos2):
        elemento = list[pos1]
        list.remove(elemento)
        list.insert(pos2,elemento)
        return list

    #Parametros: R = restart (0 = sem restart, 1 = com restart)
    #Parametros: L = Indica a lista que está sendo utilizada(0 = d_linha, 1 = p_linha)
    def Swap (self,Lista,solucao,R,L, taxa_pertubacao = 0):
        new_solucao = self.pertuba_solucao(solucao, self.instancia, taxa_pertubacao)
        while(new_solucao.FO == -1):
            new_solucao = self.pertuba_solucao(solucao, self.instancia, taxa_pertubacao)        

        solucao = new_solucao


        FOini = solucao.FO
        n = len(Lista)
        i=0
        ListaB = Lista
        solucaoB = copy.deepcopy(solucao)
        new_solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        while i < n:
            j=i+1
            while j < n:
                ListaNew = self.swapPositions(copy.deepcopy(Lista), i, j)
                #caso o swap seja feito no d_linha, devemos manter o sequenciamento e criar uma nova solucao com
                #a nova rota 
                if(L == 0):
                    new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                    new_solucao.ordemInsercaoMaquinas = copy.deepcopy(solucaoB.ordemInsercaoMaquinas)
                    for k in new_solucao.ordemInsercaoMaquinas:
                        self.heuristica.insereTarefaMelhorMaquina(new_solucao, k[0])
                    new_solucao.ordemInsercaoRotas = ListaNew

                    #cria o id da nova solucao
                    new_solucao.cria_id_Solucao_VND()
                    #caso a nova solucao nao tenha sido calculado, calcula o FO, se nao usa a solucao encontrada
                    
                    solucaoInvalida = False
                    for k in new_solucao.ordemInsercaoRotas:
                        if(self.heuristica.insereTarefaMelhorRota(new_solucao, k[0]) == False):
                            solucaoInvalida = True
                            break;
                    if(solucaoInvalida == False): 
                        new_solucao.calcula_funcaoObjetivo(self.instancia)
                    else:
                        #print("Gerou uma solucao Invalida.")
                        new_solucao.FO = -1

                    #adiciona a nova solucao na lista de solucoes ja calculadas
                    
                         
                #caso o swap seja feito no p_linha, devemos criar um nova solucao com um novo sequenciamento,
                #depois deve-se calcular um novo d_linha e criar um novo roteamento.
                #a nova rota 
                if(L == 1):
                    new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                    new_solucao.ordemInsercaoMaquinas = ListaNew
                    for k in ListaNew:
                        self.heuristica.insereTarefaMelhorMaquina(new_solucao, k[0])
                     # cria o d_linha
                    new_solucao.ordemInsercaoRotas = self.heuristica.cria_d_linha(new_solucao)

                    #cria o id da nova solucao
                    new_solucao.cria_id_Solucao_VND()
                    #caso a nova solucao nao tenha sido calculado, calcula o FO, se nao usa a solucao encontrada
                    
                    solucaoInvalida = False
                    for k in new_solucao.ordemInsercaoRotas:
                        if(self.heuristica.insereTarefaMelhorRota(new_solucao, k[0]) == False):
                            solucaoInvalida = True
                            break;
                    if(solucaoInvalida == False): 
                        new_solucao.calcula_funcaoObjetivo(self.instancia)
                    else:
                        #print("Gerou uma solucao Invalida.")
                        new_solucao.FO = -1

                    
                FO_new = new_solucao.FO
                FO_B = solucaoB.FO
                if new_solucao.FO != -1 and new_solucao.FO <= solucaoB.FO:
                    ListaB = ListaNew
                    solucaoB = copy.deepcopy(new_solucao)
                    if FO_new < FO_B:
                        if (R == 1):
                            j=0
                            i=0
                j +=1
            i+=1
        return solucaoB
    
    #Parametros: R = restart (0 = sem restart, 1 = com restart)
    #Parametros: L = Indica a lista que está sendo utilizada(0 = d_linha, 1 = p_linha)
    def Insertion (self,Lista,solucao,R,L, taxa_pertubacao = 0):
        new_solucao = self.pertuba_solucao(solucao, self.instancia, taxa_pertubacao)
        while(new_solucao.FO == -1):
            new_solucao = self.pertuba_solucao(solucao, self.instancia, taxa_pertubacao)        

        solucao = new_solucao


        FOini = solucao.FO
        n = len(Lista)
        i=0
        ListaB = Lista
        solucaoB = copy.deepcopy(solucao)
        new_solucao = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)

        while i < n:
            j=0
            while j < n:
                if (i != j):
                    ListaNew = self.insertPositions(copy.deepcopy(Lista), i, j)
                    
                    #caso o swap seja feito no d_linha, devemos manter o sequenciamento e criar uma nova solucao com
                    #a nova rota 
                    if(L == 0):
                        new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        new_solucao.ordemInsercaoMaquinas = copy.deepcopy(solucaoB.ordemInsercaoMaquinas)
                        for k in new_solucao.ordemInsercaoMaquinas:
                            self.heuristica.insereTarefaMelhorMaquina(new_solucao, k[0])
                        new_solucao.ordemInsercaoRotas = ListaNew
                        #cria o id da nova solucao
                        new_solucao.cria_id_Solucao_VND()
                        solucaoInvalida = False
                        for k in new_solucao.ordemInsercaoRotas:
                            if(self.heuristica.insereTarefaMelhorRota(new_solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False): 
                            new_solucao.calcula_funcaoObjetivo(self.instancia)
                        else:
                            #print("Gerou uma solucao Invalida.")
                            new_solucao.FO = -1
                            
                        #if(self.VerificaFO_ID(new_solucao.idSolucao)):
                            #print("Insertion L1")
                        
                    #caso o swap seja feito no p_linha, devemos criar um nova solucao com um novo sequenciamento,
                    #depois deve-se calcular um novo d_linha e criar um novo roteamento.
                    #a nova rota 
                    if(L == 1):
                        new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
                        new_solucao.ordemInsercaoMaquinas = ListaNew
                        for k in ListaNew:
                            self.heuristica.insereTarefaMelhorMaquina(new_solucao, k[0])
                        # cria o d_linha
                        new_solucao.ordemInsercaoRotas = self.heuristica.cria_d_linha(new_solucao)
                        #cria o id da nova solucao
                        new_solucao.cria_id_Solucao_VND()
                        #caso a nova solucao nao tenha sido calculado, calcula o FO, se nao usa a solucao encontrada
                        solucaoInvalida = False
                        for k in new_solucao.ordemInsercaoRotas:
                            if(self.heuristica.insereTarefaMelhorRota(new_solucao, k[0]) == False):
                                solucaoInvalida = True
                                break;
                        if(solucaoInvalida == False): 
                            new_solucao.calcula_funcaoObjetivo(self.instancia)
                        else:
                            #print("Gerou uma solucao Invalida.")
                            new_solucao.FO = -1
                        
                            
                        #if(self.VerificaFO_ID(new_solucao.idSolucao)):
                        #    print("Insertion L2")
                        
                    
                    
                    FO_new = new_solucao.FO
                    FO_B = solucaoB.FO
                    if new_solucao.FO != -1 and new_solucao.FO <= solucaoB.FO:
                        ListaB = ListaNew
                        solucaoB = copy.deepcopy(new_solucao)
                        if FO_new < FO_B:
                            if (R == 1):
                                j=0
                                i=0
                j +=1
            i+=1
        return solucaoB

    
    
    
    def pertuba_solucao(self, solucao, inst, taxa_pertubacao = 0):
        #1) Escolher aleatoriamente qual lista (1 - lista P, 2 - Lista R, 3 - ambas)
        lista = np.random.randint(1,high=3)
        #2) taxa_pertubacao - quantos Swaps e insertions vão ser feitos
        porcentagem = math.ceil(taxa_pertubacao)
        vnd = VND(inst)
        ordemInsercaoMaquinas = copy.deepcopy(solucao.ordemInsercaoMaquinas)
        ordemInsercaoRotas = copy.deepcopy(solucao.ordemInsercaoRotas)
        #3) Escolhe aleatoriamente os movimentos
        if(lista == 1):
            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoMaquinas = vnd.swapPositions(ordemInsercaoMaquinas, i, j)
            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoMaquinas = vnd.insertPositions(ordemInsercaoMaquinas, i, j)
        elif(lista == 2):
            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoRotas = vnd.swapPositions(ordemInsercaoRotas, i, j)
            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoRotas = vnd.insertPositions(ordemInsercaoRotas, i, j)
        elif(lista == 3):
            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoMaquinas = vnd.swapPositions(ordemInsercaoMaquinas, i, j)
                
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoRotas = vnd.swapPositions(ordemInsercaoRotas, i, j)

            for k in range(0, porcentagem):
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoMaquinas = vnd.insertPositions(ordemInsercaoMaquinas, i, j)    
                
                i = np.random.randint(1,high=inst.n_tarefas)
                j = np.random.randint(1,high=inst.n_tarefas)
                while i == j:
                    j = np.random.randint(1,high=inst.n_tarefas)
                ordemInsercaoRotas = vnd.insertPositions(ordemInsercaoRotas, i, j)  
                       
        #4) Constroi a solução
        solucao_new = Solucao(inst.n_tarefas, inst.n_maquinas, inst.n_veiculos)
        solucao_new.ordemInsercaoMaquinas = ordemInsercaoMaquinas
        solucao_new.ordemInsercaoRotas = ordemInsercaoRotas
        heuristica = Heuristicas(inst)
        for k in solucao_new.ordemInsercaoMaquinas:
            heuristica.insereTarefaMelhorMaquina(solucao_new, k[0])            
            
        solucaoInvalida = False
        for k in solucao_new.ordemInsercaoRotas:
            if(heuristica.insereTarefaMelhorRota(solucao_new, k[0]) == False):
                solucaoInvalida = True
                break;
        if(solucaoInvalida == False): 
            solucao_new.calcula_funcaoObjetivo(inst)
        else:
            #print("Gerou uma solucao Invalida.")
            solucao_new.FO = -1
                            
            
        return solucao_new    



    def VerificaFO_ID(self, id):
        FO = self.instancia.solucoes_Calculadas[id]
        s = str(id).split("..")
        ordemInsercaoMaquinas  = s[0].split(".")
        ordemInsercaoRotas = s[1].split(".")
        ordemInsercaoRotas.pop()        

        sol = Solucao(self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
        sol.ordemInsercaoMaquinas = ordemInsercaoMaquinas
        sol.ordemInsercaoRotas = ordemInsercaoRotas
        heuristica = Heuristicas(self.instancia)
        for k in sol.ordemInsercaoMaquinas:
            heuristica.insereTarefaMelhorMaquina(sol, int(k))
        solucaoInvalida = False
        for k in sol.ordemInsercaoRotas:
            if(heuristica.insereTarefaMelhorRota(sol, int(k)) == False):
                solucaoInvalida = True
                break;
        if(solucaoInvalida == False): 
            sol.calcula_funcaoObjetivo(self.instancia)
        else:
            #print("Gerou uma solucao Invalida.")
            sol.FO = -1
        print(sol.FO)   
        if sol.FO != FO:
            #print("ERRO - Divergencia de FO")
            return True
        return False