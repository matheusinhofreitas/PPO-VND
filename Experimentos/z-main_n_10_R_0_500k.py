import numpy as np
import gym
from gym import spaces
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3 import PPO
from gym_customizedEnv.envs.customizedEnv import CustomizedEnv
from datetime import datetime




INSTANCIA_UNICA = False
SEMENTE_INSTANCIA_UNICA = 51
PASSOS_TREINAMENTO = 500000
USAR_LOG_TENSORBOARD = True # Para ver o log, execute o comando: tensorboard --logdir ./ppo_tensorboard/

#GRUPO_INSTANCIA = 10 15 30 ou 50 para pegar as pastas do treinamento
#GRUPO_INSTANCIA = 100 150 300 ou 500 para pegar as pastas da calibração
#  
GRUPO_INSTANCIA = 100 #10 15 30 50
TIPO_RECOMPENSA = 0 # 0 1 2 3

CARREGAR_MODELO = True
CONTINUAR_TREINAMENTO = False
#NOME_MODELO = "MODELO_36_inst_UB=FO_inicial"
#NOME_MODELO = "MODELO_36_inst_1M"
if(GRUPO_INSTANCIA == 100):
    NOME_MODELO = "TREINAMENTO_Defalt_passos_"+str(PASSOS_TREINAMENTO)+"_Recompensa_"+str(TIPO_RECOMPENSA)+"_inst_N_10"
else:
    NOME_MODELO = "TREINAMENTO_Defalt_passos_"+str(PASSOS_TREINAMENTO)+"_Recompensa_"+str(TIPO_RECOMPENSA)+"_inst_N_"+str(GRUPO_INSTANCIA)
#TAMANHO = 10
#TROCAS = int(np.round(0.3*TAMANHO))

if not INSTANCIA_UNICA:
   SEMENTE_INSTANCIA_UNICA = None

print("Inicio do Experimento")
print(datetime.now())

print("PASSOS TREINAMENTO")
print(PASSOS_TREINAMENTO)


#exit()

print("===== CHECANDO AMBIENTE =====")

env = CustomizedEnv(instancia_unica=INSTANCIA_UNICA, seed=SEMENTE_INSTANCIA_UNICA, pasta=GRUPO_INSTANCIA, Tipo_Recompensa=TIPO_RECOMPENSA)#gym.make('gym_customizedEnv:gym_customizedEnv-v0')
# If the environment don't follow the interface, an error will be thrown
check_env(env, warn=True)

print()
print("===== DEMONSTRANDO AMBIENTE =====")
env = CustomizedEnv(instancia_unica=INSTANCIA_UNICA, seed=SEMENTE_INSTANCIA_UNICA, pasta=GRUPO_INSTANCIA, Tipo_Recompensa=TIPO_RECOMPENSA)#gym.make('gym_customizedEnv:gym_customizedEnv-v0')

#print(f"{env.observation_space=}")
#print(f"{env.action_space=}")
#print(f"{env.action_space.sample()=}")

print()
print("===== TREINANDO COM POO =====")

if INSTANCIA_UNICA:
   n_envs = 1
else:
   n_envs = 4
   
# Cria um ambiente vetorizado considerando 4 ambientes (atores do PPO)
vec_env = make_vec_env('gym_customizedEnv:gym_customizedEnv-v0', n_envs=n_envs, env_kwargs={'instancia_unica': INSTANCIA_UNICA, 'seed': SEMENTE_INSTANCIA_UNICA, 'pasta':GRUPO_INSTANCIA, 'Tipo_Recompensa':TIPO_RECOMPENSA})

# Usa um adaptador para normalizar as recompensas
vec_env = VecNormalize(vec_env, training=True, norm_obs=False, norm_reward=True, clip_reward=10.)

if USAR_LOG_TENSORBOARD:
  tensorboard_log="./ppo_tensorboard_Artigo/"
else:
  tensorboard_log=None

# Train the agent
vec_env.instancia_selecionada = 0
if(CARREGAR_MODELO == False):
   model = PPO('MlpPolicy', vec_env, verbose=1, tensorboard_log=tensorboard_log).learn(PASSOS_TREINAMENTO)

   model.save("MODELO_"+str(NOME_MODELO))
else:
  model = PPO.load("MODELO_"+str(NOME_MODELO),env)
  # Crie uma instância de PPOPolicy para continuar o treinamento
  #model.set_env(env)
  # Continue o treinamento do modelo
  if(CONTINUAR_TREINAMENTO == True):
    model.learn(total_timesteps=PASSOS_TREINAMENTO, reset_num_timesteps=False)
    model.save("PPO_TESTE")
print()
print("===== DEMONSTRANDO RESULTADO =====")

class RandomAgent():
  def __init__(self, env):
    self.env = env

  def predict(self, observation, deterministic=False):
    # ignora o parâmetro deterministic
    return self.env.action_space.sample(), None

def evaluate_results(model, env, seeds, render=False):
  results = []
  FO_bests = []
  
  #for seed in seeds:
  for instancia in range(0,env.TOTAL_INSTANCIAS):
    env.seed(seeds[0])
    env.instancia_selecionada = instancia
    obs = env.reset()
   
    if render: env.render()
    done = False
    while not done:
      action, _ = model.predict(obs, deterministic=True)
      obs, reward, done, info = env.step(action)
      if render: env.render()
    
    results.append({'Instancia':env.instancia.nome, 'FO_Best': env.FO_Best, 'FO_inicial': env.FO_inicial, 'LB': env.LB})  
    FO_bests.append(env.FO_Best)
  
  return np.average(FO_bests), results


def evaluate_neighborhood( env, seeds, render=False):
  results = []
  FO_bests = []
  #for action in range(0,8):
  #for seed in seeds: 
  for instancia in range(0,env.TOTAL_INSTANCIAS):
   env.seed(seeds[0])
   env.instancia_selecionada = instancia
   obs = env.reset()
   if render: env.render()
   done = False
   while not done:
     action = random.randint(0, 7)
     print(action)
     obs, reward, done, info = env.step(action)
     if render: env.render()
    
   results.append({'Instancia':env.instancia.nome, 'FO_Best': env.FO_Best, 'FO_inicial': env.FO_inicial, 'LB': env.LB})  
   FO_bests.append(env.FO_Best)
  
  return FO_bests, results
# Test the trained agent

SEMENTES_FIXAS_AVALIACAO = [190, 312,   4, 207, 461, 394, 859, 639, 138, 727]

if INSTANCIA_UNICA:  
  qtde_avaliacoes = 1
else:
  qtde_avaliacoes = 10

SEMENTES_AVALIACAO = SEMENTES_FIXAS_AVALIACAO[:qtde_avaliacoes]
for i in range(5):
  print("Executando PPO - Exec ", str(i))
  PPO_avg_FO_bests, PPO_results = evaluate_results(model, env, SEMENTES_AVALIACAO, render=False)
#salva Resultados PPO
  myfile = open("180_"+str(NOME_MODELO)+"_resultados_PPO_"+str(i)+"+.txt", "w")
  myfile.write(str(PPO_avg_FO_bests) +"\n")
  myfile.write("-------------------------"+"\n")
  myfile.write(str(PPO_results) +"\n")
  myfile.close()

for i in range(5):
  print("Executando PPO 2 - Random - Exec_",str(i))
  random_avg_FO_bests, random_results = evaluate_results(RandomAgent(env), env, SEMENTES_AVALIACAO, render=False)
  myfile = open("180_"+str(NOME_MODELO)+"_resultados_PPO_Random_"+str(i)+".txt", "w")
  myfile.write(str(random_avg_FO_bests) +"\n")
  myfile.write("-------------------------"+"\n")
  myfile.write(str(random_results) +"\n")
  myfile.close()


#print("Executando Neighborhood")
#neighborhood_avg_FO_Best, neighborhood_results = evaluate_neighborhood( env, SEMENTES_AVALIACAO, render=False)

#Salva os resultados em um arquivo

#Salva Resultados RVND
#myfile = open("resultados_neighborhood.txt", "w")
#myfile.write(str(neighborhood_avg_FO_Best) +"\n")
#myfile.write("-------------------------"+"\n")
#myfile.write(str(neighborhood_results) +"\n")
#myfile.close()


#salva Resultados PPO Random




print(f"Done! Resultado: {env.FO_Best} (inicial: {env.FO_inicial}, LB: {env.LB})")

print()
print(f"{'Execução':^20}{'FO_Best PPO':^20}{'FO_Best Random':^20}{'FO_inicial PPO':^20}{'FO_inicial Random':^20}{'LB PPO':^20}{'LB Random':^20}")
for i in range(len(PPO_results)):
  print(f"{i+1:^20}", end="")
  print(f"{PPO_results[i]['FO_Best']:^20}", end="")
  print(f"{random_results[i]['FO_Best']:^20}", end="")
  print(f"{PPO_results[i]['FO_inicial']:^20}", end="")
  print(f"{random_results[i]['FO_inicial']:^20}", end="")
  print(f"{PPO_results[i]['LB']:^20}", end="")
  print(f"{random_results[i]['LB']:^20}")

print()

print(f"FO_Best médio do PPO: {PPO_avg_FO_bests}")
print(f"FO_Best médio do Random: {random_avg_FO_bests}")


print("Fim do Experimento")
print(datetime.now())
