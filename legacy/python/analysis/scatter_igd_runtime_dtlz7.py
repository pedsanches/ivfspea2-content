import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

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

PROBLEMA = "DTLZ7"  # Defina aqui o problema a ser analisado

# Filtrar apenas dados do problema definido com 3 objetivos (M3)
print(f"Filtrando dados do {PROBLEMA} com 3 objetivos...")
dtlz_data = df[(df["Problema"] == PROBLEMA) & (df["M"] == "M3")].copy()

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

# Criar o gráfico de dispersão
plt.figure(figsize=(12, 8))

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

# Plotar cada algoritmo com cor diferente
algoritmos = dtlz_data["Algoritmo"].unique()
for i, algoritmo in enumerate(algoritmos):
    dados_algoritmo = dtlz_data[dtlz_data["Algoritmo"] == algoritmo]

    plt.scatter(
        dados_algoritmo["runtime"],
        dados_algoritmo["IGD"],
        label=algoritmo,
        color=colors[i % len(colors)],
        alpha=0.7,
        s=50,
        edgecolors="black",
        linewidth=0.5,
    )

# Configurar o gráfico
plt.xlabel("Runtime (segundos)", fontsize=12)
plt.ylabel("IGD", fontsize=12)
plt.title(
    f"Gráfico de Dispersão: IGD vs Runtime\nProblema {PROBLEMA} - 3 Objetivos",
    fontsize=14,
    fontweight="bold",
)

# Adicionar grade
plt.grid(True, alpha=0.3)

# Adicionar legenda
plt.legend(title="Algoritmo", bbox_to_anchor=(1.05, 1), loc="upper left")

# Ajustar layout para não cortar a legenda
plt.tight_layout()

# Salvar o gráfico
plt.savefig(
    os.path.join(output_dir, f"scatter_igd_runtime_{PROBLEMA.lower()}.png"),
    dpi=300,
    bbox_inches="tight",
)
print(f"Gráfico salvo como 'scatter_igd_runtime_{PROBLEMA.lower()}.png'")

# Mostrar estatísticas resumidas
print("\n=== ESTATÍSTICAS RESUMIDAS ===")
for algoritmo in algoritmos:
    dados_algoritmo = dtlz_data[dtlz_data["Algoritmo"] == algoritmo]
    print(f"\n{algoritmo}:")
    print(f"  Média IGD: {dados_algoritmo['IGD'].mean():.6f}")
    print(f"  Média Runtime: {dados_algoritmo['runtime'].mean():.2f} segundos")
    print(f"  Número de runs: {len(dados_algoritmo)}")

# Mostrar o gráfico
plt.show()
