addpath(genpath('src/matlab/lib/PlatEMO'));
addpath('src/matlab/ivf_spea2');

% Experiment Parameters
prob_name = @ZDT1;    % Problem (ZDT1, ZDT2, ZDT3, etc.)
N = 100;              % Population size
maxFE = 10000;        % Max function evaluations
runs = 1;             % Number of runs

% IVFSPEA2 Parameters (Defaults)
C = 0.11;             % Collection rate
R = 0.1;              % IVF trigger ratio
M = 0.5;              % Mothers mutation rate
V = 0.5;              % Variables mutation rate
Cycles = 3;           % IVF cycles
S = 1;                % Steady State
N_Offspring = 1;      % Offspring per crossover
EARN = 0;             % EAR mode
N_Obj_Limit = 0;      % Limit for father selection

% Run PlatEMO
fprintf('Running IVFSPEA2 on %s with N=%d, MaxFE=%d...\n', func2str(prob_name), N, maxFE);

platemo('algorithm', {@IVFSPEA2, C, R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit}, ...
        'problem', prob_name, ...
        'N', N, ...
        'maxFE', maxFE, ...
        'save', runs);

fprintf('\nExperiment complete.\nResults should be in "Data/IVFSPEA2/..." (PlatEMO default output folder).\n');
