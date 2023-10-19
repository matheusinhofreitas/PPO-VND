import numpy as np


INSTANCIA_UNICA = False
SEMENTE_INSTANCIA_UNICA = 51
#PASSOS_TREINAMENTO = 100 #Não está sendo utilizado, pega as informações dos parametros da gym
USAR_LOG_TENSORBOARD = True # Para ver o log, execute o comando: tensorboard --logdir ./ppo_tensorboard/
#TOTAL_INSTANCIAS = 180#36
#TOTAL_INSTANCIAS = 12
TOTAL_INSTANCIAS = 3

CARREGAR_MODELO = False
CONTINUAR_TREINAMENTO = False
#NOME_MODELO = "MODELO_36_inst_UB=FO_inicial"
#NOME_MODELO = "MODELO_36_inst_1M"
#NOME_MODELO = "MODELO_Treinamento_1kk_36_instancias"

NOME_MODELO = "MODELO_Calibracao_n_100_n-trials_10"

TAMANHO = None;
#ROCAS = int(np.round(0.3*TAMANHO))

if not INSTANCIA_UNICA:
   SEMENTE_INSTANCIA_UNICA = None
