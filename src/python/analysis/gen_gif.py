import pandas as pd
import matplotlib.pyplot as plt
import imageio

# Nome do arquivo CSV
csv_filename = "historico_populacao.csv"

# Carregar os dados do CSV
df = pd.read_csv(csv_filename)

# Filtrar apenas a terceira geração do hospedeiro
df_filtrado = df[df["Geracao_Anfitriao"] == 220].copy()

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
    "filho_mae_mutada": "orange",
    "anfitriao": "black",
    "desconhecido": "gray",
    # "pai": "red",
}

# Gerar a lista de tamanhos de pontos, agora corretamente associada ao tamanho dos dados
def calcular_tamanhos_pontos(tags):
    return [100 if tag in ["filho", "mae", "filho_mae_mutada"] else 15 for tag in tags]

# Preparar a lista para armazenar as imagens
imagens_frames = []

# Gerar o gráfico para cada SubGeracao_IVF
subgeracoes = df_filtrado["SubGeracao_IVF"].unique()

# Encontrar os limites dos eixos para garantir a mesma escala
x_min = df_filtrado["Objetivo_1"].min()
x_max = df_filtrado["Objetivo_1"].max()
y_min = df_filtrado["Objetivo_2"].min()
y_max = df_filtrado["Objetivo_2"].max()

for subgeracao in subgeracoes:
    # Filtrar dados para a SubGeracao_IVF atual
    df_subgeracao = df_filtrado[df_filtrado["SubGeracao_IVF"] == subgeracao]
    
    # Obter os tamanhos de pontos para a subgeração atual
    tamanhos_pontos = calcular_tamanhos_pontos(df_subgeracao["Tag"])
    
    # Criar o gráfico
    plt.figure(figsize=(8, 6))
    plt.scatter(df_subgeracao["Objetivo_1"], df_subgeracao["Objetivo_2"], 
                c=[cores.get(tag, "gray") for tag in df_subgeracao["Tag"]],
                s=tamanhos_pontos, alpha=0.7, edgecolors="k")
    
    # Destacar os pontos 'pai' com quadrados
    plt.scatter(df_subgeracao[df_subgeracao["Tag"] == "pai"]["Objetivo_1"], 
                df_subgeracao[df_subgeracao["Tag"] == "pai"]["Objetivo_2"], 
                c="red", s=150, label="Pai", alpha=1, edgecolors="k", zorder=3)
    
    # Adicionar legendas para cada tipo de indivíduo
    for tag, cor in cores.items():
        if tag in df_subgeracao["Tag"].values:
            plt.scatter([], [], c=cor, s=100, label=tag)
    
    # Configuração do gráfico
    plt.xlabel("Objetivo 1")
    plt.ylabel("Objetivo 2")
    plt.title(f"Distribuição dos Indivíduos (Geração 5, SubGeração IVF {subgeracao})")
    plt.legend()
    plt.grid(True)
    
    # Ajustar os limites dos eixos para garantir que todos os gráficos tenham a mesma escala
    plt.xlim(x_min - 0.2, x_max + 0.2)
    plt.ylim(y_min - 0.2, y_max + 0.2)
    
    # Salvar o gráfico atual como imagem
    imagem_filename = f"frame_{subgeracao}.png"
    plt.savefig(imagem_filename)
    imagens_frames.append(imagem_filename)
    plt.close()

# Criar o GIF a partir das imagens geradas
gif_filename = "animacao_subgeracoes.gif"
with imageio.get_writer(gif_filename, mode='I', duration=1000, loop=0) as writer:  # Duração aumentada para 2 segundos
    for imagem in imagens_frames:
        imagem_frame = imageio.imread(imagem)
        writer.append_data(imagem_frame)

# Remover os arquivos temporários das imagens geradas
import os
for imagem in imagens_frames:
    os.remove(imagem)

print(f"GIF gerado com sucesso: {gif_filename}")
