import numpy as np
import time
import itertools
import sys
import statistics
import copy
import os
import math
from gym_customizedEnv.envs.Heuristicas.instancia import Instancia
from gym_customizedEnv.envs.Heuristicas.solucao import Solucao
from gym_customizedEnv.envs.Heuristicas.read import *


class CalculaLB:
    path_instances = ""
#    instancia
    

    def __init__(self, path):
        self.path_instances = path

#LB inicial antes da reunião do dia 19.
    def teste(self):
        instancia_lb = {}
        cont_Instancias_q_n_conseguiu_Alocar_todos = 0 
        print("numero maquinas: {}".format(self.path_instances))
        files = listar_arquivos(self.path_instances)
        #files.sort(reverse=True)
        files.sort()
        try:
            files.remove("Amostra")
        except:
            print("An exception occurred: files.remove(\"Amostra\")")
        #Lê as instancias, 1 a 1.
        for nome in files:
            local = self.path_instances +"/"+nome
            inst = Instancia(local)

            #passo 1

            print(inst.nome)
            rc =  [] # service release date
            #rc.append(0)
            #calcula o menor TP para cada tarefa.
            for j in range(0, inst.n_tarefas + 1):
                menor_tp = inst.tempo_processamento[0][j]
                for i in range(0, inst.n_maquinas):
                    if(menor_tp > inst.tempo_processamento[i][j]):
                        menor_tp = inst.tempo_processamento[i][j]
                rc.append(menor_tp)
            print("Menor tp\n", rc)
            #calcula o menor Setup para cada tarefa.
            for j in range(1, inst.n_tarefas + 1):
                menor_setup = 100
                for k in range(1, inst.n_tarefas + 1):
                    if(j==k):
                        continue
                    for i in range(0, inst.n_maquinas):
                        if(menor_setup > inst.tempo_setup[i][j][k]):
                            menor_setup = inst.tempo_setup[i][j][k]
                rc[j]+=(menor_setup)
            print("Menor tp + menor setup\n", rc)
            #adiciona o tempo de viagem minimo 
            for j in range(1, inst.n_tarefas + 1):
                rc[j]+= inst.tempo_viagem[0][j]
            print("Menor tp + menor setup + distancia\n", rc)
             
            #transforma em um dicionario
            rc_dic = {}
            for j in range(0, inst.n_tarefas + 1):
                rc_dic[j] = rc[j]
            print("Print RCj\n", rc_dic)   
            

            #Passo 2    
            
            #calcula a maior distancia média
            
            maior_distancia_media  = 0;
            for j in range(0, inst.n_tarefas + 1):
                maior_distancia = 0
                for k in range(0, inst.n_tarefas + 1):
                    if(maior_distancia < inst.tempo_viagem[j][k]):        
                        maior_distancia = inst.tempo_viagem[j][k]
                maior_distancia_media += maior_distancia
            print("maior_distancia_soma", maior_distancia_media)
            #divide a maior_distancia_media  pelo a quantidade de veiculos
            maior_distancia_media = maior_distancia_media / inst.n_veiculos
            print("maior_distancia_media: ", maior_distancia_media)
            maior_rc = max(rc, key=int)
            print("maior_rc", maior_rc )
            UBE = maior_rc + maior_distancia_media
            print("UBE - ", UBE)
          

            #passo 3 - menor distancia entre os clientes
            pc = []
            pc.append(0)
            for j in range(1, inst.n_tarefas + 1):
                menor_distancia = 10000
                for k in range(1, inst.n_tarefas + 1):
                    if(k == j):
                        continue
                    if(menor_distancia > inst.tempo_viagem[j][k]):
                        menor_distancia = inst.tempo_viagem[j][k]
                pc.append(menor_distancia)

            print("\nPC")
            print(pc)

            #passo 4 
            ECT = []
            ECT = np.zeros((inst.n_tarefas + 1, (int(UBE) + 1)))
         
            for j in range(1, inst.n_tarefas + 1):
                for t in range(0, int(UBE) + 1):
                    ECT[j][t] = inst.penalidade_atraso[j] * max(0, t - inst.data_entrega[j]) / pc[j]
            
            #for j in range(1, inst.n_tarefas + 1):
            #    for t in range(0, int(UBE) + 1):
            #        print("%d - " % ECT[j][t], end = "")
            #    print("\n\n")

            #passo 5
            maior_capacidade = max(inst.capacidade_veiculo)
            print("Maior capacidade: ",maior_capacidade)
            capacidade_media = sum(inst.capacidade_veiculo) / inst.n_veiculos 
            print("Média capacidade: ",capacidade_media)
            capaciadeLimite = capacidade_media + (maior_capacidade -capacidade_media)
            print("Capacidade Limite: ",capaciadeLimite)
            
            capacidade_utilizada  = np.zeros(inst.n_veiculos)


            rotas = []
            for i in range(inst.n_veiculos):
                linha = [] # lista vazia
                rotas.append(linha)

            dataPartida = np.zeros(inst.n_veiculos)
            ECT_Utilizados = 0
            tarefasAlocadas = [];

            #pare cada tarefa, qual o menor t.
            print("ETC a partir de 1 para cada job")
            for j in range(1, inst.n_tarefas + 1):
                for t in range(0, int(UBE) + 1):
                    if(ECT[j][t] != 0):
                        print("Job ", j, " - Time ", t)
                        break;
            print("\n")
            rc_dic_ordenado = {}
            for i in sorted(rc_dic, key = rc_dic.get):
                 rc_dic_ordenado[i] = rc_dic[i]
                 #print(i, rc_dic[i])
            print("\nRC Ordenado")
            print(rc_dic_ordenado)


            #Vai adicionar ao veiculo a tarefa com menor rc.
            #depois vai atualizar o tempo de partida do veiculo com o rc+pc da tarefa que foi adicionada
            #depois vai olhar, se na data de partida do veiculo, ainda existe alguma tarefa com 
            #ETC igual a zero para add no veiculo
            
            veiculo = 0;
            del rc_dic_ordenado[0]
            rc_dic = rc_dic_ordenado
            while(veiculo < inst.n_veiculos):
                if(len(rc_dic_ordenado) == 0):
                    break;

                rc_dic = rc_dic_ordenado
                for j in rc_dic.keys():
                    tarefa = int(j)
                    print("Tarefa: ", tarefa, " ECT, " ,ECT[tarefa][int(dataPartida[veiculo])])
                    if(ECT[tarefa][int(dataPartida[veiculo])] <= 0 and ((capacidade_utilizada[veiculo] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or (capacidade_utilizada[veiculo] - inst.tamanho_tarefa[tarefa] < (maior_capacidade -capacidade_media)))):
                        #adiciona a tarefa no veiculo v
                        rotas[veiculo].append(tarefa) #adiciona a tarefe na rota
                        tarefasAlocadas.append(tarefa) #adiciona a tarefa no vetor de tarefas alocadas 
                        capacidade_utilizada[veiculo] += inst.tamanho_tarefa[tarefa]
                        #TODO: pegar o maior rc das tarefas da rota e somar com os pc[j] das tarefas j que estao no veiculo.
                        
                        if( dataPartida[veiculo] == 0 ):
                            dataPartida[veiculo] = rc[tarefa] + pc[tarefa]
                        else:
                            dataPartida[veiculo] = max(dataPartida[veiculo] , rc[tarefa]) + pc[tarefa]

                        ECT_Utilizados += ECT[tarefa][int(dataPartida[veiculo] - pc[tarefa])] * pc[tarefa] 
                        
                        rc_dic_ordenado.pop(tarefa, None)
                        tarefas_zero = retornaTarefasComECT_zero(ECT,rc_dic_ordenado, dataPartida[veiculo])
                        break;
                    #elif (ECT[tarefa][int(dataPartida[veiculo])] > 0):
                        #ECT maior que zero Ver o qe q faz. se abre outro veiculo ou nao.
                   #     print("ECT MAIOR QUE ZERO Comeca outro veiculo")
                   #     veiculo = veiculo + 1
                   #     break;
                    elif (((capacidade_utilizada[veiculo] + inst.tamanho_tarefa[tarefa] > capacidade_media) or (capacidade_utilizada[veiculo] - inst.tamanho_tarefa[tarefa] > (maior_capacidade -capacidade_media)))):
                        #Limite excedido do veiculo
                        print("Limite do Veiculo execeido Fazer a funcao para ver isso")
                        veiculo = veiculo + 1
                        break;

            print("Instanicia: ",inst.nome)
            print("\nECT_Utilizados: ", ECT_Utilizados)
            print("Tarefas Alocas em Rotas: ", len(tarefasAlocadas))
            print("Rotas")
            print(rotas)
            print("\nTamanho utilizado nos veiculos:")
            print(capacidade_utilizada)
            
            #ans = input()
            #print("-"*300)
            #print("\n"*10)

            if(len(tarefasAlocadas) != inst.n_tarefas):
                cont_Instancias_q_n_conseguiu_Alocar_todos += 1
                print("ERRO, NEM TODAS TAREFAS FORAM ALOCAS NESTA INSTANCIA")
                instancia_lb[inst.nome] = -1
            else:
                instancia_lb[inst.nome] = ECT_Utilizados
            


            #exit()
        print("Instancias que nao conseguiram alocar todas as tarfas nos veiculos:", cont_Instancias_q_n_conseguiu_Alocar_todos)

        print(instancia_lb)






    def teste_final(self):
        instancia_lb = {}
        cont_Instancias_q_n_conseguiu_Alocar_todos = 0 
        print("numero maquinas: {}".format(self.path_instances))
        files = listar_arquivos(self.path_instances)
        #files.sort(reverse=True)
        files.sort()
        try:
            files.remove("Amostra")
            files.remove("Amostra_2_LB_test")
        except:
            print("An exception occurred: files.remove(\"Amostra\")")
        #Lê as instancias, 1 a 1.
        for nome in files:
            local = self.path_instances +"/"+nome
            inst = Instancia(local)

            #passo 1

            print(inst.nome)
            rc =  [] # service release date
            #rc.append(0)
            #calcula o menor TP para cada tarefa.
            for j in range(0, inst.n_tarefas + 1):
                menor_tp = inst.tempo_processamento[0][j]
                for i in range(0, inst.n_maquinas):
                    if(menor_tp > inst.tempo_processamento[i][j]):
                        menor_tp = inst.tempo_processamento[i][j]
                rc.append(menor_tp)
            print("Menor tp\n", rc)
            #calcula o menor Setup para cada tarefa.
            for j in range(1, inst.n_tarefas + 1):
                menor_setup = 100
                for k in range(1, inst.n_tarefas + 1):
                    if(j==k):
                        continue
                    for i in range(0, inst.n_maquinas):
                        if(menor_setup > inst.tempo_setup[i][j][k]):
                            menor_setup = inst.tempo_setup[i][j][k]
                rc[j]+=(menor_setup)
            print("Menor tp + menor setup\n", rc)
            #adiciona o tempo de viagem minimo 
            for j in range(1, inst.n_tarefas + 1):
                rc[j]+= inst.tempo_viagem[0][j]
            print("Menor tp + menor setup + distancia\n", rc)
             
            #transforma em um dicionario
            rc_dic = {}
            for j in range(0, inst.n_tarefas + 1):
                rc_dic[j] = rc[j]
            print("Print RCj\n", rc_dic)   
            

            #Passo 2    
            
            #calcula a maior distancia média
            
            maior_distancia_media  = 0;
            for j in range(0, inst.n_tarefas + 1):
                maior_distancia = 0
                for k in range(0, inst.n_tarefas + 1):
                    if(maior_distancia < inst.tempo_viagem[j][k]):        
                        maior_distancia = inst.tempo_viagem[j][k]
                maior_distancia_media += maior_distancia
            print("maior_distancia_soma", maior_distancia_media)
            #divide a maior_distancia_media  pelo a quantidade de veiculos
            maior_distancia_media = maior_distancia_media / inst.n_veiculos
            print("maior_distancia_media: ", maior_distancia_media)
            maior_rc = max(rc, key=int)
            print("maior_rc", maior_rc )
            UBE = maior_rc + maior_distancia_media
            print("UBE - ", UBE)
          

            #passo 3 - menor distancia entre os clientes
            pc = []
            pc.append(0)
            for j in range(1, inst.n_tarefas + 1):
                menor_distancia = 10000
                for k in range(1, inst.n_tarefas + 1):
                    if(k == j):
                        continue
                    if(menor_distancia > inst.tempo_viagem[j][k]):
                        menor_distancia = inst.tempo_viagem[j][k]
                pc.append(menor_distancia)

            print("\nPC")
            print(pc)

            #passo 4 
            ECT = []
            ECT = np.zeros((inst.n_tarefas + 1, (int(UBE) + 1)))
         
            for j in range(1, inst.n_tarefas + 1):
                for t in range(0, int(UBE) + 1):
                    ECT[j][t] = inst.penalidade_atraso[j] * max(0, t - inst.data_entrega[j]) / pc[j]
            
            #for j in range(1, inst.n_tarefas + 1):
            #    for t in range(0, int(UBE) + 1):
            #        print("%d - " % ECT[j][t], end = "")
            #    print("\n\n")

            #passo 5
            maior_capacidade = max(inst.capacidade_veiculo)
            print("Maior capacidade: ",maior_capacidade)
            capacidade_media = sum(inst.capacidade_veiculo) / inst.n_veiculos 
            print("Média capacidade: ",capacidade_media)
            capaciadeLimite = capacidade_media + (maior_capacidade -capacidade_media)
            print("Capacidade Limite: ",capaciadeLimite)
            
            capacidade_utilizada  = np.zeros(inst.n_veiculos)


            rotas = []
            for i in range(inst.n_veiculos):
                linha = [] # lista vazia
                rotas.append(linha)

            dataPartida = np.zeros(inst.n_veiculos)
            
            tarefasAlocadas = [];

            #pare cada tarefa, qual o menor t.
            print("ETC a partir de 1 para cada job")
            for j in range(1, inst.n_tarefas + 1):
                for t in range(0, int(UBE) + 1):
                    if(ECT[j][t] != 0):
                        print("Job ", j, " - Time ", t)
                        break;
            print("\n")
            rc_dic_ordenado = {}
            for i in sorted(rc_dic, key = rc_dic.get):
                 rc_dic_ordenado[i] = rc_dic[i]
                 #print(i, rc_dic[i])
            print("\nRC Ordenado")
            print(rc_dic_ordenado)


            
            ECT_Utilizados = np.zeros(inst.n_veiculos)
            ECT_Ut = 0;
            del rc_dic_ordenado[0]
            rc_dic = rc_dic_ordenado
            #abre todos os veiculos e add as tarefas ordenadas pelo RC
            for v in range(0,inst.n_veiculos):
                rc_dic = rc_dic_ordenado
                for j in rc_dic.keys():
                    tarefa = int(j)
                    print("Tarefa: ", tarefa, " ECT, " ,ECT[tarefa][int(dataPartida[v])])
                    if((capacidade_utilizada[v] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or (capacidade_utilizada[v] - inst.tamanho_tarefa[tarefa] < (maior_capacidade -capacidade_media))):
                        #adiciona a tarefa no veiculo v
                        rotas[v].append(tarefa) #adiciona a tarefe na rota
                        tarefasAlocadas.append(tarefa) #adiciona a tarefa no vetor de tarefas alocadas 
                        capacidade_utilizada[v] += inst.tamanho_tarefa[tarefa]
                        #TODO: pegar o maior rc das tarefas da rota e somar com os pc[j] das tarefas j que estao no veiculo.
                        
                        if( dataPartida[v] == 0 ):
                            dataPartida[v] = rc[tarefa] + pc[tarefa]
                        else:
                            dataPartida[v] = max(dataPartida[v] , rc[tarefa]) + pc[tarefa]

                        ECT_Utilizados[v] += ECT[tarefa][int(dataPartida[v] - pc[tarefa])] #* pc[tarefa] 
                        ECT_Ut += ECT[tarefa][int(dataPartida[v] - pc[tarefa])] #* pc[tarefa]

                        rc_dic_ordenado.pop(tarefa, None)
                      
                        break;
            print("\n------------\n")
            #indica que ainda tem tarefas a serem alocadas nas rotas.
            #a ideia aqui é inserir a tarefa no veiculo que possua a menor ECT
            if( len(rc_dic_ordenado) != 0):
                while(len(rc_dic_ordenado) != 0): #enquanto estiver tarefas para serem adicionandos na rota
                    rc_dic = rc_dic_ordenado
                    for j in rc_dic.keys():
                        tarefa = int(j)
                        #procura o melhor veiculo para adicionar a tarefa.
                        melhor_veiculo = -1
                        menor_ECT = 10000000
                        for v in range(0,inst.n_veiculos):
                            if((capacidade_utilizada[v] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or (capacidade_utilizada[v] - inst.tamanho_tarefa[tarefa] < (maior_capacidade -capacidade_media))):
                                dp = max(dataPartida[v] , rc[tarefa]) + pc[tarefa]
                                ECT_Tarefa = ECT[tarefa][int(dp - pc[tarefa])] #* pc[tarefa]
                                print("Tarefa: ", tarefa, " ECT, " ,ECT_Tarefa)
                                if(ECT_Tarefa < menor_ECT ):
                                    menor_ECT = ECT_Tarefa
                                    melhor_veiculo = v
                        #adiciona a tarefa no veiculo certo.
                        if(melhor_veiculo != -1):
                            #adiciona a tarefa no veiculo v
                            rotas[melhor_veiculo].append(tarefa) #adiciona a tarefe na rota
                            tarefasAlocadas.append(tarefa) #adiciona a tarefa no vetor de tarefas alocadas 
                            capacidade_utilizada[melhor_veiculo] += inst.tamanho_tarefa[tarefa]
                            dataPartida[melhor_veiculo] = max(dataPartida[melhor_veiculo] , rc[tarefa]) + pc[tarefa]
                            ECT_Utilizados[melhor_veiculo] += ECT[tarefa][int(dataPartida[melhor_veiculo] - pc[tarefa])] #* pc[tarefa] 
                            ECT_Ut += ECT[tarefa][int(dataPartida[melhor_veiculo] - pc[tarefa])] #* pc[tarefa] 

                            rc_dic_ordenado.pop(tarefa, None)
                            break

            print("Instanicia: ",inst.nome)
            print("\nECT_Utilizados SOMA: ", ECT_Ut)
            print("\nECT_Utilizados Veiculos: ", ECT_Utilizados)
            NOVO_ECT = 0
            NOVO_ECT_2 = 0
            #para cada rota, vamos multiplicar o ECT UTILIZADO pelo menor tempo de procesamento da tarefa da tarefa da rota
            for v in range(0,inst.n_veiculos):
                menor_tp = 1000
                for t in range(0,len(rotas[v])):
                    tarefa = rotas[v][t]
                    for i in range(0,inst.n_maquinas):
                        if(menor_tp > inst.tempo_processamento[i][tarefa]):
                            menor_tp = inst.tempo_processamento[i][tarefa]
                NOVO_ECT += menor_tp * ECT_Utilizados[v] 
                NOVO_ECT_2 += menor_tp * ECT_Ut


            



            print("\nNOVO ECT_Utilizados: ", NOVO_ECT_2)
            print("\nNOVO ECT_Utilizados por veiculo: ", NOVO_ECT)
            print("Tarefas Alocas em Rotas: ", len(tarefasAlocadas))
            print("Rotas")
            print(rotas)
            print("\nTamanho utilizado nos veiculos:")
            print(capacidade_utilizada)
            
            pause = False
            if(pause):
                ans = input()
                print("-"*300)
                print("\n"*10)

            if(len(tarefasAlocadas) != inst.n_tarefas):
                cont_Instancias_q_n_conseguiu_Alocar_todos += 1
                print("ERRO, NEM TODAS TAREFAS FORAM ALOCAS NESTA INSTANCIA")
                instancia_lb[inst.nome] = -1
            else:
                instancia_lb[inst.nome] = math.ceil(NOVO_ECT) #arredonda para cima
            


            #exit()
        print("Instancias que nao conseguiram alocar todas as tarfas nos veiculos:", cont_Instancias_q_n_conseguiu_Alocar_todos)

        print(instancia_lb)
        return instancia_lb


#teste ideia do matheus
    def teste_com_completionTime(self):
        instancia_lb = {}
        cont_Instancias_q_n_conseguiu_Alocar_todos = 0 
        print("numero maquinas: {}".format(self.path_instances))
        files = listar_arquivos(self.path_instances)
        #files.sort(reverse=True)
        files.sort()
        try:
            files.remove("Amostra")
            files.remove("Amostra_2_LB_test")
        except:
            print("An exception occurred: files.remove(\"Amostra\")")
        #Lê as instancias, 1 a 1.
        for nome in files:
            local = self.path_instances +"/"+nome
            inst = Instancia(local)

            #passo 1

            print(inst.nome)
            tp_setup =  [] # service release date
            #calcula o menor TP para cada tarefa.
            for j in range(0, inst.n_tarefas + 1):
                menor_tp = inst.tempo_processamento[0][j]
                for i in range(0, inst.n_maquinas):
                    if(menor_tp > inst.tempo_processamento[i][j]):
                        menor_tp = inst.tempo_processamento[i][j]
                tp_setup.append(menor_tp)
            print("Menor tp\n", tp_setup)
            #calcula o menor Setup para cada tarefa.
            for j in range(1, inst.n_tarefas + 1):
                menor_setup = 100
                for k in range(1, inst.n_tarefas + 1):
                    if(j==k):
                        continue
                    for i in range(0, inst.n_maquinas):
                        if(menor_setup > inst.tempo_setup[i][j][k]):
                            menor_setup = inst.tempo_setup[i][j][k]
                tp_setup[j]+=(menor_setup)
            print("Menor tp + menor setup\n", tp_setup)
            #adiciona o tempo de viagem minimo 
            #for j in range(1, inst.n_tarefas + 1):
            #    tp_setup[j]+= inst.tempo_viagem[0][j]
            #print("Menor tp + menor setup + distancia\n", rc)
             
            for j in range(0, inst.n_tarefas + 1):
                print("Tarefa: ",j , "tp_setup: ", tp_setup[j], " Data de entrega:", inst.data_entrega[j], " Dif", inst.data_entrega[j] - tp_setup[j])



            #transforma em um dicionario
            tp_setup_dic = {}
            for j in range(0, inst.n_tarefas + 1):
                tp_setup_dic[j] = inst.data_entrega[j] - tp_setup[j]
            
            tp_setup_ordenado = {}
            for i in sorted(tp_setup_dic, key = tp_setup_dic.get):
                 tp_setup_ordenado[i] = tp_setup_dic[i]

            print("\ntp_setup_dic - Ordenado pelo inst.data_entrega[j] - tp_setup[j]")
            print(tp_setup_ordenado)


            for j in tp_setup_ordenado.keys():
                tp_setup_ordenado[j] = tp_setup[j]
            for j in tp_setup_dic.keys():
                tp_setup_dic[j] = tp_setup[j]

            print("\ntp_setup_dic - Ordenado pelo menor tp + setup")
            print(tp_setup_ordenado)
            #cria o sequenciamento
            sequenciamento = []
            for i in range(inst.n_maquinas):
                linha = [] # lista vazia
                sequenciamento.append(linha)

            #forma 1 - adiciona todas as tarefas nas máquinas pela, as tarefas sao adicionadas 1 em cada máquina.
#            tp_setup_ordenado_aux = tp_setup_ordenado
#            tp_setup_ordenado_aux.pop(0,None)
#            completionTime = np.zeros(inst.n_tarefas + 1) 
#            while(len(tp_setup_ordenado_aux) > 0):
#                for i in range(inst.n_maquinas):
#                    tp_setup_ordenado = tp_setup_ordenado_aux 
#                    for j in tp_setup_ordenado.keys():
#                        tarefa = int(j)
#                        if(len(sequenciamento[i]) == 0):
#                            sequenciamento[i].append(tarefa)
#                            completionTime[tarefa] = tp_setup_ordenado[tarefa]
#                            tp_setup_ordenado_aux.pop(tarefa, None)
#                            break;
#                        else:
#                            completionTime[tarefa] = tp_setup_ordenado[tarefa] + completionTime[sequenciamento[i][len(sequenciamento[i])-1]]   
#                            sequenciamento[i].append(tarefa)
#                            tp_setup_ordenado_aux.pop(tarefa, None)
#                            break;



            #forma 2 - insere a tarefa na máquina que da o menor CompletionTime
            tp_setup_ordenado_aux = tp_setup_ordenado
            tp_setup_ordenado_aux.pop(0,None)
            completionTime = np.zeros(inst.n_tarefas + 1) 
            while(len(tp_setup_ordenado_aux) > 0):  
                tp_setup_ordenado = tp_setup_ordenado_aux 
                for j in tp_setup_ordenado.keys():
                    tarefa = int(j)
                    melhormaquina = -1
                    menorct = 10000
                    for i in range(inst.n_maquinas):
                        if(len(sequenciamento[i]) == 0):
                            ct = tp_setup_ordenado[tarefa]
                        else:
                            ct = tp_setup_ordenado[tarefa] + completionTime[sequenciamento[i][len(sequenciamento[i])-1]]   
                        if(ct < menorct):
                            menorct = ct
                            melhormaquina = i

                    if(len(sequenciamento[melhormaquina]) == 0):
                        sequenciamento[melhormaquina].append(tarefa)
                        completionTime[tarefa] = tp_setup_ordenado[tarefa]
                        tp_setup_ordenado_aux.pop(tarefa, None)
                        break;
                    else:
                        completionTime[tarefa] = tp_setup_ordenado[tarefa] + completionTime[sequenciamento[melhormaquina][len(sequenciamento[melhormaquina])-1]]   
                        sequenciamento[melhormaquina].append(tarefa)
                        tp_setup_ordenado_aux.pop(tarefa, None)
                        break;
            
            
            print("TP SETUP")
            print(tp_setup)
            print("completion time das tarefas")
            print(completionTime)

            #melhor LB é utilizando o completion time igual ao tp_setup
            #teste sem utilizar o completion Time das tarefas. inserindo ela nas rotas com o menor tp+setup
            completionTime = tp_setup
            #print("completion time das tarefas")
            #print(completionTime)


             #transforma em um dicionario
            completionTime_dic = {}
            for j in range(0, inst.n_tarefas + 1):
                completionTime_dic[j] = completionTime[j]
            
            completionTime_dic_ordenado = {}
            for i in sorted(completionTime_dic, key = completionTime_dic.get):
                 completionTime_dic_ordenado[i] = completionTime_dic[i]
    
            print("completion time das tarefas Ordenados")
            print(completionTime_dic_ordenado)

            #Passo 2    
            
            #calcula a maior distancia média
            
            maior_distancia_media  = 0;
            for j in range(0, inst.n_tarefas + 1):
                maior_distancia = 0
                for k in range(0, inst.n_tarefas + 1):
                    if(maior_distancia < inst.tempo_viagem[j][k]):        
                        maior_distancia = inst.tempo_viagem[j][k]
                maior_distancia_media += maior_distancia
            print("maior_distancia_soma", maior_distancia_media)
            #divide a maior_distancia_media  pelo a quantidade de veiculos
            maior_distancia_media = maior_distancia_media / inst.n_veiculos
            print("maior_distancia_media: ", maior_distancia_media)
            maior_completion_time = max(completionTime)
            print("maior_completion_time", maior_completion_time )
            UBE = maior_completion_time + maior_distancia_media
            print("UBE - ", UBE)
          

            #passo 3 - menor distancia entre os clientes
            menor_distancia = []
            menor_distancia.append(0)
            for j in range(1, inst.n_tarefas + 1):
                md = 10000
                for k in range(1, inst.n_tarefas + 1):
                    if(k == j):
                        continue
                    if(md> inst.tempo_viagem[j][k]):
                        md= inst.tempo_viagem[j][k]
                menor_distancia.append(md)

            print("\n Menores distancias")
            print(menor_distancia)

            
            #passo 4 
            ECT = []
            ECT = np.zeros((inst.n_tarefas + 1, (int(UBE) + 1)))
         
            for j in range(1, inst.n_tarefas + 1):
                for t in range(0, int(UBE) + 1):
                    ECT[j][t] = inst.penalidade_atraso[j] * max(0, t - inst.data_entrega[j])
            
            #for j in range(1, inst.n_tarefas + 1):
            #    for t in range(0, int(UBE) + 1):
            #        print("%d - " % ECT[j][t], end = "")
            #    print("\n\n")

            #passo 5
            maior_capacidade = max(inst.capacidade_veiculo)
            print("Maior capacidade: ",maior_capacidade)
            capacidade_media = sum(inst.capacidade_veiculo) / inst.n_veiculos 
            print("Média capacidade: ",capacidade_media)
            capaciadeLimite = capacidade_media + (maior_capacidade -capacidade_media)
            print("Capacidade Limite: ",capaciadeLimite)
            
            capacidade_utilizada  = np.zeros(inst.n_veiculos)


            rotas = []
            for i in range(inst.n_veiculos):
                linha = [] # lista vazia
                rotas.append(linha)

            dataPartida = np.zeros(inst.n_veiculos)
            
            tarefasAlocadas = [];

            #pare cada tarefa, qual o menor t.
            #print("ETC (data de entrega) a partir de 1 para cada job")
            #for j in range(1, inst.n_tarefas + 1):
            #    for t in range(0, int(UBE) + 1):
            #        if(ECT[j][t] != 0):
            #            print("Job ", j, " - Time ", t)
            #            break;
            

            dataPartida = np.zeros(inst.n_veiculos)
            ECT_Utilizados = np.zeros(inst.n_veiculos)
            ECT_Ut = 0;
            del completionTime_dic_ordenado[0]
            ct_dic = completionTime_dic_ordenado
            
            veiculo = 0;
            #forma 1: tenta adicionar as tarefas nas rotas sem ter atraso
            while(veiculo < inst.n_veiculos):
                if(len(completionTime_dic_ordenado) == 0):
                    break;
                ct_dic = completionTime_dic_ordenado
                for j in ct_dic.keys():
                    tarefa = int(j)
                    #adiciona a tarefa no veiculo, caso o veiculo esteja vazio
                    if(len(rotas[veiculo]) == 0 and ((capacidade_utilizada[veiculo] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or (capacidade_utilizada[veiculo] - inst.tamanho_tarefa[tarefa] < (maior_capacidade -capacidade_media)))):
                        rotas[veiculo].append(tarefa) #adiciona a tarefe na rota
                        tarefasAlocadas.append(tarefa) #adiciona a tarefa no vetor de tarefas alocadas 
                        capacidade_utilizada[veiculo] += inst.tamanho_tarefa[tarefa]
                        dataPartida[veiculo] = ct_dic[tarefa]
                        completionTime_dic_ordenado.pop(tarefa, None)
                        break;
                    #é possivel adicionar a tarefa no veiculo sem atraso ?
                    elif ((capacidade_utilizada[veiculo] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or ((capacidade_utilizada[veiculo] - inst.tamanho_tarefa[tarefa]) < (maior_capacidade -capacidade_media))):
                        nova_data_partida = max (int(dataPartida[veiculo]), int(ct_dic[tarefa]))
                        w = len(rotas[veiculo])
                        for p in range(0, w):
                            nova_data_partida += menor_distancia[rotas[veiculo][p]]    

                        if(nova_data_partida + menor_distancia[tarefa] < inst.data_entrega[tarefa]):
                            rotas[veiculo].append(tarefa) #adiciona a tarefe na rota
                            tarefasAlocadas.append(tarefa) #adiciona a tarefa no vetor de tarefas alocadas 
                            capacidade_utilizada[veiculo] += inst.tamanho_tarefa[tarefa]    
                            dataPartida[veiculo] =  max(dataPartida[veiculo] , ct_dic[tarefa])
                            completionTime_dic_ordenado.pop(tarefa, None)
                            break;
                        else:
                            #tarefa com atraso, abre um novo veiculo.
                            veiculo += 1
                            break;
                     #limite excedido do veiculo.
                    else:
                        veiculo += 1
                        break;

            # Ainda falta tarefas a serem adicionadas nas rotas.
            if(len(tarefasAlocadas) != inst.n_tarefas):
            #para cada tarefa ainda nao alocada, verificar em qual veiculo e em qual posição inserir a tarefa tem o 
            #menor atraso total ponderado, 
                for j in ct_dic.keys():
                    tarefa = int(j)
                    #tempo = ct_dic[tarefa] + menor_distancia[tarefa]
                    #print("Tarefa", tarefa , "Tempo",  tempo)
                    a = DefineAMelhorMaquinaParaInserir(inst, rotas, tarefa, ct_dic[tarefa], dataPartida, menor_distancia, capacidade_utilizada, capacidade_media, maior_capacidade )
                    if(a == True):
                        tarefasAlocadas.append(tarefa)



            wt_final = calcula_wt_solucao(inst, rotas, dataPartida, menor_distancia)

            print("Instanicia: ",inst.nome)
         

          
            print("Tarefas Alocas em Rotas: ", len(tarefasAlocadas))
            print("Rotas")
            print(rotas)
            print("\nTamanho utilizado nos veiculos:")
            print(capacidade_utilizada)
            
            pause = False
            if(pause):
                ans = input()
                print("-"*300)
                print("\n"*10)

            if(len(tarefasAlocadas) != inst.n_tarefas):
                cont_Instancias_q_n_conseguiu_Alocar_todos += 1
                print("ERRO, NEM TODAS TAREFAS FORAM ALOCAS NESTA INSTANCIA")
                instancia_lb[inst.nome] = -1
            else:
                instancia_lb[inst.nome] = math.ceil(wt_final) #arredonda para cima
            


            #exit()
        print("Instancias que nao conseguiram alocar todas as tarfas nos veiculos:", cont_Instancias_q_n_conseguiu_Alocar_todos)

        print(instancia_lb)

           

            #exit()
        print("Instancias que nao conseguiram alocar todas as tarfas nos veiculos:", cont_Instancias_q_n_conseguiu_Alocar_todos)

        print(instancia_lb)



def calcula_wt_solucao(inst, rotas, dataPartida, menor_distancia):
    data_entrega = np.zeros(inst.n_tarefas + 1)
    for i in range(0, inst.n_veiculos):
        for j in range (0, len(rotas[i])):
            tarefa = rotas[i][j]
            if(j == 0):
                data_entrega[tarefa] = dataPartida[i] + menor_distancia[tarefa]
            else:
                data_entrega[tarefa] = data_entrega[rotas[i][j-1]] + menor_distancia[tarefa]
    wt = 0
    for j in range (0, inst.n_tarefas + 1):
        #tarefa com atraso
        if ( data_entrega[j] > inst.data_entrega[j] ):
            wt += (data_entrega[j] - inst.data_entrega[j]) * inst.penalidade_atraso[j] 
         
    #print("WT: ", wt)
    return wt

def DefineAMelhorMaquinaParaInserir(inst, rotas, tarefa, ct_tarefa, dataPartida, menor_distancia, capacidade_utilizada, capacidade_media, maior_capacidade ):
    # a ideia dessa função é inserir a tarefa na rota e na posição que minimiza o wt da solucao
    # neste caso, vamos testar todas as posiçoes possiveis 
    #depois inserir a tarefa na posicao com menor wt geral.
    menor_wt = 15000000000
    melhor_veiculo = -1
    melhor_posicao = -1
    for v in range(0, inst.n_veiculos):
        #Verifica se a tarefa cabe no veiculo.
        if ((capacidade_utilizada[v] + inst.tamanho_tarefa[tarefa] <= capacidade_media) or ((capacidade_utilizada[v] - inst.tamanho_tarefa[tarefa]) < (maior_capacidade - capacidade_media))):
            for t in range(0,len(rotas[v])+1):
           
                #insere a tarefa na posicao t do veiculo v
                rotas[v].insert(t, tarefa)
                #atualiza a data de partida do veiculo 
                dataPartidaOriginal = dataPartida[v]
                dataPartida[v] = max(dataPartida[v], ct_tarefa)
                wt_solucao = calcula_wt_solucao(inst, rotas, dataPartida, menor_distancia)
                if(menor_wt > wt_solucao):
                    menor_wt = wt_solucao
                    melhor_veiculo = v
                    melhor_posicao = t
                #remove a tarefa da rota para inseir em outra posicão
                del(rotas[v][t])
                dataPartida[v] = dataPartidaOriginal

    if(melhor_veiculo != -1 ):
        rotas[melhor_veiculo].insert(melhor_posicao, tarefa)
        capacidade_utilizada[melhor_veiculo] += inst.tamanho_tarefa[tarefa]
        dataPartida[melhor_veiculo] = max(dataPartida[melhor_veiculo], ct_tarefa)
        #print("Menor wt: ", menor_wt)
        return True
    else:
        return False
def retornaTarefasComECT_zero(ECT, rc_dic_ordenado, dt_partida):
    tarefas_com_ECT_zero = []
    for j in rc_dic_ordenado.keys():
        tarefa = int(j)
        if(ECT[int(j)][int(dt_partida)] <= 0):
            tarefas_com_ECT_zero.append(tarefa)
    return tarefas_com_ECT_zero
