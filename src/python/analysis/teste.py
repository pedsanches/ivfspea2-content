import os
import re
import scipy.io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib as mpl

# Configurações para melhorar a visualização
plt.rcParams.update({"font.size": 12})
sns.set_style("whitegrid")
sns.set_palette("colorblind")

# Caminhos das pastas
# Caminhos das pastas
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../matlab/lib/PlatEMO/Data")
output_dir = os.path.join(base_dir, "../../../results/figures")
processed_data_dir = os.path.join(base_dir, "../../../data/processed")

algorithms = ["IVFSPEA2", "SPEA2", "NSGAIII", "NSGAII", "MOEAD", "SPEA2SDE", "MFOSPEA2"]
algorithm_paths = {alg: os.path.join(data_path, alg) for alg in algorithms}


# Função para extrair problema do nome do arquivo
def get_problem(filename):
    base_problem_name = "UnknownProblem"
    problem_patterns = [
        r"ZDT\d+",  # ZDT1, ZDT2, etc.
        r"WFG\d+",  # WFG1, WFG2, etc.
        r"DTLZ\d+",  # DTLZ1, DTLZ2, etc.
        r"MaF\d+",  # MaF1, MaF2, etc.
    ]

    for pattern in problem_patterns:
        match = re.search(pattern, filename)
        if match:
            base_problem_name = match.group(0)
            break

    if base_problem_name == "UnknownProblem":
        return "Unknown"  # Match original behavior for truly unknown problem patterns

    objective_suffix = get_objective_count(filename)  # Uses the existing function

    if objective_suffix:
        return f"{base_problem_name}_{objective_suffix}"
    else:
        # If no objective suffix is found, return the base problem name.
        # This might occur if objective_suffix_filters is None in load_results
        # and a file matches a base problem but has no M-suffix.
        return base_problem_name


# Função para extrair número de objetivos do nome do arquivo
def get_objective_count(filename):
    match = re.search(r"M(\d+)", filename)
    if match:
        return match.group(0)  # Retorna M2, M3, etc.
    return None


# Função para extrair a métrica de interesse do .mat
def extract_metric(matfile, metric="IGD"):
    try:
        data = scipy.io.loadmat(matfile)
        # Verificamos se existe o campo 'metric' nos dados
        if "metric" in data:
            metric_data = data["metric"]
            # ---- START DIAGNOSTIC PRINTS ----
            # print(f"DEBUG: Processing {matfile} for metric {metric}")
            # print(f"DEBUG: metric_data shape: {metric_data.shape}, type: {type(metric_data)}")
            # if metric_data.size > 0:
            #     print(f"DEBUG: metric_data[0,0] type: {type(metric_data[0,0])}, value: {metric_data[0,0]}")
            # ---- END DIAGNOSTIC PRINTS ----

            # A métrica geralmente está no formato [[(HV, IGD)]]
            if metric_data.shape == (1, 1):
                # Se for um array, pegamos o primeiro elemento
                values = metric_data[0, 0]
                # ---- START DIAGNOSTIC PRINTS ----
                # print(f"DEBUG: Extracted 'values': {values}, type: {type(values)}, length: {len(values) if hasattr(values, '__len__') else 'N/A'}")
                # ---- END DIAGNOSTIC PRINTS ----

                # IGD está no índice 1, HV está no índice 0
                if metric.upper() == "IGD":
                    # Verifica se o segundo elemento existe
                    if (
                        hasattr(values, "__len__") and len(values) > 1
                    ):  # Check if 'values' is a sequence and has at least two elements
                        try:
                            igd_val = values[1].item()
                            # print(f"DEBUG: Attempting to return IGD: {igd_val} from values[1]")
                            return np.array([igd_val])
                        except Exception as e:
                            # print(f"DEBUG: Error accessing values[1].item() for IGD: {e}")
                            pass  # Fall through to return None
                    # else:
                    # print(f"DEBUG: Not enough elements in 'values' for IGD (len: {len(values) if hasattr(values, '__len__') else 'N/A'})")
                # Se for HV, pega o primeiro elemento da tupla
                elif metric.upper() == "HV":
                    if (
                        hasattr(values, "__len__") and len(values) > 0
                    ):  # Check if 'values' is a sequence and has at least one element
                        try:
                            hv_val = values[0].item()
                            # print(f"DEBUG: Attempting to return HV: {hv_val} from values[0]")
                            return np.array([hv_val])
                        except Exception as e:
                            # print(f"DEBUG: Error accessing values[0].item() for HV: {e}")
                            pass  # Fall through to return None
                    # else:
                    # print(f"DEBUG: Not enough elements in 'values' for HV (len: {len(values) if hasattr(values, '__len__') else 'N/A'})")
            # else:
            # print(f"DEBUG: metric_data.shape is not (1,1): {metric_data.shape}")
        # else:
        # print(f"DEBUG: 'metric' not in data for {matfile}")

    except Exception as e:
        print(f"Erro ao processar {matfile}: {e}")
        # print(f"DEBUG: Full error in extract_metric for {matfile}: {e}")
    # print(f"DEBUG: Returning None for {matfile}")
    return None


# Carregar dados
def load_results(folder, algoritmo, metric="IGD", objective_suffix_filters=None):
    results = []
    for fname in os.listdir(folder):
        if fname.endswith(".mat"):
            # Filter by objective suffix if specified
            if objective_suffix_filters:
                if not any(suffix in fname for suffix in objective_suffix_filters):
                    continue

            problem = get_problem(fname)  # This will now return e.g., DTLZ1_M2
            values = extract_metric(os.path.join(folder, fname), metric)
            objective_count = get_objective_count(fname)

            if values is not None:
                # Garante que values é 1D
                values = np.array(values).flatten()
                for v in values:
                    # Só adiciona se for escalar
                    if np.isscalar(v):
                        print(
                            f"Arquivo: {fname}, Problem: {problem}, Objetivos: {objective_count}, Valor: {v}, Tipo: {type(v)}"
                        )
                        results.append(
                            {
                                "Algoritmo": algoritmo,
                                "Problema": problem,
                                "Valor": float(v),
                                "Objetivos": objective_count,
                            }
                        )
    return results


# Função para adicionar grupo de benchmark
def add_benchmark_group(df):
    # Função para extrair o grupo de benchmark
    def get_benchmark_group(problem):
        if problem.startswith("ZDT"):
            return "ZDT"
        elif problem.startswith("DTLZ"):
            return "DTLZ"
        elif problem.startswith("WFG"):
            return "WFG"
        elif problem.startswith("MaF"):
            return "MaF"
        else:
            return "Unknown"

    # Adicionar coluna de grupo e numero do problema
    df["Grupo"] = df["Problema"].apply(get_benchmark_group)
    df["Numero"] = df["Problema"].str.extract(r"(\d+)").astype(int)

    # Ordenar o DataFrame
    return df.sort_values(["Grupo", "Numero"])


# Juntar dados de todas as pastas
all_data = []
for alg in algorithms:
    dados_alg = load_results(
        algorithm_paths[alg], alg, metric="IGD", objective_suffix_filters=["M2", "M3"]
    )
    all_data.extend(dados_alg)
df = pd.DataFrame(all_data)

# Adicionar informação de grupo para ordenação
df = add_benchmark_group(df)

print("Tamanho do DataFrame:", len(df))
print("Colunas do DataFrame:", df.columns)
print("Primeiras linhas do DataFrame:")
print(df.head(10))

# Contar ocorrências de cada problema por algoritmo
problemas_count = df.groupby(["Problema", "Algoritmo"]).size().unstack(fill_value=0)
print("\nContagem de problemas por algoritmo:")
print(problemas_count)

# Filtrar apenas problemas que estão presentes em todos os algoritmos
problemas_comuns = set.intersection(
    *[set(df[df["Algoritmo"] == alg]["Problema"]) for alg in algorithms]
)
df_filtered = df[df["Problema"].isin(problemas_comuns)]

print("\nProblemas comuns a todos os algoritmos:", sorted(list(problemas_comuns)))

# Normalizar os valores por problema (para que a comparação seja mais justa)
df_normalized = df_filtered.copy()

# Aplicamos a normalização min-max para cada problema
for problema in problemas_comuns:
    problema_mask = df_normalized["Problema"] == problema
    min_val = df_normalized.loc[problema_mask, "Valor"].min()
    max_val = df_normalized.loc[problema_mask, "Valor"].max()

    # Evitar divisão por zero
    if max_val == min_val:
        df_normalized.loc[problema_mask, "Valor_Normalizado"] = 1.0
    else:
        df_normalized.loc[problema_mask, "Valor_Normalizado"] = (
            df_normalized.loc[problema_mask, "Valor"] - min_val
        ) / (max_val - min_val)

# Calcular estatísticas para cada problema e algoritmo
estatisticas = (
    df_filtered.groupby(["Problema", "Algoritmo"])["Valor"]
    .agg(["mean", "std", "min", "max"])
    .reset_index()
)

# Pivot para obter as médias por algoritmo lado a lado
pivot_mean = estatisticas.pivot(index="Problema", columns="Algoritmo", values="mean")
pivot_std = estatisticas.pivot(index="Problema", columns="Algoritmo", values="std")

# Criar subconjuntos para cada família de problemas
problemas_dtlz = [p for p in problemas_comuns if "DTLZ" in p]
problemas_wfg = [p for p in problemas_comuns if "WFG" in p]
problemas_zdt = [p for p in problemas_comuns if "ZDT" in p]
problemas_maf = [p for p in problemas_comuns if "MaF" in p]

# Ordenar cada lista de problemas por número
problemas_dtlz.sort(key=lambda x: int(re.search(r"\d+", x).group()))
problemas_wfg.sort(key=lambda x: int(re.search(r"\d+", x).group()))
problemas_zdt.sort(key=lambda x: int(re.search(r"\d+", x).group()))
problemas_maf.sort(key=lambda x: int(re.search(r"\d+", x).group()))

# Juntar todas as listas na ordem desejada
problema_order = problemas_dtlz + problemas_wfg + problemas_zdt + problemas_maf

# 1. Gráfico de barras com erro para comparação direta entre algoritmos
plt.figure(figsize=(20, 10))
x = np.arange(len(problema_order))
width = 0.15  # Ajustado para acomodar mais algoritmos

# Preparar dados para o gráfico de barras
valores_por_algoritmo = {
    alg: [pivot_mean.loc[p, alg] for p in problema_order] for alg in algorithms
}
erros_por_algoritmo = {
    alg: [pivot_std.loc[p, alg] for p in problema_order] for alg in algorithms
}

ax = plt.subplot(111)
for i, alg in enumerate(algorithms):
    offset = (i - len(algorithms) / 2 + 0.5) * width
    ax.bar(
        x + offset,
        valores_por_algoritmo[alg],
        width,
        label=alg,
        yerr=erros_por_algoritmo[alg],
        capsize=4,
    )

# Adicionar linhas verticais para separar as famílias de problemas
familia_indices = [
    len(problemas_dtlz),
    len(problemas_dtlz) + len(problemas_wfg),
    len(problemas_dtlz) + len(problemas_wfg) + len(problemas_zdt),
]
for idx in familia_indices:
    plt.axvline(x=idx - 0.5, color="gray", linestyle="--", alpha=0.5)

# Adicionar rótulos de família
familia_positions = [
    len(problemas_dtlz) / 2,
    len(problemas_dtlz) + len(problemas_wfg) / 2,
    len(problemas_dtlz) + len(problemas_wfg) + len(problemas_zdt) / 2,
    len(problemas_dtlz)
    + len(problemas_wfg)
    + len(problemas_zdt)
    + len(problemas_maf) / 2,
]
familia_labels = ["DTLZ", "WFG", "ZDT", "MaF"]
for pos, label in zip(familia_positions, familia_labels):
    plt.text(
        pos, ax.get_ylim()[1] * 1.01, label, ha="center", fontweight="bold", fontsize=14
    )

# Adicionar rótulos e legendas
ax.set_ylabel("IGD (menor é melhor)")
ax.set_xticks(x)
ax.set_xticklabels(problema_order, rotation=45)
ax.set_title("Comparação dos valores de IGD por Problema e Algoritmo")
ax.legend()

# Ajustar layout
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "comparacao_barra_erros.png"), dpi=300)
plt.close()

# 2. Gráfico de violino para comparação por família
plt.figure(figsize=(20, 10))
ax = sns.violinplot(
    data=df_filtered,
    x="Problema",
    y="Valor",
    hue="Algoritmo",
    order=problema_order,
    scale="width",
    split=True,
    inner="quart",
)
ax.set_yscale("log")
plt.title("Comparação dos Algoritmos por Problema (IGD) - Gráfico de Violino")
plt.xlabel("Problema")
plt.ylabel("IGD (menor é melhor)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "comparacao_violino.png"), dpi=300)
plt.close()

# 3. Dashboard comparativo
fig, axes = plt.subplots(2, 2, figsize=(20, 15))
axes = axes.flatten()

# Para cada família, criar um boxplot
familia_dados = [
    (
        df_filtered[df_filtered["Problema"].isin(problemas_dtlz)],
        problemas_dtlz,
        "DTLZ",
        axes[0],
    ),
    (
        df_filtered[df_filtered["Problema"].isin(problemas_wfg)],
        problemas_wfg,
        "WFG",
        axes[1],
    ),
    (
        df_filtered[df_filtered["Problema"].isin(problemas_zdt)],
        problemas_zdt,
        "ZDT",
        axes[2],
    ),
    (
        df_filtered[df_filtered["Problema"].isin(problemas_maf)],
        problemas_maf,
        "MaF",
        axes[3],
    ),
]

for dados, ordem, titulo, ax in familia_dados:
    sns.boxplot(
        data=dados,
        x="Problema",
        y="Valor",
        hue="Algoritmo",
        order=ordem,
        ax=ax,
        showfliers=False,
    )
    ax.set_title(f"Problemas {titulo}")
    ax.set_yscale("log")
    ax.set_xlabel("Problema")
    ax.set_ylabel("IGD (menor é melhor)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

plt.suptitle("Dashboard Comparativo por Família de Problemas", fontsize=16)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "dashboard_comparativo.png"), dpi=300)
plt.close()

# 4. Heatmap de comparação entre algoritmos
# Calcular a média de IGD para cada algoritmo em cada problema
heatmap_data = df_filtered.groupby(["Problema", "Algoritmo"])["Valor"].mean().unstack()

# Normalizar os valores para cada problema
for problema in heatmap_data.index:
    min_val = heatmap_data.loc[problema].min()
    max_val = heatmap_data.loc[problema].max()
    if max_val != min_val:
        heatmap_data.loc[problema] = (heatmap_data.loc[problema] - min_val) / (
            max_val - min_val
        )

plt.figure(figsize=(15, 10))
sns.heatmap(heatmap_data, annot=True, cmap="RdYlGn_r", fmt=".2f", linewidths=0.5)
plt.title("Comparação Normalizada entre Algoritmos (menor é melhor)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "heatmap_comparacao.png"), dpi=300)
plt.close()

# Exportar estatísticas
estatisticas_completas = (
    df_filtered.groupby(["Grupo", "Problema", "Algoritmo"])["Valor"]
    .agg(["mean", "std", "min", "max"])
    .reset_index()
)
estatisticas_completas.to_csv(
    os.path.join(processed_data_dir, "estatisticas_comparacao.csv"), index=False
)

# Exportar valores de IGD por run
igd_per_run_df = df_filtered[
    ["Grupo", "Problema", "Numero", "Algoritmo", "Objetivos", "Valor"]
].copy()
igd_per_run_df = igd_per_run_df.sort_values(
    by=["Grupo", "Numero", "Problema", "Algoritmo", "Valor"]
).reset_index(drop=True)
igd_per_run_df.rename(columns={"Valor": "IGD"}, inplace=True)
igd_per_run_df.to_csv(
    os.path.join(processed_data_dir, "igd_values_per_run.csv"), index=False
)

print("\nGráficos gerados:")
print(
    "1. comparacao_barra_erros.png: Gráfico de barras com barras de erro para comparação direta"
)
print("2. comparacao_violino.png: Gráfico de violino para comparação por família")
print("3. dashboard_comparativo.png: Dashboard comparativo por família de problemas")
print(
    "4. heatmap_comparacao.png: Mapa de calor mostrando comparação normalizada entre algoritmos"
)
print("\nArquivos de dados exportados:")
print(
    "1. estatisticas_comparacao.csv: Estatísticas detalhadas por problema e algoritmo"
)
print("2. igd_values_per_run.csv: Valores de IGD de cada execução")
