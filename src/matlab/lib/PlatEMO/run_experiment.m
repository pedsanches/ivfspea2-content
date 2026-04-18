% Escolha o problema desejado
selected_problem = @MaF10;  % Altere para qualquer problema da lista
M_obj = 2

% Número de execuções por combinação
num_runs = 30;

% Lista de combinações de parâmetros a testar
R_poss = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300];
C_poss = [0.05, 0.07, 0.11, 0.16, 0.21, 0.27, 0.32, 0.42, 0.53, 0.64];

% Gerar combinações de R e C
param_combinations = combvec(R_poss, C_poss)';

% Iniciar o pool de processamento paralelo
if isempty(gcp('nocreate'))
    parpool; % Inicia um pool de trabalhadores com a configuração padrão
end

% Usar parfor para rodar as execuções em paralelo
for param_idx = 1:size(param_combinations, 1)
    % Definir valores de R e C da combinação atual
    R_val = param_combinations(param_idx, 1);
    C_val = param_combinations(param_idx, 2);

    % Outros parâmetros fixos
    M_val = 0;
    V_val = 0;
    Cycles_val = 20;
    S_val = 1;
    N_Offspring_val = 1;
    EARN_val = 0;
    N_Obj_Limit_val = 20;

    % Diretório original onde os resultados são armazenados
    original_folder = fullfile('Data', 'IVFSPEA2');

    % Nome da nova pasta baseada na combinação de parâmetros
    new_folder_name = sprintf('IVFSPEA2_R%.4f_C%.2f_%s', R_val, C_val, func2str(selected_problem));
    new_folder_path = fullfile('Data', new_folder_name);

    % Verificar se a pasta já existe
    if isfolder(new_folder_path)
        fprintf('A pasta %s já existe. Pulando...\n', new_folder_path);
        continue; % Pular para a próxima combinação de parâmetros
    end

    % Loop para as execuções
    parfor run = 1:num_runs
        % Gerar o índice único para cada execução
        unique_run_idx = (param_idx - 1) * num_runs + run;

        fprintf('Executando %s - Execução %d - R=%.4f, C=%.2f\n', ...
                func2str(selected_problem), unique_run_idx, R_val, C_val);

        try
            % Chama o PlatEMO
            platemo('algorithm', {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, ...
                                  N_Offspring_val, EARN_val, N_Obj_Limit_val}, ...
                    'problem', selected_problem, ...
                    'maxFE', 25000, ...
                    'save', 10, ...
                    'run', unique_run_idx, ...
                    'metName', {'IGD', 'HV'});

        catch ME
            fprintf('Erro ao executar %s na execução %d: %s\n', func2str(selected_problem), unique_run_idx, ME.message);
            fprintf('Erro ID: %s\n', ME.identifier);
            disp(ME.stack);
        end
    end

    % Renomear a pasta após todas as execuções
    if isfolder(original_folder)
        movefile(original_folder, new_folder_path);
        fprintf('Pasta renomeada para: %s\n', new_folder_path);
    else
        fprintf('Aviso: Pasta %s não encontrada. Nenhum arquivo foi movido.\n', original_folder);
    end
end

% Fechar o pool de processamento paralelo após a conclusão
delete(gcp('nocreate'));
