%% run_norm_pilot.m
% Quick pilot: compare IVFSPEA2V2 (no normalization) vs IVFSPEA2V2Norm
% (min-max normalized dissimilar father) on 5 problems where normalization
% should matter most.
%
% Data is saved under PlatEMO/Data/{IVFSPEA2V2Norm,IVFSPEA2V2} with
% run IDs 9001..9030 (isolated from submission runs).
%
% Usage:
%   matlab -batch "run('experiments/run_norm_pilot.m')"

%% Configuration
NUM_RUNS     = 30;
RUN_BASE     = 9001;  % well away from submission IDs (2xxx, 3xxx)
MAX_FE       = 100000;
N_SAVE       = 10;
NUM_WORKERS  = 6;

% Tuned C26 parameters (same for both)
ivf_cfg = struct( ...
    'collection_rate', 0.12, ...
    'ivf_activation_ratio', 0.225, ...
    'mother_mutation_fraction', 0.3, ...
    'variable_mutation_fraction', 0.1, ...
    'max_ivf_cycles', 2, ...
    'offspring_per_mother', 1, ...
    'exploration_mode', 0); % 0: EAR, 1: EARN

params = {ivf_cfg.collection_rate, ivf_cfg.ivf_activation_ratio, ...
          ivf_cfg.mother_mutation_fraction, ivf_cfg.variable_mutation_fraction, ...
          ivf_cfg.max_ivf_cycles, ivf_cfg.offspring_per_mother, ivf_cfg.exploration_mode};
% C, R, M, V, Cycles, N_Offspring, EARN

algorithms = {
    'IVFSPEA2V2',     {@IVFSPEA2V2,     params{:}};
    'IVFSPEA2V2Norm', {@IVFSPEA2V2Norm, params{:}};
};

% 5 problems where normalization has the most impact:
%   RWMOP9  M=2 — engineering, heterogeneous objective scales
%   WFG1    M=2 — only v2 loss vs v1, possible scale bias
%   WFG1    M=3 — ranges [0,2],[0,4],[0,6]
%   WFG4    M=3 — multi-modal, good representative
%   WFG7    M=3 — separable, another representative
problems = {
    @RWMOP9, 2,  4;
    @WFG1,   2, 11;
    @WFG1,   3, 12;
    @WFG4,   3, 12;
    @WFG7,   3, 12;
};

%% Setup
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');

log_dir = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('norm_pilot_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== NORMALIZATION PILOT EXPERIMENT ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Runs/config: %d | maxFE: %d | Run range: %d..%d\n', ...
    NUM_RUNS, MAX_FE, RUN_BASE, RUN_BASE + NUM_RUNS - 1);
fprintf('Problems: %d | Algorithms: %d\n', size(problems, 1), size(algorithms, 1));
fprintf('Log: %s\n\n', log_file);

addpath(genpath(platemo_dir));
cd(platemo_dir);

data_dir = fullfile(platemo_dir, 'Data');

% Start parallel pool
if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
end

%% Main loop
t_start = tic;
total_configs = size(problems, 1) * size(algorithms, 1);
config_idx = 0;

for ai = 1:size(algorithms, 1)
    algo_name = algorithms{ai, 1};
    algo_spec = algorithms{ai, 2};

    for pi = 1:size(problems, 1)
        config_idx = config_idx + 1;
        prob_handle = problems{pi, 1};
        M_obj       = problems{pi, 2};
        D_vars      = problems{pi, 3};
        prob_name   = func2str(prob_handle);

        fprintf('[%d/%d] %s on %s (M=%d, D=%d)\n', ...
            config_idx, total_configs, algo_name, prob_name, M_obj, D_vars);

        % Check which runs are missing (resume-safe)
        target_folder = fullfile(data_dir, algo_name);
        runs_needed = [];
        for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
            fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
            if ~isfile(fullfile(target_folder, fname))
                runs_needed(end+1) = r; %#ok<AGROW>
            end
        end

        if isempty(runs_needed)
            fprintf('  -> already complete (%d/%d)\n', NUM_RUNS, NUM_RUNS);
            continue;
        end

        fprintf('  -> running %d missing runs\n', length(runs_needed));

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
                        'metName', {'IGD','HV'});
            catch ME
                fprintf('  [FAIL] %s/%s run %d: %s\n', algo_name, prob_name, run_idx, ME.message);
            end
        end

        % Post-check
        n_found = 0;
        for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
            fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
            if isfile(fullfile(target_folder, fname))
                n_found = n_found + 1;
            end
        end
        fprintf('  -> files: %d/%d\n', n_found, NUM_RUNS);
    end
end

elapsed = toc(t_start);
fprintf('\n=== PILOT COMPLETE in %.2f hours ===\n', elapsed/3600);

delete(gcp('nocreate'));
diary off;
