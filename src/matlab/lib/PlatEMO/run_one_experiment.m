% Escolha o problema desejado
selected_problem = @MaF2;  % Altere para qualquer problema da lista

% Defina os valores de C, R e M manualmente
C_val = 0;  
R_val = 0;  
M_val = 0;
V_val = 0;
Cycles_val = 40;
S_val = 1;
N_Offspring_val = 1;
EARN_val = 0;
N_Obj_Limit_val = 20;

% Execução única
run = 1;
fprintf('Executando %s - Execução %d - C=%.2f, R=%.2f, M=%.2f\n', ...
        func2str(selected_problem), run, C_val, R_val, M_val);

try
    % Chama o PlatEMO para a execução única
    platemo('algorithm', {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, ...
                          N_Offspring_val, EARN_val, N_Obj_Limit_val}, ...
            'problem', selected_problem, ...
            'maxFE', 100000, ...
            'M', 3, ....
            'save', 10, ...
            'run', run, ...
            'metName', {'IGD', 'HV'});

catch ME
    fprintf('Erro ao executar %s na execução %d: %s\n', func2str(selected_problem), run, ME.message);
    fprintf('Erro ID: %s\n', ME.identifier);
    disp(ME.stack);
end
