import pandas as pd
import matplotlib.pyplot as plt

# Nome do arquivo CSV
csv_filename = "historico_populacao.csv"

# Carregar os dados do CSV
df = pd.read_csv(csv_filename)

# Filtrar apenas a terceira geração do hospedeiro e primeiro ciclo do IVF
df_filtrado = df[(df["Geracao_Anfitriao"] == 3) & (df["SubGeracao_IVF"] == 1)].copy()

# Verificar os valores únicos na coluna "Tag"
print("Valores únicos na coluna 'Tag':", df_filtrado["Tag"].unique())

# Substituir NaN por 'desconhecido'
df_filtrado.loc[:, "Tag"] = df_filtrado["Tag"].fillna("desconhecido")

# Garantir que todos os valores na coluna "Tag" sejam strings
df_filtrado.loc[:, "Tag"] = df_filtrado["Tag"].astype(str)

# Normalizar as tags: remover espaços e converter para minúsculas
df_filtrado.loc[:, "Tag"] = df_filtrado["Tag"].str.strip().str.lower()

# Definir cores para cada tipo de indivíduo
cores = {
    "mae": "blue",
    "filho": "green",
    "anfitriao": "black",
    "desconhecido": "gray",
    "pai": "red",
}

# Criar lista de cores para os pontos
cores_pontos = [cores.get(tag, "gray") for tag in df_filtrado["Tag"]]

# Definir o tamanho dos pontos (maiores para 'pai', 'mae', 'filho')
tamanhos_pontos = [150 if tag == "pai" else 100 if tag in ["filho", "mae"] else 40 for tag in df_filtrado["Tag"]]

# Pegar os dois primeiros objetivos para plotar
x = df_filtrado["Objetivo_1"]
y = df_filtrado["Objetivo_2"]

# Criar o gráfico
plt.figure(figsize=(8, 6))

# Plotando todos os pontos normalmente
plt.scatter(x, y, c=cores_pontos, s=tamanhos_pontos, alpha=0.7, edgecolors="k")

# Destacar os pontos 'pai' com quadrados
plt.scatter(x[df_filtrado["Tag"] == "pai"], y[df_filtrado["Tag"] == "pai"],
            c="red", s=150, marker='s', label="Pai", alpha=0.7, edgecolors="k", zorder=3)

# Adicionar legendas para cada tipo de indivíduo
for tag, cor in cores.items():
    if tag in df_filtrado["Tag"].values:
        plt.scatter([], [], c=cor, s=100, label=tag)

# Configuração do gráfico
plt.xlabel("Objetivo 1")
plt.ylabel("Objetivo 2")
plt.title("Distribuição dos Indivíduos (Geração 3, Ciclo 1)")
plt.legend()
plt.grid(True)

# Mostrar o gráfico
plt.show()
