import os
import numpy as np
import gym
from gym import spaces
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3 import PPO

from gym_customizedEnv.envs.Heuristicas.solver import *
from gym_customizedEnv.envs.Heuristicas.Executa_estrategias import *
from gym_customizedEnv.envs.Heuristicas.read import *
from gym_customizedEnv.envs.Heuristicas.calculaLB import *
from gym_customizedEnv.envs.Heuristicas.VND import *

#import gym_customizedEnv.envs.variaveis as var

class CustomizedEnv(gym.Env):
  """
  Custom Environment that follows gym interface.
  This is a simple env where the agent must learn to go always left. 
  """ 
 
  def __init__(self, instancia_unica=False, seed=None, pasta=None, Tipo_Recompensa = 0):
    #try:
    super(CustomizedEnv, self).__init__()
    self.Tipo_Recompensa = Tipo_Recompensa
    self.pasta_instancias = pasta
    
    if(self.pasta_instancias == 100):
      pasta = 10
    if(self.pasta_instancias == 150):
      pasta = 15
    if(self.pasta_instancias == 300):
      pasta = 30
    if(self.pasta_instancias == 500):
      pasta = 50

    self.TAMANHO = int(pasta)
    self.TROCAS = int(np.round(0.3*self.TAMANHO))
    
    
    #print(f"Criando ambiente: {instancia_unica=} {seed=}" )  
    
    self.max_iter_sem_melhoras = self.TAMANHO
    tam = (self.TAMANHO)*3 + 2
    #tam = TAMANHO
    self.Dmax = 10*tam #TODO: Ver o que vai alterar aqui
    self.FOmax = tam*self.Dmax #TODO: Ver o que vai alterar aqui
    
    
    # Define action and observation space
    self.action_space = spaces.Discrete(CustomizedEnv.NUMERO_ACOES)
    self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(tam,), dtype=np.float64)

    self.seed(seed)
    self.instancia_unica = instancia_unica
    
    if not self.instancia_unica: 
      self.criar_instancia(self.instancia_selecionada)
      self.instancia_selecionada += 1

    self.iter_sem_melhoras = 0
    self.passo = 0
    self.ultima_acao = None
    self.ultima_recompensa = None    
    #except:
    #  print("FUNÇÂO __init__") 
      #exit()
    
  #TODO: Adicionar as vizinhanças do problema aqui.
  # Constantes paras as ações possíveis
  ACAO_SWAP_D_linha = 0 #sem restart
  ACAO_SWAP_D_linha_R1 = 1 #com restart
  ACAO_INSERT_D_linha = 2 #sem restart
  ACAO_INSERT_D_linha_R1 = 3 #com restart

  ACAO_SWAP_P_linha = 4 #sem restart
  ACAO_SWAP_P_linha_R1 = 5 #com restart
  ACAO_INSERT_P_linha = 6 #sem restart
  ACAO_INSERT_P_linha_R1 = 7 #com restart
  
  NUMERO_ACOES = 8
  
  instancia = None
  solucao = None
  instancia_selecionada = 0
  #função que calcula a FO do problema e retorna o Valor da FO  
  def Avalia(self, solucao):
    #try:
    FO = 0
    solucao.calcula_funcaoObjetivo(self.instancia)
    FO = solucao.FO
    return FO
    #except:
    #  print("FUNÇÂO AVALIA") 
    #  exit()

  #Chamar a função construtiva do problema e retorna a solucao construtiva.
  def Construtiva (self):
    #try:
    vnd = VND(self.instancia)
    solucao = vnd.retornaSolucaoInicial()    
    
    return solucao
    #except:
     # print("FUNÇÂO Contrutiva") 
      #exit()



  #Vizinhanças do problema, retornando a melhor solucão encontrada
  def Solver (self, solucao, Escolha):
    #try:
    vnd = VND(self.instancia)   
    new_solucao = Solucao( self.instancia.n_tarefas, self.instancia.n_maquinas, self.instancia.n_veiculos)
    
    if Escolha == CustomizedEnv.ACAO_SWAP_D_linha:
      new_solucao = vnd.Swap (solucao.ordemInsercaoRotas,solucao,0,0,self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_SWAP_D_linha_R1:
      new_solucao = vnd.Swap (solucao.ordemInsercaoRotas,solucao,1,0, self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_INSERT_D_linha:
      new_solucao = vnd.Insertion (solucao.ordemInsercaoRotas,solucao,0,0, self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_INSERT_D_linha_R1:
      new_solucao = vnd.Insertion (solucao.ordemInsercaoRotas,solucao,1,0, self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_SWAP_P_linha:
      new_solucao = vnd.Swap (solucao.ordemInsercaoMaquinas,solucao,0,1,self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_SWAP_P_linha_R1:
      new_solucao = vnd.Swap (solucao.ordemInsercaoMaquinas,solucao,1,1,self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_INSERT_P_linha:
      new_solucao = vnd.Insertion (solucao.ordemInsercaoMaquinas,solucao,0,1,self.TROCAS)

    if Escolha == CustomizedEnv.ACAO_INSERT_P_linha_R1:
      new_solucao = vnd.Insertion (solucao.ordemInsercaoMaquinas,solucao,1,1,self.TROCAS)   
    
    lista = self.GeraListaD(new_solucao)
    #new_solucao.calcula_funcaoObjetivo(self.instancia)
    return lista, new_solucao.FO, new_solucao
    #GAP = round(100*((UB-LB)/UB))
    #except:
    #  print("FUNÇÂO SOLVER") 
      #exit()
    
  #lêr uma nova instancia do problema
  #TODO: Ler apenas 1 instancia por vez.
  def criar_instancia(self, instancia_selecionada):
    #try:
    #path = "./Instancias/Testes"#_3"
    #print("****Caminho****")
    #print(os.path.join(os.path.dirname(__file__)))
    #path = os.path.join(os.path.dirname(__file__)) + "/../../Instancias/N_10"#_3"
    #path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_10"#_3"
    if(self.pasta_instancias == 10):
      #path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_10"#_3"
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/treinamento_n_10"#_3"
    if(self.pasta_instancias == 15):
      #path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_15"#_3"
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/treinamento_n_15"#_3"
    if(self.pasta_instancias == 30):
      #path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_30"#_3"
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/treinamento_n_30"#_3"
    if(self.pasta_instancias == 50):
      #path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_50"#_3"
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/treinamento_n_50"#_3"
    
    if(self.pasta_instancias == 100):
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_10"#_3"
    if(self.pasta_instancias == 150):
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_15"#_3"
    if(self.pasta_instancias == 300):
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_30"#_3"
    if(self.pasta_instancias == 500):
      path = os.path.join(os.path.dirname(__file__)) + "/Instancias/Calibracao_n_50"#_3"
    #print("****Caminho Final****")
    #print(path)
    files = listar_arquivos(path)
    files.sort()
    self.TOTAL_INSTANCIAS = len(files)
    instancia_selecionada = int(instancia_selecionada % self.TOTAL_INSTANCIAS)
    local = path +"/"+ files[instancia_selecionada]
    #print(files[instancia_selecionada])     
    #carrega a instancia para memoria
    self.instancia = Instancia(local)
    #print("Instancia;"+files[instancia_selecionada]+";LB; "+ str(self.instancia.LB) + ";UB; "+ str(self.instancia.UB))
    #print("LB; "+ str(self.instancia.LB))
    #print("UB: "+ str(self.instancia.UB))
    #except:
    #  print("FUNÇÂO CRIA INSTANCIA") 
      #exit()
    

  #cria a solucao inicial + a Lista que tem a mesma composição da listaD
  #CompletionTime das tarefas + Data de entrega das tarefas + Atraso ponderado das tarefas  
  def usar_instancia(self):
    #try:
    self.LB = self.instancia.LB
    solucao = self.Construtiva()
    #print(solucao.FO)
    self.FO_inicial = solucao.FO
    atraso_ponderado = [0]*(self.instancia.n_tarefas+1)
    for i in range(0, self.instancia.n_tarefas+1):
        atraso_ponderado[i] = int(solucao.atrasoTarefa[i] * self.instancia.penalidade_atraso[i]) 

    n = self.instancia.n_tarefas + 1
    self.Lista = [0]*n*3
    for i in range(0,n):
      self.Lista[i] = int(solucao.completionTime[i])
    j = 0
    for i in range(n,2*n):
      self.Lista[i] = int(solucao.dataEntrega[j])
      j+=1

    j = 0
    for i in range(2*n,len(self.Lista)):
      self.Lista[i] = int(atraso_ponderado[j])
      j+=1
    
    self.FO = solucao.FO
    self.FO_Best = solucao.FO#self.FO_Best_inicial
    return solucao
    #except:
    #  print("FUNÇÂO USAR INSTANCIA") 
      #exit()

  #Funcao que gera a listaD, a listaD é composta pelos CompletionTime das tarefas + Data de entrega das tarefas + Atraso ponderado das tarefas
  def GeraListaD(self, solucao):
    #try:
    n = self.instancia.n_tarefas
    listaD = [0]*n*3 + [0] + [0]
    
    listaD[0] = self.instancia.n_maquinas
    listaD[1] = self.instancia.n_tarefas
    
    j = 1
    for i in range(2,n+2):
      listaD[i] = int(solucao.completionTime[j])
      j+=1
    j = 1
    for i in range(n+2,2*n + 2 ):
      listaD[i] = int(solucao.dataEntrega[j])
      j+=1

    j = 1
    for i in range(2*n + 2,len(listaD)):
      listaD[i] = int(solucao.atrasoTarefa[j] * self.instancia.penalidade_atraso[j])
      j+=1
    

    return listaD
    #except:
     # print("FUNÇÂO GERALISTAD") 
      #exit()

  
  
  def reset(self):
    #try:
    """
    Important: the observation must be a numpy array
    :return: (np.array) 
    """
    
    if not self.instancia_unica: 
      self.criar_instancia(self.instancia_selecionada)
      self.instancia_selecionada += 1
    else:
      self.criar_instancia(self.instancia_selecionada)  
    self.solucao = self.usar_instancia()
    
    #self.instancia.UB = self.solucao.FO    
    #print("Instancia;"+self.instancia.nome+";LB; "+ str(self.instancia.LB) + ";UB; "+ str(self.instancia.UB))

    self.iter_sem_melhoras = 0
    self.DeltaBest = 0 #distancia da melhor solucão   
    self.passo = 0
    self.ultima_acao = None
    self.ultima_recompensa = None

    self.ListaD = self.GeraListaD(self.solucao)
    self.somaFO = self.FO_Best
    #return self.normalizar_estado([self.FO,self.FO_Best,self.DeltaBest,self.iter_sem_melhoras]+self.ListaD)
    #return self.normalizar_estado([self.iter_sem_melhoras]+self.ListaD)
    return self.normalizar_estado(self.ListaD)
    #except:
    #  print("FUNÇÂO RESET") 
      #exit()
    

    #TODO:Conversar com o Thiago para ver a questão de normalização de estados.
  def normalizar_estado(self, estado):
    #try:
    # Precisamos pegar cada campo do estado e reescalonar seus valores mínimos e máximos para o intervalo [-1,1]
    estado_temp = estado.copy()
    #n de iteraçoes sem melhora
    #numero de máquinas
    estado_temp[0] =  (estado_temp[0] - 2) / (8 - 2)
    estado_temp[1] =  (estado_temp[1] - 10) / (50 - 10)

    n = self.instancia.n_tarefas
    #completionTime
    j = 1
    for i in range(2,n+2):
      estado_temp[i] = (estado_temp[i] - self.instancia.menor_completion_time[j])/ (self.instancia.maior_completion_time[j] - self.instancia.menor_completion_time[j])
      j+=1
    
    #dataEntrega
    j = 1
    for i in range(n+2,(2*n)+2):
      estado_temp[i] = (estado_temp[i] - self.instancia.menor_data_entrega[j] )/(self.instancia.maior_data_entrega[j] - self.instancia.menor_data_entrega[j])
      j+=1


    #atrasoTarefa
    j = 1
    for i in range((2*n)+2,len(estado_temp)):
      estado_temp[i] = (estado_temp[i] - self.instancia.menor_atraso_ponderado[j] ) / (self.instancia.maior_atraso_ponderado[j] - self.instancia.menor_atraso_ponderado[j])
      j+=1
    

    return np.clip(np.array(estado_temp)*2 - 1, self.observation_space.low, self.observation_space.high) 
    #except:
    #  print("FUNÇÂO normalizar_estado") 
      #exit() 

  #Recompens utilizando o UB e LB para Calcular
  def recompensa_0(self):
    return float(-1* (self.FO - self.instancia.LB)/(self.instancia.UB - self.instancia.LB)*100 )

  #Recompensa 1 define uma recompensa no seguinte esquema 
  #Se a FO for melhor que a solucao_best a recompensa é multiplicada em 100x
  #Se a FO foi melhor que a solução anterior a recompensa é multiplicada em 10x
  #Se a FO for PIOR que a solução anterior a recompensa é multiplicada em -10x
  def recompensa_1(self):
    recompensa = float(self.FO_anterior - self.FO)
    if(self.FO_Best > self.FO):
      recompensa = 100*recompensa
    elif (self.FO_anterior > self.FO):
      recompensa = 10*recompensa
    elif (self.FO_anterior >= self.FO):
      recompensa = recompensa
    else:
      recompensa = -10*recompensa

    return recompensa
  #Recompensa 2 define uma recompensa no seguinte esquema 
  #Se a FO for melhor que a solucao_best a recompensa é 100
  #Se a FO foi melhor que a solução anterior a recompensa é 10
  #Se a FO for PIOR que a solução anterior a recompensa é -10
  def recompensa_2(self):
    recompensa = float(self.FO_anterior - self.FO)
    if(self.FO_Best > self.FO):
      recompensa = 100
    elif (self.FO_anterior > self.FO):
      recompensa = 10
    elif (self.FO_anterior >= self.FO):
      recompensa = recompensa
    else:
      recompensa = -10
    return recompensa

  #Recompensa 3 - igual ao do artigo, utiliza a diferença entre a FO e a média do FO dos passos anteriores
  def recompensa_3(self):
    media  = self.somaFO / (self.passo + 1)
    recompensa = (self.FO - media) / 100
    
    return recompensa

  def step(self, action):
    #try:
    self.FO_anterior = self.FO
    self.Lista, self.FO, self.solucao = self.Solver(copy.deepcopy(self.solucao), action)
    #print("self.Lista :", self.Lista)
    self.ultima_acao = action
    self.ListaD = self.GeraListaD(self.solucao) #TODO: Tirar pois a listaD é igual a self.Lista 1
    
    if (self.Tipo_Recompensa == 0):
      recompensa = self.recompensa_0()
      #print("Instancia; "+str(self.instancia.nome)+";Passo;"+str(self.passo)+"; Acao;"+str(action)+"; Recompensa;" + str(recompensa)+"; FO;"+str(self.FO) + ";LB;"+str(self.instancia.LB) +";UB;"+str(self.instancia.UB) + "; Tipo_Recompensa;" + str(self.Tipo_Recompensa))
    elif(self.Tipo_Recompensa == 1):
      recompensa = self.recompensa_1()
      #print("Instancia; "+str(self.instancia.nome)+";Passo;"+str(self.passo)+"; Acao;"+str(action)+"; Recompensa;" + str(recompensa)+"; FO;"+str(self.FO) + ";FO_Anterior;"+str(self.FO_anterior) +";FO_BEST;"+str(self.FO_Best)+ "; Tipo_Recompensa;" + str(self.Tipo_Recompensa))
    elif(self.Tipo_Recompensa == 2):
      recompensa = self.recompensa_2()
      #print("Instancia; "+str(self.instancia.nome)+";Passo;"+str(self.passo)+"; Acao;"+str(action)+"; Recompensa;" + str(recompensa)+"; FO;"+str(self.FO) + ";FO_Anterior;"+str(self.FO_anterior) +";FO_BEST;"+str(self.FO_Best)+ "; Tipo_Recompensa;" + str(self.Tipo_Recompensa))
    elif (self.Tipo_Recompensa == 3):
      recompensa = self.recompensa_3()
      #print("Instancia; "+str(self.instancia.nome)+";Passo;"+str(self.passo)+" Acao;"+str(action)+"; Recompensa;" + str(recompensa)+"; FO;"+str(self.FO) + ";FO_Soma"+str(self.somaFO) +";FO_media;"+str((self.somaFO/self.passo+1))+ "; Tipo_Recompensa;" + str(self.Tipo_Recompensa))
      self.somaFO += self.FO

    #print("STEP->"+ "Pass;"+str(self.passo)+" Acao;"+str(action)+"; Recompensa;" + str(recompensa)+"; FO;"+str(self.FO) + "LB;"+str(self.instancia.LB) +";UB;"+str(self.instancia.UB))
    #print(recompensa)

    self.ultima_recompensa = recompensa
    #recompensa = float(self.FO_Best - self.FO)

    if self.FO_Best > self.FO:
      self.FO_Best = self.FO

    self.iter_sem_melhoras += 1
      #self.DeltaBest = self.FO - self.FO_Best

    # if sum(self.ListaD) != self.FO:
    #   print(sum(self.ListaD))
    #   print(self.Lista)
    #   print(self.Avalia(self.Lista))
    #   print(self.FO)
    #   os.system("PAUSE")
    
    terminou_episodio = bool(self.FO == self.LB or self.iter_sem_melhoras == self.max_iter_sem_melhoras)

    # Optionally we can pass additional info, we are not using that for now
    info = {}

    self.passo += 1

    #return self.normalizar_estado([self.FO, self.FO_Best,self.DeltaBest, self.iter_sem_melhoras]+self.ListaD), recompensa, terminou_episodio, info
    #return self.normalizar_estado([self.iter_sem_melhoras]+self.ListaD), recompensa, terminou_episodio, info
    return self.normalizar_estado(self.ListaD), recompensa, terminou_episodio, info
    #except:
    #  print("FUNÇÂO Step") 
      #exit()


  def render(self, mode='console'):
    #try: 
    if mode != 'console':
      raise NotImplementedError()
    
    if (self.passo > 0): 
      print(f'Passo {self.passo}') 
    else: 
      print('Instância:')
    
    print(f'\tÚltima ação: {self.ultima_acao}, FO: {self.FO}, FO_Best: {self.FO_Best}, Ism: {self.iter_sem_melhoras}, DeltaBest: {self.DeltaBest}')
    print(f'\tLista: {self.Lista}')
    print(f'\tListaD: {self.ListaD}')
    print(f'\tRecompensa: {self.ultima_recompensa}')
    #except:
     # print("FUNÇÂO RENDER") 
      #exit()

  def close(self):
    #try:
    pass
    #except:
    #  print("FUNÇÂO CLOSE") 
      #exit()
  
  def seed(self, seed=None):
    #try:
    self.rand_generator = np.random.RandomState(seed)
    self.action_space.seed(seed)
    #except:
    #  print("FUNÇÂO SEED") 
      #exit()