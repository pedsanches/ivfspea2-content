import pandas as pd
import matplotlib.pyplot as plt
import imageio
import os

# Nome do arquivo CSV
csv_filename = "Top10_Individuos.csv"

# Carregar os dados do CSV
df = pd.read_csv(csv_filename)

# Remover espaços e garantir que o fitness é numérico
df["Fitness"] = pd.to_numeric(df["Fitness"], errors='coerce')

# Filtrar as gerações únicas
geracoes = df["SPEA2_Gen"].unique()

# Definir as cores com base no fitness
cores = {
    "melhor": "red",     # Menor fitness
    "segundo_melhor": "orange",  # Segundo menor fitness
    "terceiro_melhor": "yellow",  # Terceiro melhor fitness
    "outros": "gray",    # Os outros são cinza
}

# Função para calcular os tamanhos dos pontos (opcional, mas pode ser ajustado conforme a necessidade)
def calcular_tamanhos_pontos():
    return 100  # Todos os pontos terão o mesmo tamanho neste caso

# Calcular os limites fixos de X e Y com base em todos os dados
x_min = df["obj1"].min() - 0.2
x_max = df["obj1"].max() + 0.2
y_min = df["obj2"].min() - 0.2
y_max = df["obj2"].max() + 0.2

# Lista para armazenar os frames para o GIF
imagens_frames = []

# Loop sobre as gerações
for geracao in geracoes:
    # Filtrar os dados para a geração atual
    df_geracao = df[df["SPEA2_Gen"] == geracao]
    
    # Ordenar pelo Fitness (menor fitness primeiro)
    df_geracao = df_geracao.sort_values(by="Fitness", ascending=True)
    
    # Selecionar os 10 melhores indivíduos
    df_10_melhores = df_geracao.head(10)

    # Determinar as cores dos indivíduos com base no fitness
    cores_individuos = []
    
    # Atribuir cores de acordo com a posição na classificação do fitness
    for i, row in df_10_melhores.iterrows():
        if i == df_10_melhores.index[0]:  # Menor fitness
            cores_individuos.append(cores["melhor"])
        elif i == df_10_melhores.index[1]:  # Segundo menor fitness
            cores_individuos.append(cores["segundo_melhor"])
        elif i == df_10_melhores.index[2]:  # Terceiro menor fitness
            cores_individuos.append(cores["terceiro_melhor"])
        else:  # O restante é cinza
            cores_individuos.append(cores["outros"])

    # Criar o gráfico
    plt.figure(figsize=(8, 6))

    # Plotar primeiro os "outros" (com o fitness maior) para ficar atrás
    plt.scatter(df_10_melhores["obj1"][df_10_melhores["Fitness"] > df_10_melhores["Fitness"].iloc[2]], 
                df_10_melhores["obj2"][df_10_melhores["Fitness"] > df_10_melhores["Fitness"].iloc[2]], 
                c=cores["outros"], s=calcular_tamanhos_pontos(), alpha=0.7, edgecolors="k")

    # Plotar o terceiro melhor (fitness)
    plt.scatter(df_10_melhores["obj1"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[2]], 
                df_10_melhores["obj2"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[2]], 
                c=cores["terceiro_melhor"], s=calcular_tamanhos_pontos(), alpha=0.7, edgecolors="k")

    # Plotar o segundo melhor (fitness)
    plt.scatter(df_10_melhores["obj1"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[1]], 
                df_10_melhores["obj2"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[1]], 
                c=cores["segundo_melhor"], s=calcular_tamanhos_pontos(), alpha=0.7, edgecolors="k")

    # Plotar o melhor (fitness)
    plt.scatter(df_10_melhores["obj1"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[0]], 
                df_10_melhores["obj2"][df_10_melhores["Fitness"] == df_10_melhores["Fitness"].iloc[0]], 
                c=cores["melhor"], s=calcular_tamanhos_pontos(), alpha=0.7, edgecolors="k")
    
    # Adicionar legendas
    plt.scatter([], [], c=cores["melhor"], s=100, label="Menor Fitness")
    plt.scatter([], [], c=cores["segundo_melhor"], s=100, label="Segundo Menor Fitness")
    plt.scatter([], [], c=cores["terceiro_melhor"], s=100, label="Terceiro Menor Fitness")
    plt.scatter([], [], c=cores["outros"], s=100, label="Outros")

    # Configuração do gráfico
    plt.xlabel("Objetivo 1 (obj1)")
    plt.ylabel("Objetivo 2 (obj2)")
    plt.title(f"Distribuição das 10 Soluções (Geração {geracao})")
    plt.legend()
    plt.grid(True)
    
    # Ajustar os limites dos eixos para garantir consistência entre as gerações
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    # Salvar o gráfico como imagem
    imagem_filename = f"frame_geracao_{geracao}.png"
    plt.savefig(imagem_filename)
    imagens_frames.append(imagem_filename)
    plt.close()

# Criar o GIF a partir das imagens geradas
gif_filename = "animacao_geracoes.gif"
with imageio.get_writer(gif_filename, mode='I', duration=700, loop=0) as writer:  # Duração de 1 segundo por frame
    for imagem in imagens_frames:
        imagem_frame = imageio.imread(imagem)
        writer.append_data(imagem_frame)

# Remover os arquivos temporários das imagens geradas
for imagem in imagens_frames:
    os.remove(imagem)

print(f"GIF gerado com sucesso: {gif_filename}")
