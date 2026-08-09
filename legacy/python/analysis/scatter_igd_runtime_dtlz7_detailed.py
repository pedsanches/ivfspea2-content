import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from matplotlib.patches import Ellipse
import os

# Configurar matplotlib para não usar backend interativo
plt.ioff()

# Configurar estilo do matplotlib
plt.style.use("default")
sns.set_palette("husl")

# Carregar os dados
print("Carregando dados...")
base_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(
    base_dir, "../../../data/processed/todas_metricas_consolidado.csv"
)
output_dir = os.path.join(base_dir, "../../../results/figures")

df = pd.read_csv(data_file)

PROBLEMA = "WFG7"  # Defina aqui o problema a ser analisado
N_OBJ = "M3"

# Filtrar apenas dados do problema definido com 3 objetivos (M3)
print(f"Filtrando dados do {PROBLEMA} com 3 objetivos...")
dtlz_data = df[(df["Problema"] == PROBLEMA) & (df["M"] == N_OBJ)].copy()

# Verificar se há dados
if dtlz_data.empty:
    print(f"Nenhum dado encontrado para {PROBLEMA} com 3 objetivos!")
    exit()

print(f"Dados encontrados: {len(dtlz_data)} registros")
print(f"Algoritmos disponíveis: {dtlz_data['Algoritmo'].unique()}")

# Converter runtime para numérico (remover possíveis valores vazios)
dtlz_data["runtime"] = pd.to_numeric(dtlz_data["runtime"], errors="coerce")
dtlz_data["IGD"] = pd.to_numeric(dtlz_data["IGD"], errors="coerce")

# Remover linhas com valores NaN
dtlz_data = dtlz_data.dropna(subset=["runtime", "IGD"])

print(f"Dados válidos após limpeza: {len(dtlz_data)} registros")

# Criar figura com subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Lista de cores para os algoritmos
colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]

# Plot 1: Gráfico de dispersão com elipses de confiança
algoritmos = dtlz_data["Algoritmo"].unique()

for i, algoritmo in enumerate(algoritmos):
    dados_algoritmo = dtlz_data[dtlz_data["Algoritmo"] == algoritmo]

    # Plotar pontos
    ax1.scatter(
        dados_algoritmo["runtime"],
        dados_algoritmo["IGD"],
        label=algoritmo,
        color=colors[i % len(colors)],
        alpha=0.7,
        s=60,
        edgecolors="black",
        linewidth=0.5,
    )

    # Calcular elipse de confiança (95%)
    if len(dados_algoritmo) > 2:
        cov = np.cov(dados_algoritmo["runtime"], dados_algoritmo["IGD"])
        eigenvals, eigenvecs = np.linalg.eig(cov)
        angle = np.degrees(np.arctan2(eigenvecs[1, 0], eigenvecs[0, 0]))
        center = (dados_algoritmo["runtime"].mean(), dados_algoritmo["IGD"].mean())
        chi2_val = stats.chi2.ppf(0.95, 2)
        width = 2 * np.sqrt(chi2_val * eigenvals[0])
        height = 2 * np.sqrt(chi2_val * eigenvals[1])
        ellipse = Ellipse(
            center,
            width,
            height,
            angle=angle,
            fill=False,
            color=colors[i % len(colors)],
            linewidth=2,
            alpha=0.8,
        )
        ax1.add_patch(ellipse)

ax1.set_xlabel("Runtime (segundos)", fontsize=12)
ax1.set_ylabel("IGD (Inverted Generational Distance)", fontsize=12)
ax1.set_title(
    f"Gráfico de Dispersão com Elipses de Confiança (95%)\nProblema {PROBLEMA} - 3 Objetivos",
    fontsize=14,
    fontweight="bold",
)
ax1.grid(True, alpha=0.3)
ax1.legend(title="Algoritmo", bbox_to_anchor=(1.05, 1), loc="upper left")

boxplot_data = []
boxplot_labels = []
for algoritmo in algoritmos:
    dados_algoritmo = dtlz_data[dtlz_data["Algoritmo"] == algoritmo]
    boxplot_data.append(dados_algoritmo["IGD"].values)
    boxplot_labels.append(algoritmo)
bp = ax2.boxplot(boxplot_data, labels=boxplot_labels, patch_artist=True)
for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.set_ylabel("IGD", fontsize=12)
ax2.set_title(
    f"Distribuição de IGD por Algoritmo\nProblema {PROBLEMA} - 3 Objetivos",
    fontsize=14,
    fontweight="bold",
)
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig(
    os.path.join(output_dir, f"scatter_igd_runtime_{PROBLEMA.lower()}_detailed.png"),
    dpi=300,
    bbox_inches="tight",
)
print(
    f"Gráfico detalhado salvo como 'scatter_igd_runtime_{PROBLEMA.lower()}_detailed.png'"
)

print("\n=== ANÁLISE ESTATÍSTICA DETALHADA ===")
print("Algoritmo\t\tMédia IGD\tStd IGD\tMédia Runtime\tStd Runtime\tRuns")
print("-" * 80)
for algoritmo in algoritmos:
    dados_algoritmo = dtlz_data[dtlz_data["Algoritmo"] == algoritmo]
    print(
        f"{algoritmo:<15}\t{dados_algoritmo['IGD'].mean():.6f}\t{dados_algoritmo['IGD'].std():.6f}\t"
        f"{dados_algoritmo['runtime'].mean():.2f}s\t\t{dados_algoritmo['runtime'].std():.2f}s\t\t{len(dados_algoritmo)}"
    )
igd_groups = [
    dtlz_data[dtlz_data["Algoritmo"] == alg]["IGD"].values for alg in algoritmos
]
h_stat, p_value = stats.kruskal(*igd_groups)
print("\n=== TESTE DE SIGNIFICÂNCIA ESTATÍSTICA ===")
print(f"Teste Kruskal-Wallis para IGD:")
print(f"H-statistic: {h_stat:.4f}")
print(f"p-value: {p_value:.6f}")
print(
    f"Diferenças são {'estatisticamente significativas' if p_value < 0.05 else 'não significativas'} (α=0.05)"
)
print("\n=== ANÁLISE DE CORRELAÇÃO ===")
correlation = dtlz_data["IGD"].corr(dtlz_data["runtime"])
print(f"Correlação entre IGD e Runtime: {correlation:.4f}")
print(
    f"Interpretação: {'Forte' if abs(correlation) > 0.7 else 'Moderada' if abs(correlation) > 0.3 else 'Fraca'} correlação"
)
print("\nAnálise detalhada concluída!")
