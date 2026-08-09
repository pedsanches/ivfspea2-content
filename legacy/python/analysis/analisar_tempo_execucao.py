import pymatreader
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
from collections import defaultdict

# Função para carregar os dados de um arquivo .mat
def carregar_dados(caminho_arquivo):
    try:
        dados = pymatreader.read_mat(caminho_arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

# Função para inspecionar a estrutura de um arquivo .mat
def inspecionar_estrutura_arquivo(caminho_arquivo):
    """
    Inspeciona a estrutura de um arquivo .mat para entender
    quais campos estão disponíveis, especialmente relacionados ao tempo
    """
    dados = carregar_dados(caminho_arquivo)
    if dados is None:
        return None
    
    print(f"\nEstrutura do arquivo: {caminho_arquivo}")
    print("="*50)
    
    def mostrar_estrutura(obj, nivel=0, max_nivel=3):
        indent = "  " * nivel
        
        if isinstance(obj, dict):
            for chave, valor in obj.items():
                print(f"{indent}{chave}: {type(valor)}")
                if nivel < max_nivel:
                    if isinstance(valor, (dict, list, tuple)) and len(str(valor)) < 1000:
                        mostrar_estrutura(valor, nivel + 1, max_nivel)
                    elif isinstance(valor, np.ndarray):
                        print(f"{indent}  -> shape: {valor.shape}, dtype: {valor.dtype}")
                        if valor.size < 50:
                            print(f"{indent}  -> values: {valor}")
        elif isinstance(obj, (list, tuple)):
            print(f"{indent}Tipo: {type(obj)}, Tamanho: {len(obj)}")
            if len(obj) > 0 and nivel < max_nivel:
                mostrar_estrutura(obj[0], nivel + 1, max_nivel)
        elif isinstance(obj, np.ndarray):
            print(f"{indent}Array shape: {obj.shape}, dtype: {obj.dtype}")
            if obj.size < 20:
                print(f"{indent}Values: {obj}")
        else:
            print(f"{indent}Valor: {obj}")
    
    mostrar_estrutura(dados)
    return dados

# Função para extrair dados de tempo de execução
def extrair_dados_tempo(dados):
    """
    Extrai informações de tempo de execução dos dados do arquivo .mat
    """
    tempo_dados = {}
    
    # Verificar se existem campos relacionados ao tempo
    if 'runtime' in dados:
        tempo_dados['runtime'] = dados['runtime']
    
    if 'time' in dados:
        tempo_dados['time'] = dados['time']
    
    if 'elapsed_time' in dados:
        tempo_dados['elapsed_time'] = dados['elapsed_time']
    
    # Verificar se há informações de tempo dentro de métricas
    if 'metric' in dados and isinstance(dados['metric'], dict):
        for chave, valor in dados['metric'].items():
            if 'time' in chave.lower() or 'runtime' in chave.lower():
                tempo_dados[f'metric_{chave}'] = valor
    
    # Verificar se há informações de tempo em outros campos
    for chave, valor in dados.items():
        if 'time' in chave.lower() or 'runtime' in chave.lower():
            tempo_dados[chave] = valor
    
    return tempo_dados

# Função para analisar tempos de execução por configuração
def analisar_tempos_por_configuracao(base_path="Experimentos_Platemo/"):
    """
    Analisa os tempos de execução para diferentes configurações de R e C
    """
    dados_tempo = []
    
    # Buscar todas as pastas que correspondem ao padrão
    for pasta_nome in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta_nome)
        
        if os.path.isdir(pasta_path) and pasta_nome.startswith("IVFSPEA2_R"):
            print(f"\nAnalisando pasta: {pasta_nome}")
            
            # Extrair parâmetros R e C do nome da pasta
            try:
                partes = pasta_nome.split("_")
                r_value = float(partes[1][1:])  # Remove 'R' e converte para float
                c_value = float(partes[2][1:])  # Remove 'C' e converte para float
                problema = partes[3] if len(partes) > 3 else "DTLZ2"
            except:
                print(f"Erro ao extrair parâmetros da pasta: {pasta_nome}")
                continue
            
            # Analisar todos os arquivos .mat na pasta
            tempos_pasta = []
            for arquivo in os.listdir(pasta_path):
                if arquivo.endswith(".mat"):
                    caminho_arquivo = os.path.join(pasta_path, arquivo)
                    dados = carregar_dados(caminho_arquivo)
                    
                    if dados is not None:
                        tempo_dados = extrair_dados_tempo(dados)
                        
                        # Adicionar informações da configuração
                        tempo_dados.update({
                            'R': r_value,
                            'C': c_value,
                            'problema': problema,
                            'arquivo': arquivo,
                            'pasta': pasta_nome
                        })
                        
                        tempos_pasta.append(tempo_dados)
            
            dados_tempo.extend(tempos_pasta)
    
    return dados_tempo

# Função principal para executar a análise
def main():
    base_path = "Experimentos_Platemo/"
    
    # Primeiro, vamos inspecionar a estrutura de alguns arquivos
    print("=== INSPEÇÃO DA ESTRUTURA DOS ARQUIVOS ===")
    
    # Encontrar um arquivo para inspeção
    pasta_exemplo = None
    for pasta_nome in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta_nome)
        if os.path.isdir(pasta_path) and pasta_nome.startswith("IVFSPEA2_R"):
            pasta_exemplo = pasta_path
            break
    
    if pasta_exemplo:
        arquivo_exemplo = None
        for arquivo in os.listdir(pasta_exemplo):
            if arquivo.endswith(".mat"):
                arquivo_exemplo = os.path.join(pasta_exemplo, arquivo)
                break
        
        if arquivo_exemplo:
            dados_exemplo = inspecionar_estrutura_arquivo(arquivo_exemplo)
            
            # Extrair dados de tempo do arquivo exemplo
            print("\n=== DADOS DE TEMPO ENCONTRADOS ===")
            tempo_dados = extrair_dados_tempo(dados_exemplo)
            for chave, valor in tempo_dados.items():
                print(f"{chave}: {valor}")
    
    # Analisar todos os dados de tempo
    print("\n=== ANÁLISE COMPLETA DOS TEMPOS ===")
    dados_tempo = analisar_tempos_por_configuracao(base_path)
    
    # Converter para DataFrame para análise mais fácil
    if dados_tempo:
        df = pd.DataFrame(dados_tempo)
        print(f"\nTotal de experimentos analisados: {len(df)}")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
        
        # Salvar dados em CSV para análise posterior
        df.to_csv('dados_tempo_experimentos.csv', index=False)
        print("Dados salvos em 'dados_tempo_experimentos.csv'")
        
        # Mostrar estatísticas básicas
        print("\n=== ESTATÍSTICAS BÁSICAS ===")
        print(df.describe())
        
        return df
    else:
        print("Nenhum dado de tempo encontrado nos arquivos .mat")
        return None

if __name__ == "__main__":
    df_resultados = main() 