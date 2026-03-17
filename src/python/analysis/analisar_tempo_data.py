import pymatreader
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import time

def carregar_dados(caminho_arquivo):
    """Carrega dados de um arquivo .mat"""
    try:
        dados = pymatreader.read_mat(caminho_arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def inspecionar_estrutura_arquivo(caminho_arquivo):
    """Inspeciona a estrutura de um arquivo .mat para encontrar dados de tempo"""
    dados = carregar_dados(caminho_arquivo)
    if dados is None:
        return None
    
    print(f"\nEstrutura do arquivo: {os.path.basename(caminho_arquivo)}")
    print("="*60)
    
    def mostrar_estrutura(obj, nivel=0, max_nivel=3):
        indent = "  " * nivel
        
        if isinstance(obj, dict):
            for chave, valor in obj.items():
                if isinstance(valor, np.ndarray):
                    print(f"{indent}{chave}: numpy.array(shape={valor.shape}, dtype={valor.dtype})")
                    # Se é pequeno, mostra alguns valores
                    if valor.size <= 10:
                        print(f"{indent}  -> valores: {valor}")
                else:
                    print(f"{indent}{chave}: {type(valor)}")
                    
                # Recursão para estruturas aninhadas
                if nivel < max_nivel and isinstance(valor, dict):
                    mostrar_estrutura(valor, nivel + 1, max_nivel)
        else:
            print(f"{indent}Tipo: {type(obj)}")
    
    mostrar_estrutura(dados)
    return dados

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

def extrair_dados_tempo(dados):
    """Extrai informações de tempo de execução dos dados"""
    tempo_info = {}
    
    # A métrica principal de tempo está em metric['runtime']
    if 'metric' in dados and isinstance(dados['metric'], dict):
        if 'runtime' in dados['metric']:
            tempo_info['runtime'] = dados['metric']['runtime']
            
        # Também extrair outras métricas úteis para contexto
        for chave, valor in dados['metric'].items():
            if chave != 'runtime':  # Runtime já foi extraído acima
                tempo_info[f'metric_{chave}'] = valor
    
    # Verificar outros campos de tempo caso existam (backup)
    campos_tempo_alternativos = ['time', 'elapsed_time', 'execution_time', 'cpu_time']
    for campo in campos_tempo_alternativos:
        if campo in dados and campo not in tempo_info:
            tempo_info[campo] = dados[campo]
    
    # Buscar por qualquer campo que contenha 'time' no nome (backup)
    for chave, valor in dados.items():
        if 'time' in chave.lower() and chave not in tempo_info:
            tempo_info[chave] = valor
    
    return tempo_info

def analisar_todos_algoritmos(base_path="/home/pedro/Downloads/Experimentos_Platemo_v2/PlatEMO/Data"):
    """Analisa todos os algoritmos na pasta Data"""
    
    # Lista para armazenar todos os dados
    todos_dados = []
    
    print(f"Analisando dados em: {base_path}")
    
    # Iterar por todas as pastas de algoritmos
    for pasta_algoritmo in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta_algoritmo)
        
        # Pular se não for diretório ou se for o arquivo Setting.mat
        if not os.path.isdir(pasta_path) or pasta_algoritmo == 'Setting.mat':
            continue
            
        print(f"\n=== Analisando algoritmo: {pasta_algoritmo} ===")
        
        # Contar arquivos na pasta
        arquivos_mat = [f for f in os.listdir(pasta_path) if f.endswith('.mat')]
        print(f"Encontrados {len(arquivos_mat)} arquivos .mat")
        
        # Analisar cada arquivo
        for i, arquivo in enumerate(arquivos_mat):
            if i % 50 == 0:  # Progress indicator
                print(f"Processando arquivo {i+1}/{len(arquivos_mat)}: {arquivo}")
            
            caminho_arquivo = os.path.join(pasta_path, arquivo)
            
            # Extrair informações do nome do arquivo
            info_arquivo = extrair_informacoes_arquivo(arquivo)
            if info_arquivo is None:
                continue
            
            # Carregar dados do arquivo
            dados = carregar_dados(caminho_arquivo)
            if dados is None:
                continue
            
            # Extrair dados de tempo
            tempo_dados = extrair_dados_tempo(dados)
            
            # Criar registro completo
            registro = {
                'Grupo': info_arquivo['Grupo'],  # Grupo de benchmark (MaF, WFG, etc.)
                'Algoritmo': info_arquivo['Algoritmo'],
                'Problema': info_arquivo['Problema'],
                'Run': info_arquivo['Run'],
                'M': info_arquivo['M'],
                'D': info_arquivo['D'],
                'arquivo_original': arquivo
            }
            
            # Adicionar dados de tempo encontrados
            registro.update(tempo_dados)
            
            todos_dados.append(registro)
    
    return todos_dados

def criar_visualizacoes(df):
    """Cria visualizações dos dados de tempo"""
    
    # Verificar se temos a métrica principal de tempo (runtime)
    if 'runtime' not in df.columns:
        print("Métrica 'runtime' não encontrada nos dados")
        return
    
    # Focar na métrica runtime que sabemos que existe
    col_tempo = 'runtime'
    
    # Converter para numérico se necessário
    df[col_tempo] = pd.to_numeric(df[col_tempo], errors='coerce')
    
    # Filtrar valores válidos
    df_valid = df[df[col_tempo].notna()]
    
    if len(df_valid) == 0:
        print("Nenhum valor válido de runtime encontrado")
        return
    
    print(f"Criando visualizações para {len(df_valid)} registros com runtime válido")
    
    try:
        # Configurar o estilo
        plt.style.use('default')  # Usar estilo padrão para compatibilidade
        
        # 1. Boxplot por algoritmo
        plt.figure(figsize=(14, 8))
        algorithms = df_valid['Algoritmo'].unique()
        data_by_algo = [df_valid[df_valid['Algoritmo'] == algo][col_tempo].values for algo in algorithms]
        
        plt.boxplot(data_by_algo, labels=algorithms)
        plt.title(f'Distribuição de Tempo de Execução por Algoritmo')
        plt.ylabel(f'Tempo de Execução (segundos)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'tempo_execucao_por_algoritmo.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Boxplot por grupo de benchmark
        plt.figure(figsize=(12, 8))
        grupos = df_valid['Grupo'].unique()
        data_by_grupo = [df_valid[df_valid['Grupo'] == grupo][col_tempo].values for grupo in grupos]
        
        plt.boxplot(data_by_grupo, labels=grupos)
        plt.title(f'Distribuição de Tempo de Execução por Grupo de Benchmark')
        plt.ylabel(f'Tempo de Execução (segundos)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'tempo_execucao_por_grupo.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 3. Boxplot por problema (limitado aos mais frequentes)
        problemas_freq = df_valid['Problema'].value_counts().head(10)
        df_problemas_top = df_valid[df_valid['Problema'].isin(problemas_freq.index)]
        
        plt.figure(figsize=(14, 8))
        problemas = df_problemas_top['Problema'].unique()
        data_by_problema = [df_problemas_top[df_problemas_top['Problema'] == prob][col_tempo].values for prob in problemas]
        
        plt.boxplot(data_by_problema, labels=problemas)
        plt.title(f'Distribuição de Tempo de Execução por Problema (Top 10)')
        plt.ylabel(f'Tempo de Execução (segundos)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'tempo_execucao_por_problema_top10.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 4. Heatmap algoritmo vs grupo
        if len(df_valid['Algoritmo'].unique()) > 1 and len(df_valid['Grupo'].unique()) > 1:
            pivot_table = df_valid.pivot_table(values=col_tempo, 
                                             index='Algoritmo', 
                                             columns='Grupo', 
                                             aggfunc='mean')
            
            plt.figure(figsize=(10, 8))
            import seaborn as sns
            sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='viridis', cbar_kws={'label': 'Tempo médio (s)'})
            plt.title(f'Tempo Médio de Execução - Algoritmo vs Grupo de Benchmark')
            plt.tight_layout()
            plt.savefig(f'heatmap_tempo_algoritmo_grupo.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 5. Estatísticas por algoritmo
        print("\n=== ESTATÍSTICAS DE TEMPO POR ALGORITMO ===")
        stats_algo = df_valid.groupby('Algoritmo')[col_tempo].agg(['count', 'mean', 'std', 'min', 'max']).round(3)
        print(stats_algo)
        
        # 6. Estatísticas por grupo
        print("\n=== ESTATÍSTICAS DE TEMPO POR GRUPO ===")
        stats_grupo = df_valid.groupby('Grupo')[col_tempo].agg(['count', 'mean', 'std', 'min', 'max']).round(3)
        print(stats_grupo)
        
        # 7. Ranking de algoritmos por tempo médio
        print("\n=== RANKING DE ALGORITMOS (TEMPO MÉDIO) ===")
        ranking = df_valid.groupby('Algoritmo')[col_tempo].mean().sort_values()
        for i, (algo, tempo) in enumerate(ranking.items(), 1):
            print(f"{i}. {algo}: {tempo:.3f} segundos")
                    
    except Exception as e:
        print(f"Erro ao criar visualização: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("=== ANÁLISE DE TEMPO DE EXECUÇÃO DOS ALGORITMOS ===")
    
    # Caminho base
    base_path = "/home/pedro/Downloads/Experimentos_Platemo_v2/PlatEMO/Data"
    
    # Verificar se o caminho existe
    if not os.path.exists(base_path):
        print(f"Caminho não encontrado: {base_path}")
        return None
    
    # Primeiro, inspecionar um arquivo para entender a estrutura
    print("\n=== INSPEÇÃO DA ESTRUTURA DE UM ARQUIVO ===")
    
    # Encontrar o primeiro arquivo .mat para inspeção
    arquivo_exemplo = None
    for pasta in os.listdir(base_path):
        pasta_path = os.path.join(base_path, pasta)
        if os.path.isdir(pasta_path):
            for arquivo in os.listdir(pasta_path):
                if arquivo.endswith('.mat'):
                    arquivo_exemplo = os.path.join(pasta_path, arquivo)
                    break
            if arquivo_exemplo:
                break
    
    if arquivo_exemplo:
        dados_exemplo = inspecionar_estrutura_arquivo(arquivo_exemplo)
        
        print("\n=== DADOS DE TEMPO ENCONTRADOS NO ARQUIVO EXEMPLO ===")
        if dados_exemplo:
            tempo_dados = extrair_dados_tempo(dados_exemplo)
            if tempo_dados:
                for chave, valor in tempo_dados.items():
                    print(f"{chave}: {valor} (tipo: {type(valor)})")
            else:
                print("Nenhum dado de tempo encontrado")
    
    # Analisar todos os dados
    print("\n=== ANÁLISE COMPLETA DE TODOS OS ALGORITMOS ===")
    
    inicio_analise = time.time()
    todos_dados = analisar_todos_algoritmos(base_path)
    fim_analise = time.time()
    
    print(f"\nAnálise concluída em {fim_analise - inicio_analise:.2f} segundos")
    
    if not todos_dados:
        print("Nenhum dado foi coletado")
        return None
    
    # Converter para DataFrame
    df = pd.DataFrame(todos_dados)
    
    print(f"\n=== RESUMO DOS DADOS COLETADOS ===")
    print(f"Total de registros: {len(df)}")
    print(f"Grupos de benchmark únicos: {df['Grupo'].nunique()} - {list(df['Grupo'].unique())}")
    print(f"Algoritmos únicos: {df['Algoritmo'].nunique()} - {list(df['Algoritmo'].unique())}")
    print(f"Problemas únicos: {df['Problema'].nunique()} - {list(df['Problema'].unique())}")
    print(f"Runs únicos: {df['Run'].nunique()} - {sorted(df['Run'].unique())}")
    
    print(f"\n=== COLUNAS DISPONÍVEIS ===")
    print(df.columns.tolist())
    
    # Identificar colunas de tempo (focar no runtime que sabemos que existe)
    colunas_tempo = ['runtime']
    colunas_tempo_disponiveis = [col for col in colunas_tempo if col in df.columns]
    
    print(f"\nMétrica principal de tempo encontrada: {colunas_tempo_disponiveis}")
    
    # Mostrar estatísticas básicas para runtime
    print(f"\n=== ESTATÍSTICAS BÁSICAS PARA RUNTIME ===")
    if 'runtime' in df.columns:
        # Converter para numérico
        df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
        
        print("\nEstatísticas gerais para runtime:")
        runtime_stats = df['runtime'].describe()
        print(runtime_stats)
        
        # Verificar valores nulos
        null_count = df['runtime'].isnull().sum()
        total_count = len(df)
        print(f"\nValores válidos: {total_count - null_count}/{total_count} ({((total_count - null_count)/total_count)*100:.1f}%)")
        
        if null_count > 0:
            print(f"Valores nulos encontrados: {null_count}")
    
    # Salvar dados
    nome_arquivo_csv = 'analise_tempo_algoritmos_completa.csv'
    df.to_csv(nome_arquivo_csv, index=False)
    print(f"\nDados salvos em: {nome_arquivo_csv}")
    
    # Criar visualizações se houver dados de runtime
    if 'runtime' in df.columns and df['runtime'].notna().any():
        print(f"\n=== CRIANDO VISUALIZAÇÕES ===")
        criar_visualizacoes(df)
    else:
        print("Nenhum dado de runtime válido encontrado para visualização")
    
    return df

if __name__ == "__main__":
    df_resultados = main() 