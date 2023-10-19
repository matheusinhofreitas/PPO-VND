import time

from gym_customizedEnv.envs.Heuristicas.instancia import Instancia
from gym_customizedEnv.envs.Heuristicas.solucao import Solucao
from gym_customizedEnv.envs.Heuristicas.heuristicas import Heuristicas

class Solver:
    
    #construtor
    def __init__(self, path, nome_instancia):
        self.path= path
        local = path +"/"+nome_instancia
        self.instancia = Instancia(local)
        self.heuristicas = Heuristicas(self.instancia)
       

    def exec (self, tamanho_best = 10, tempo_max_execucao=180, metodo=0):
        inicio = time.time()
        solucao = self.heuristicas.solucao_inicial(0);
        if(solucao == None):
            solucao = self.heuristicas.solucao_inicial(1);
            

        fim = time.time()
        if (solucao != None):
            best_solutions = []
            
            if metodo == 0:
                inicio = time.time()
                solucao, best_solutions  = self.heuristicas.busca_local_d_linha_sem_restart(solucao,inicio,tempo_max_execucao, best_solutions, tamanho_best)
                fim = time.time()

            elif metodo == 1:
                inicio = time.time()
                solucao, best_solutions = self.heuristicas.busca_local_p_linha_semRestart(solucao,tamanho_best,tempo_max_execucao)
                fim = time.time()

            elif metodo == 2:
                inicio = time.time()
                solucao, best_solutions = self.heuristicas.busca_local_2_semRestart(solucao,tamanho_best,tempo_max_execucao)
                fim = time.time()

            elif metodo == 3:
                inicio = time.time()
                solucao, best_solutions = self.heuristicas.busca_local_2(solucao,tamanho_best, True ,tempo_max_execucao)
                fim = time.time()
 
        print("Temp. Exec. Algs: ", fim-inicio)
        solucao.tempo_execucao = fim-inicio
        return solucao , self.instancia
        #if(solucao.verifica_solucao_valida_original(inst) == False):
        #    print("Solucao invalida Gerada")


