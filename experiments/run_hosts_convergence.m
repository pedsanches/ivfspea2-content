%% run_hosts_convergence.m
% Dense-save re-execution for the hosts convergence figure.
%
% Usage:
%   matlab -batch "run('experiments/run_hosts_convergence.m')"

%% Configuration
NUM_RUNS = 30;
RUN_BASE = 7001;
MAX_FE = 100000;
N_SAVE = 100;
NUM_WORKERS = 6;
SUBMISSION_TAG = 'CONVERGENCE_HOSTS';

algorithms = {
    'IVFSPEA2V2', {@IVFSPEA2V2, 0.12, 0.225, 0.3, 0.1, 2};
    'SPEA2',      {@SPEA2};
    'IVFNSGAII',  {@IVFNSGAII, 0.5, 0.07, 5};
    'NSGAII',     {@NSGAII};
    'IVFNSGAIII', {@IVFNSGAIII, 0.10, 0.10, 5};
    'NSGAIII',    {@NSGAIII};
};

%% Load selected instances
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
instances_csv = fullfile(project_root, 'results', 'tables', 'hosts_convergence_instances.csv');
if ~isfile(instances_csv)
    error('Run select_convergence_instances.py first: %s not found', instances_csv);
end
T = readtable(instances_csv);
fprintf('Loaded %d instances from %s\n', height(T), instances_csv);

%% Map selected problems to PlatEMO dimensions
problem_D = struct( ...
    'ZDT1',30,'ZDT2',30,'ZDT3',30,'ZDT4',10,'ZDT6',10, ...
    'DTLZ1_M2',6,'DTLZ2_M2',11,'DTLZ3_M2',11,'DTLZ4_M2',11, ...
    'DTLZ5_M2',11,'DTLZ6_M2',11,'DTLZ7_M2',21, ...
    'DTLZ1_M3',7,'DTLZ2_M3',12,'DTLZ3_M3',12,'DTLZ4_M3',12, ...
    'DTLZ5_M3',12,'DTLZ6_M3',12,'DTLZ7_M3',22, ...
    'WFG1_M2',11,'WFG2_M2',11,'WFG3_M2',11,'WFG4_M2',11, ...
    'WFG5_M2',11,'WFG6_M2',11,'WFG7_M2',11,'WFG8_M2',11,'WFG9_M2',11, ...
    'WFG1_M3',12,'WFG2_M3',12,'WFG3_M3',12,'WFG4_M3',12, ...
    'WFG5_M3',12,'WFG6_M3',12,'WFG7_M3',12,'WFG8_M3',12,'WFG9_M3',12, ...
    'MaF1_M2',11,'MaF2_M2',11,'MaF3_M2',11,'MaF4_M2',11, ...
    'MaF5_M2',11,'MaF6_M2',11,'MaF7_M2',21, ...
    'MaF1_M3',12,'MaF2_M3',12,'MaF3_M3',12,'MaF4_M3',12, ...
    'MaF5_M3',12,'MaF6_M3',12,'MaF7_M3',22, ...
    'RWMOP9_M2',4);

all_problems = {};
for i = 1:height(T)
    prob_name = T.problem{i};
    M_obj = T.M(i);
    key = sprintf('%s_M%d', prob_name, M_obj);
    if isfield(problem_D, key)
        D_vars = problem_D.(key);
    elseif isfield(problem_D, prob_name)
        D_vars = problem_D.(prob_name);
    else
        error('Unknown problem/D mapping: %s M=%d', prob_name, M_obj);
    end
    all_problems(end + 1, :) = {str2func(prob_name), M_obj, D_vars}; %#ok<SAGROW>
end

fprintf('\nProblem set (%d instances):\n', size(all_problems, 1));
for i = 1:size(all_problems, 1)
    fprintf('  %s M=%d D=%d\n', func2str(all_problems{i,1}), all_problems{i,2}, all_problems{i,3});
end

%% Paths and logging
platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir)
    mkdir(log_dir);
end
log_file = fullfile(log_dir, sprintf('convergence_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('\n=== Convergence experiment ===\n');
fprintf('Start: %s | Tag: %s\n', datestr(now), SUBMISSION_TAG);
fprintf('Algos: %d | Problems: %d | Runs: %d | save: %d\n', ...
    size(algorithms, 1), size(all_problems, 1), NUM_RUNS, N_SAVE);

addpath(genpath(platemo_dir));
cd(platemo_dir);
data_dir = fullfile(platemo_dir, 'Data');

if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
end

%% Main loop
t_start = tic;
for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};
    fprintf('\n--- Algorithm: %s ---\n', algo_name);

    for p = 1:size(all_problems, 1)
        prob_handle = all_problems{p, 1};
        M_obj = all_problems{p, 2};
        D_vars = all_problems{p, 3};
        prob_name = func2str(prob_handle);

        fprintf('[%d/%d] %s on %s (M=%d, D=%d)\n', ...
            p, size(all_problems, 1), algo_name, prob_name, M_obj, D_vars);

        target_folder = fullfile(data_dir, algo_name);
        runs_needed = [];
        for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
            fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
            if ~isfile(fullfile(target_folder, fname))
                runs_needed(end + 1) = r; %#ok<AGROW>
            end
        end

        if isempty(runs_needed)
            fprintf('  -> already complete (%d/%d).\n', NUM_RUNS, NUM_RUNS);
            continue;
        end
        fprintf('  -> missing runs: %d\n', length(runs_needed));

        parfor ri = 1:length(runs_needed)
            run_idx = runs_needed(ri);
            try
                platemo('algorithm', algo_spec, ...
                        'problem', prob_handle, ...
                        'M', M_obj, ...
                        'D', D_vars, ...
                        'maxFE', MAX_FE, ...
                        'save', N_SAVE, ...
                        'run', run_idx, ...
                        'metName', {'IGD', 'HV'});
            catch ME
                fprintf('  [FAIL] %s/%s run %d: %s\n', algo_name, prob_name, run_idx, ME.message);
            end
        end

        n_found = 0;
        for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
            fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
            if isfile(fullfile(target_folder, fname))
                n_found = n_found + 1;
            end
        end
        fprintf('  -> files now: %d/%d\n', n_found, NUM_RUNS);
    end
end

elapsed = toc(t_start);
fprintf('\n=== COMPLETE in %.2f hours ===\n', elapsed / 3600);
delete(gcp('nocreate'));
diary off;
