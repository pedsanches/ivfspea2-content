import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os # Adicionado para manipulação de diretórios

# Ignorar avisos futuros do Seaborn (opcional, para limpar a saída)
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configurações ---
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, '../../../data/processed')
results_dir = os.path.join(base_dir, '../../../results/figures')

file_path = os.path.join(data_dir, 'igd_values_per_run.csv')
igd_threshold = 0.1 # Limiar para considerar um valor como outlier extremo a ser removido
output_plot_directory = os.path.join(results_dir, 'plots_igd') # Diretório para salvar os gráficos
output_image_prefix = 'boxplot_igd' # Prefixo para os nomes dos arquivos de imagem
save_plots = True # Definir como True para salvar os gráficos em arquivos
output_formats = ['pdf', 'png'] # Lista de formatos de saída para os gráficos

# --- Criar diretório de saída se não existir ---
if save_plots and not os.path.exists(output_plot_directory):
    try:
        os.makedirs(output_plot_directory)
        print(f"Diretório '{output_plot_directory}' criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar o diretório '{output_plot_directory}': {e}")
        save_plots = False # Desabilitar salvamento se não puder criar o diretório

# --- Carregar Dados ---
try:
    df_full = pd.read_csv(file_path) # Renomeado para df_full
    print(f"Dados carregados com sucesso de '{file_path}'.")
except FileNotFoundError:
    print(f"Erro: Arquivo '{file_path}' não encontrado.")
    exit()
except Exception as e:
    print(f"Erro ao carregar o arquivo CSV: {e}")
    exit()

# --- Tratamento de Outliers ---
original_rows = len(df_full)
# Filtrar valores de IGD acima do limiar
df_filtered_all_objectives = df_full[df_full['IGD'] <= igd_threshold].copy() # Usar .copy()
removed_rows = original_rows - len(df_filtered_all_objectives)

print(f"\n--- Tratamento de Outliers (Geral) ---")
print(f"Linhas originais: {original_rows}")
print(f"Linhas após filtrar IGD <= {igd_threshold}: {len(df_filtered_all_objectives)}")
print(f"Linhas removidas (potenciais outliers): {removed_rows}")

# Salvar os dados filtrados em um CSV (todos os objetivos juntos antes de separar)
filtered_data_filename = os.path.join(output_plot_directory, 'filtered_igd_data_all_objectives.csv')
try:
    df_filtered_all_objectives.to_csv(filtered_data_filename, index=False)
    print(f"\nDados filtrados (todos objetivos) salvos em '{filtered_data_filename}'")
except Exception as e:
    print(f"\nErro ao salvar os dados filtrados: {e}")

# --- Função para Geração dos Boxplots por Grupo de Objetivos ---
def generate_boxplots_for_objective_group(df_group, objective_label, output_dir, base_img_prefix, igd_val_threshold, save_flag, formats_list):
    sns.set_theme(style="whitegrid")

    if df_group.empty:
        print(f"\nNenhum dado para plotar para o grupo de objetivos: {objective_label}.")
        return

    all_problems = sorted(df_group['Problema'].unique())
    num_problems = len(all_problems)

    if num_problems == 0:
        print(f"Nenhum problema para plotar no grupo {objective_label} após a filtragem.")
        return
    
    print(f"\nGerando gráficos para {objective_label} - Problemas: {', '.join(all_problems)}...")

    ncols = 2
    nrows = (num_problems + ncols - 1) // ncols
    fig_width = 20
    fig_height_per_row = 6
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_width, nrows * fig_height_per_row), squeeze=False, sharey=False)
    axes = axes.flatten()

    for i, problem_name in enumerate(all_problems):
        ax = axes[i]
        
        # --- New logic to get display name ---
        display_problem_name = problem_name
        suffix_to_remove = f"_{objective_label}" # e.g., "_M2"
        if problem_name.endswith(suffix_to_remove):
            display_problem_name = problem_name[:-len(suffix_to_remove)]
        # --- End new logic ---

        # Filtrar o DataFrame do grupo de objetivos para o problema atual e ordenar
        problem_df_group = df_group[df_group['Problema'] == problem_name].sort_values(by=['Algoritmo'])

        if problem_df_group.empty:
            ax.set_title(f'{display_problem_name} (Sem dados)', fontsize=14)
            ax.axis('off')
            continue

        sns.boxplot(
            ax=ax,
            data=problem_df_group,
            x='Algoritmo',
            y='IGD',
            hue='Algoritmo',
            palette='viridis',
            showfliers=True,
            linewidth=1.2,
            flierprops=dict(marker='o', markersize=4, markerfacecolor='gray', alpha=0.6),
            dodge=False
        )

        ax.set_title(f'{display_problem_name}', fontsize=16)
        
        ax.set_xlabel(None)
        ax.set_ylabel('IGD', fontsize=12)
        ax.tick_params(axis='x', labelrotation=45, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    for j in range(num_problems, nrows * ncols):
        fig.delaxes(axes[j])

    # Tentativa de obter handles e labels da primeira subplot válida que tenha legenda.
    first_valid_ax_for_legend = None
    for ax_idx in range(num_problems):
        # Verificar se o DataFrame para este subplot não estava vazio
        problem_name_for_legend = all_problems[ax_idx] 
        if not df_group[df_group['Problema'] == problem_name_for_legend].empty:
            first_valid_ax_for_legend = axes[ax_idx]
            break

    if first_valid_ax_for_legend and first_valid_ax_for_legend.get_legend_handles_labels()[0]:
        handles, labels = first_valid_ax_for_legend.get_legend_handles_labels()
        unique_labels_dict = dict(zip(labels, handles)) # Use dict to keep unique labels and corresponding handles
        fig.legend(unique_labels_dict.values(), unique_labels_dict.keys(), title='Algoritmo', fontsize=10, title_fontsize=11, 
                   loc='upper right', bbox_to_anchor=(0.98, 0.97))

    fig.suptitle(f'Distribuição IGD por Problema ({objective_label})\n(Execuções com IGD > {igd_val_threshold} removidas)', 
                 fontsize=20, y=0.99)
    plt.tight_layout(rect=[0, 0, 0.9, 0.96])

    if save_flag:
        for output_format in formats_list:
            output_filename = os.path.join(output_dir, f"{base_img_prefix}_{objective_label}_all_problems.{output_format}")
            try:
                plt.savefig(output_filename, dpi=300, bbox_inches='tight')
                print(f"Gráfico para {objective_label} salvo como '{output_filename}'")
            except Exception as e:
                print(f"Erro ao salvar o gráfico para {objective_label} no formato {output_format}: {e}")
    
    plt.show() # Mostrar o gráfico após salvar

# --- Separar Dados por Objetivos (M2, M3, etc.) e Gerar Gráficos ---
# Assume que a coluna 'Objetivos' existe e contém 'M2', 'M3', etc.
if 'Objetivos' not in df_filtered_all_objectives.columns:
    print("Erro: A coluna 'Objetivos' não foi encontrada no CSV. Não é possível separar por M2/M3.")
    # Se não houver coluna 'Objetivos', podemos tentar plotar tudo junto como antes,
    # ou adaptar para extrair M2/M3 do nome do problema se estiver lá.
    # Por enquanto, vamos encerrar se a coluna 'Objetivos' não existir.
    if not df_filtered_all_objectives.empty:
         print("Tentando plotar todos os dados juntos como um único grupo (sem separação M2/M3).")
         generate_boxplots_for_objective_group(df_filtered_all_objectives, "TodosObjetivos", output_plot_directory, output_image_prefix, igd_threshold, save_plots, output_formats)
    else:
        print("Nenhum dado para plotar.")
else:
    objective_groups = df_filtered_all_objectives['Objetivos'].unique()
    print(f"\nGrupos de objetivos encontrados: {', '.join(objective_groups)}")

    for obj_group_label in sorted(objective_groups): # Ordenar para M2 antes de M3, etc.
        df_current_objective_group = df_filtered_all_objectives[df_filtered_all_objectives['Objetivos'] == obj_group_label].copy()
        if not df_current_objective_group.empty:
            generate_boxplots_for_objective_group(
                df_current_objective_group, 
                obj_group_label, # e.g., "M2"
                output_plot_directory, 
                output_image_prefix, 
                igd_threshold, 
                save_plots, 
                output_formats
            )
        else:
            print(f"Nenhum dado para o grupo de objetivos '{obj_group_label}' após a filtragem.")

print("\nGeração de gráficos concluída.")