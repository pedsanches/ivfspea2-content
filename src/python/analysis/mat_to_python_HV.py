import pymatreader
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Função para carregar os dados de um arquivo .mat
def carregar_dados(caminho_arquivo):
    dados = pymatreader.read_mat(caminho_arquivo)
    return dados

# Função para processar os arquivos e extrair as métricas
def calcular_hv_map(R_poss, C_poss, base_path="Data/"):
    # Inicializa a matriz de HV com NaN
    hv_matrix = np.full((len(R_poss), len(C_poss)), np.nan)
    
    # Iterar sobre todas as combinações de R e C
    for R in R_poss:
        for C in C_poss:
            pasta = f"{base_path}IVFSPEA2_R{R:.3f}_C{C:.0f}_DTLZ1"  # Formato do caminho
            if os.path.exists(pasta):  # Verifica se a pasta existe
                hvs = []
                # Iterar sobre todos os arquivos .mat na pasta
                for arquivo in os.listdir(pasta):
                    if arquivo.endswith(".mat"):
                        caminho_arquivo = os.path.join(pasta, arquivo)
                        dados = carregar_dados(caminho_arquivo)
                        
                        # Acessar a chave 'metric' e obter o HV
                        metric = dados.get('metric', None)
                        if metric is not None:
                            hv = metric.get('HV', None)
                            if hv is not None:
                                max_hv = np.max(hv)  # Melhor HV é o mínimo
                                hvs.append(max_hv)  # Adiciona o valor à lista de HVs
                
                # Calcular a média do HV para aquela pasta (combinação de R e C)
                if hvs:
                    mean_hv = np.mean(hvs)  # Média do HV
                    hv_matrix[R_poss.index(R), C_poss.index(C)] = mean_hv  # Atribui à matriz
                    
                    # Print do tipo de dado e valor
                    print(f"Valor HV calculado: {mean_hv}, Tipo de dado: {type(mean_hv)}")
            else:
                print(f"Pasta não encontrada: {pasta}")
    
    # Garantir que todos os valores na matriz sejam do tipo float
    hv_matrix = np.array(hv_matrix, dtype=float)
    
    return hv_matrix

# Definir as possibilidades de R e C
R_poss = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300]
C_poss = [5, 7, 11, 16, 21, 27, 32, 42, 53, 64]

# Caminho base
base_path = "Data/"

# Calcular a matriz de HV para as combinações de R e C
hv_matrix = calcular_hv_map(R_poss, C_poss, base_path)

# Verificando se a matriz contém NaN (caso não tenha encontrado alguma configuração)
if np.any(np.isnan(hv_matrix)):
    print("Alguns valores de HV não foram encontrados para todas as combinações de R e C.")

# Normalizar os valores de HV para o intervalo [0, 1]
scaler = MinMaxScaler()
hv_matrix_normalized = scaler.fit_transform(np.nan_to_num(hv_matrix).T).T  # Normalizando por linha

# Gerar o mapa de calor do HV
plt.figure(figsize=(8, 6))

# Criar o gráfico com a normalização
plt.imshow(hv_matrix_normalized, cmap='coolwarm', aspect='auto', origin='upper')
plt.colorbar(label='HV Normalizado (0 a 1)')

plt.title('Mapa de Calor do HV - Todas as Configurações')

# Ajustando os rótulos dos ticks (não as posições)
plt.xlabel('C')
plt.ylabel('R')

# Ajuste dos labels dos ticks no eixo x (C)
plt.xticks(ticks=np.arange(len(C_poss)), labels=C_poss)

# Ajuste dos labels dos ticks no eixo y (R)
plt.yticks(ticks=np.arange(len(R_poss)), labels=R_poss)

plt.show()
