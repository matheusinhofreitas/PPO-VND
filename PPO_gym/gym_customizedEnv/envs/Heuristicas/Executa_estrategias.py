#from importlib.metadata import files
from importlib_metadata import files
from os import listdir
from os.path import *
from gym_customizedEnv.envs.Heuristicas.read import *
from gym_customizedEnv.envs.Heuristicas.solver import *


def executa_estrategias(path, arquivoSaida, temp_exec):
    files = listar_arquivos(path)
    files.sort()
    
    Lista = []
    Lista.append((0,"BL d_linha"))
    Lista.append((1,"BL p_linha"))
    Lista.append((2,"BL p+d"))
    Lista.append((3,"BL p+d Rest"))

      
    #remover as instancias que já foram executadas da lista
    myfile = open(arquivoSaida, "a+")   #open('Instances.txt')
    next_line = myfile.readline()
    
    while next_line != "" and next_line != "\n": 
       split_line = next_line.split(',')
       inst_exec = split_line[0]
       print("Removendo : ",inst_exec)
       inst_exec = inst_exec + ".txt"
       files.remove(inst_exec)
       next_line = myfile.readline()
      
    myfile.close()

    cont = 0
    try:
        files.remove("Amostra")
    except:
        print("An exception occurred: files.remove(\"Amostra\")")
    for nome in files:
        local = path +"/"+nome
        print(nome)
        solver = Solver(path, nome)
        valores = []
        tempos = []
        for i in range(0,len(Lista)):
            print(Lista[i][1])
            solucao, instancia = solver.exec(0,temp_exec,Lista[i][0])
            valores.append((Lista[i][0], solucao.FO))
            tempos.append((Lista[i][0], solucao.tempo_execucao))
            print(Lista[i][1])
            print(solucao.FO)
            print(solucao.tempo_execucao)

        Rest = open(arquivoSaida,"a+")
        nome_p = nome.split(".")
        Rest.write(str(nome_p[0]))
        for i in valores:
            Rest.write(",%s"%str(i[0]))
            Rest.write(",%s"%str(i[1]))
        Rest.write("\n")
        Rest.close()
        
        saida = "tempos_" + arquivoSaida
        Rest = open(saida,"a+")
        Rest.write(str(nome_p[0]))
        for i in tempos:
            Rest.write(",%s"%str(i[0]))
            Rest.write(",%s"%str(i[1]))
        Rest.write("\n")
        Rest.close()
