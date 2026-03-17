import pymatreader
import numpy as np
import os
import pandas as pd
import time
from collections import defaultdict

def carregar_dados(caminho_arquivo):
    """Carrega dados de um arquivo .mat"""
    try:
        dados = pymatreader.read_mat(caminho_arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def extrair_informacoes_arquivo(nome_arquivo):
    """Extrai Algoritmo, Problema, Grupo (benchmark) e Run do nome do arquivo"""
    # Formato esperado: ALGORITMO_PROBLEMA_M3_D12_RUN.mat
    # Exemplo: IVFSPEA2_WFG9_M3_D12_1.mat
    partes = nome_arquivo.replace('.mat', '').split('_')
    
    if len(partes) >= 5:
        algoritmo = partes[0]
        problema = partes[1]
        # M3 e D12 são parâmetros fixos neste caso
        m_param = partes[2]  # M3
        d_param = partes[3]  # D12
        run = int(partes[4])
        
        # Extrair o grupo de benchmark do problema
        # Exemplo: WFG9 -> grupo = WFG, problema = WFG9
        # Exemplo: MaF10 -> grupo = MaF, problema = MaF10
        grupo = None
        if problema.startswith('WFG'):
            grupo = 'WFG'
        elif problema.startswith('MaF'):
            grupo = 'MaF'
        elif problema.startswith('DTLZ'):
            grupo = 'DTLZ'
        elif problema.startswith('UF'):
            grupo = 'UF'
        elif problema.startswith('ZDT'):
            grupo = 'ZDT'
        else:
            # Se não reconhecer, usar os primeiros caracteres
            grupo = problema[:3] if len(problema) >= 3 else problema
        
        return {
            'Algoritmo': algoritmo,
            'Problema': problema,
            'Grupo': grupo,
            'M': m_param,
            'D': d_param,
            'Run': run
        }
    else:
        print(f"Formato de arquivo não reconhecido: {nome_arquivo}")
        return None

def extrair_todas_metricas(dados):
    """Extrai todas as métricas disponíveis dos dados"""
    metricas = {}
    
    # As métricas estão no campo 'metric'
    if 'metric' in dados and isinstance(dados['metric'], dict):
        for chave, valor in dados['metric'].items():
            # Converter valores para tipos Python nativos se necessário
            if isinstance(valor, np.ndarray):
                if valor.size == 1:
                    metricas[chave] = float(valor.item())
                else:
                    # Se for um array, pegar o último valor (geralmente é o resultado final)
                    metricas[chave] = float(valor[-1]) if len(valor) > 0 else np.nan
            elif isinstance(valor, (int, float)):
                metricas[chave] = float(valor)
            else:
                metricas[chave] = valor
    
    return metricas

def coletar_todos_dados(base_path="/home/pedro/Downloads/Experimentos_Platemo_v2/PlatEMO/Data"):
    """Coleta todos os dados de todas as métricas de todos os arquivos"""
    
    print(f"Coletando dados de: {base_path}")
    
    # Dicionário para armazenar dados por métrica
    dados_por_metrica = defaultdict(list)
    todas_metricas_encontradas = set()
    
    total_arquivos = 0
    arquivos_processados = 0
    
    # Contar total de arquivos primeiro
    for pasta_algoritmo in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta_algoritmo)
        if os.path.isdir(pasta_path):
            arquivos_mat = [f for f in os.listdir(pasta_path) if f.endswith('.mat')]
            total_arquivos += len(arquivos_mat)
    
    print(f"Total de arquivos a processar: {total_arquivos}")
    
    # Processar todos os arquivos
    for pasta_algoritmo in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta_algoritmo)
        
        # Pular se não for diretório
        if not os.path.isdir(pasta_path):
            continue
            
        print(f"\n=== Processando algoritmo: {pasta_algoritmo} ===")
        
        # Contar arquivos na pasta
        arquivos_mat = [f for f in os.listdir(pasta_path) if f.endswith('.mat')]
        print(f"Arquivos nesta pasta: {len(arquivos_mat)}")
        
        # Analisar cada arquivo
        for arquivo in arquivos_mat:
            arquivos_processados += 1
            
            if arquivos_processados % 100 == 0:
                print(f"Progresso: {arquivos_processados}/{total_arquivos} ({(arquivos_processados/total_arquivos)*100:.1f}%)")
            
            caminho_arquivo = os.path.join(pasta_path, arquivo)
            
            # Extrair informações do nome do arquivo
            info_arquivo = extrair_informacoes_arquivo(arquivo)
            if info_arquivo is None:
                continue
            
            # Carregar dados do arquivo
            dados = carregar_dados(caminho_arquivo)
            if dados is None:
                continue
            
            # Extrair todas as métricas
            metricas = extrair_todas_metricas(dados)
            
            # Registrar todas as métricas encontradas
            todas_metricas_encontradas.update(metricas.keys())
            
            # Para cada métrica encontrada, adicionar aos dados
            for metrica, valor in metricas.items():
                registro = {
                    'Grupo': info_arquivo['Grupo'],
                    'Algoritmo': info_arquivo['Algoritmo'],
                    'Problema': info_arquivo['Problema'],
                    'Run': info_arquivo['Run'],
                    'M': info_arquivo['M'],
                    'D': info_arquivo['D'],
                    metrica: valor,
                    'arquivo_original': arquivo
                }
                dados_por_metrica[metrica].append(registro)
    
    print(f"\nProcessamento concluído!")
    print(f"Arquivos processados: {arquivos_processados}/{total_arquivos}")
    print(f"Métricas encontradas: {sorted(todas_metricas_encontradas)}")
    
    return dados_por_metrica, todas_metricas_encontradas

def gerar_csvs_por_metrica(dados_por_metrica, todas_metricas):
    """Gera um arquivo CSV para cada métrica"""
    
    print(f"\n=== GERANDO ARQUIVOS CSV ===")
    
    arquivos_gerados = []
    
    for metrica in sorted(todas_metricas):
        if metrica in dados_por_metrica:
            # Criar DataFrame para esta métrica
            df_metrica = pd.DataFrame(dados_por_metrica[metrica])
            
            # Ordenar por Grupo, Algoritmo, Problema, Run
            df_metrica = df_metrica.sort_values(['Grupo', 'Algoritmo', 'Problema', 'Run'])
            
            # Nome do arquivo CSV
            nome_arquivo = f'metrica_{metrica}.csv'
            
            # Salvar CSV
            df_metrica.to_csv(nome_arquivo, index=False)
            
            print(f"✓ {nome_arquivo}: {len(df_metrica)} registros")
            
            # Mostrar estatísticas básicas
            if metrica in df_metrica.columns:
                valores_validos = df_metrica[metrica].notna().sum()
                print(f"  - Valores válidos: {valores_validos}/{len(df_metrica)}")
                if valores_validos > 0:
                    stats = df_metrica[metrica].describe()
                    print(f"  - Média: {stats['mean']:.6f}, Std: {stats['std']:.6f}")
                    print(f"  - Min: {stats['min']:.6f}, Max: {stats['max']:.6f}")
            
            arquivos_gerados.append(nome_arquivo)
    
    return arquivos_gerados

def gerar_csv_consolidado(dados_por_metrica, todas_metricas):
    """Gera um arquivo CSV consolidado com todas as métricas"""
    
    print(f"\n=== GERANDO ARQUIVO CONSOLIDADO ===")
    
    # Criar um dicionário para consolidar todos os dados
    dados_consolidados = {}
    
    # Para cada arquivo, queremos ter uma linha com todas as métricas
    for metrica, registros in dados_por_metrica.items():
        for registro in registros:
            # Criar chave única para identificar cada execução
            chave = (
                registro['Grupo'],
                registro['Algoritmo'], 
                registro['Problema'],
                registro['Run'],
                registro['arquivo_original']
            )
            
            # Se ainda não existe registro para esta chave, criar
            if chave not in dados_consolidados:
                dados_consolidados[chave] = {
                    'Grupo': registro['Grupo'],
                    'Algoritmo': registro['Algoritmo'],
                    'Problema': registro['Problema'],
                    'Run': registro['Run'],
                    'M': registro['M'],
                    'D': registro['D'],
                    'arquivo_original': registro['arquivo_original']
                }
                # Inicializar todas as métricas com NaN
                for m in todas_metricas:
                    dados_consolidados[chave][m] = np.nan
            
            # Adicionar o valor da métrica atual
            dados_consolidados[chave][metrica] = registro[metrica]
    
    # Converter para DataFrame
    df_consolidado = pd.DataFrame(list(dados_consolidados.values()))
    
    # Ordenar
    df_consolidado = df_consolidado.sort_values(['Grupo', 'Algoritmo', 'Problema', 'Run'])
    
    # Salvar
    nome_arquivo = 'todas_metricas_consolidado.csv'
    df_consolidado.to_csv(nome_arquivo, index=False)
    
    print(f"✓ {nome_arquivo}: {len(df_consolidado)} registros")
    print(f"  - Colunas: {list(df_consolidado.columns)}")
    
    # Mostrar completude dos dados
    print(f"\n=== COMPLETUDE DOS DADOS ===")
    for metrica in sorted(todas_metricas):
        if metrica in df_consolidado.columns:
            valores_validos = df_consolidado[metrica].notna().sum()
            total = len(df_consolidado)
            porcentagem = (valores_validos/total)*100
            print(f"{metrica}: {valores_validos}/{total} ({porcentagem:.1f}%)")
    
    return nome_arquivo

def main():
    """Função principal"""
    print("=== GERAÇÃO DE ARQUIVOS CSV POR MÉTRICA ===")
    
    # Caminho base
    base_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "src", "matlab", "lib", "PlatEMO", "Data"
    )
    
    # Verificar se o caminho existe
    if not os.path.exists(base_path):
        print(f"Caminho não encontrado: {base_path}")
        return None
    
    # Coletar todos os dados
    inicio = time.time()
    dados_por_metrica, todas_metricas = coletar_todos_dados(base_path)
    fim = time.time()
    
    print(f"\nColeta concluída em {fim - inicio:.2f} segundos")
    
    if not dados_por_metrica:
        print("Nenhum dado foi coletado")
        return None
    
    # Gerar CSVs individuais por métrica
    arquivos_individuais = gerar_csvs_por_metrica(dados_por_metrica, todas_metricas)
    
    # Gerar CSV consolidado
    arquivo_consolidado = gerar_csv_consolidado(dados_por_metrica, todas_metricas)
    
    print(f"\n=== RESUMO ===")
    print(f"Métricas processadas: {len(todas_metricas)}")
    print(f"Arquivos CSV individuais gerados: {len(arquivos_individuais)}")
    print(f"Arquivo consolidado: {arquivo_consolidado}")
    
    print(f"\nArquivos gerados:")
    for arquivo in arquivos_individuais:
        print(f"  - {arquivo}")
    print(f"  - {arquivo_consolidado}")
    
    return dados_por_metrica, todas_metricas

if __name__ == "__main__":
    resultado = main() 