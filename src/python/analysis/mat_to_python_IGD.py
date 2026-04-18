import pymatreader
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

PROBLEM = 'MaF10'

# Função para carregar os dados de um arquivo .mat
def carregar_dados(caminho_arquivo):
    try:
        dados = pymatreader.read_mat(caminho_arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

# Função para processar os arquivos e extrair as métricas
def calcular_igd_map(R_poss, C_poss, base_path="Data/"):
    # Inicializa a matriz de IGD com NaN
    igd_matrix = np.full((len(R_poss), len(C_poss)), np.nan)
    
    # Iterar sobre todas as combinações de R e C
    for R in R_poss:
        for C in C_poss:
            pasta = f"{base_path}IVFSPEA2_R{R:.4f}_C{C:.2f}_{PROBLEM}"
            print(pasta)  # Formato do caminho
            if os.path.exists(pasta):  # Verifica se a pasta existe
                igds = []
                # Iterar sobre todos os arquivos .mat na pasta
                for arquivo in os.listdir(pasta):
                    if arquivo.endswith(".mat"):
                        caminho_arquivo = os.path.join(pasta, arquivo)
                        dados = carregar_dados(caminho_arquivo)
                        
                        if dados is not None:
                            try:
                                # Acessar a chave 'metric' e obter o IGD
                                metric = dados.get('metric', None)
                                if metric is not None:
                                    igd = metric.get('IGD', None)
                                    if igd is not None:
                                        min_igd = np.min(igd)  # Melhor IGD é o mínimo
                                        igds.append(min_igd)  # Adiciona o valor à lista de IGDs
                            except Exception as e:
                                print(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")
                
                # Calcular a média do IGD para aquela pasta (combinação de R e C)
                if igds:
                    # Excluir outliers baseado no desvio padrão (valores acima de 3 desvios padrão)
                    mean_igd = np.mean(igds)
                    std_igd = np.std(igds)
                    filtered_igd = [igd for igd in igds if (igd > mean_igd - 3 * std_igd) and (igd < mean_igd + 3 * std_igd)]
                    
                    if filtered_igd:  # Certificar-se de que ainda há dados após a filtragem
                        mean_igd_filtered = np.mean(filtered_igd)  # Média sem outliers
                        igd_matrix[R_poss.index(R), C_poss.index(C)] = mean_igd_filtered  # Atribui à matriz
                        print(f"Valor IGD calculado (sem outliers): {mean_igd_filtered}, Tipo de dado: {type(mean_igd_filtered)}")
                    else:
                        print(f"Após a remoção dos outliers, nenhum IGD válido encontrado para {pasta}")
                else:
                    print(f"Nenhum IGD calculado para {pasta}")
            else:
                print(f"Pasta não encontrada: {pasta}")
    
    # Garantir que todos os valores na matriz sejam do tipo float
    igd_matrix = np.array(igd_matrix, dtype=float)
    
    return igd_matrix

# Definir as possibilidades de R e C
# R_poss = [2, 3, 4, 5, 6, 7]
# C_poss = [0, 1, 2, 3, 4, 5]
R_poss = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300]
C_poss = [0.05, 0.07, 0.11, 0.16, 0.21, 0.27, 0.32, 0.42, 0.53, 0.64]

# Caminho base
base_path = "Data/"

# Calcular a matriz de IGD para as combinações de R e C
igd_matrix = calcular_igd_map(R_poss, C_poss, base_path)

# Verificando se a matriz contém NaN (caso não tenha encontrado alguma configuração)
if np.any(np.isnan(igd_matrix)):
    print("Alguns valores de IGD não foram encontrados para todas as combinações de R e C.")

# Normalizar os valores de IGD para o intervalo [0, 1]
scaler = MinMaxScaler()

# Gerar o mapa de calor do IGD
plt.figure(figsize=(8, 6))

# Criar o gráfico com a normalização
plt.imshow(igd_matrix, cmap='RdYlBu', aspect='auto', origin='upper')
plt.colorbar(label='IGD')

plt.title(f'Mapa de Calor do IGD - {PROBLEM}')

# Ajustando os rótulos dos ticks (não as posições)
plt.xlabel('C_poss')
plt.ylabel('R_poss')

# Ajuste dos labels dos ticks no eixo x (C)
plt.xticks(ticks=np.arange(len(C_poss)), labels=C_poss)

# Ajuste dos labels dos ticks no eixo y (R)
plt.yticks(ticks=np.arange(len(R_poss)), labels=R_poss)

plt.show()
