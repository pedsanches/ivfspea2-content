% run_ablation_v2_batch_C.m
% =========================================================================
% ABLATION V2 - BATCH C: V4 (Adaptive Trigger) + V5 (Post-SBX Mutation)
% =========================================================================
%
% This batch runs on Process 3 with 6 parpool workers.
% Configs: V4 (stagnation-based activation) and V5 (post-SBX mutation)
% Instances: 12 representative problems (M=2 and M=3)
% Runs: 30 per config-instance pair
%
% Usage:
%   matlab -nodisplay -r "run('/home/pedro/desenvolvimento/ivfspea2/scripts/experiments/run_ablation_v2_batch_C.m')"
%
% =========================================================================

%% Absolute paths
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ablation_v2_batchC_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== ABLATION V2 BATCH C - Log started: %s ===\n', datestr(now));
fprintf('MATLAB: %s\n', version);
fprintf('Log file: %s\n\n', log_file);

%% Setup paths
addpath(genpath(PLATEMO_DIR));
addpath(fullfile(PROJECT_ROOT, 'src', 'matlab', 'ivf_spea2'));

%% Experimental configuration
num_runs = 30;
maxFE    = 100000;
N_pop    = 100;

% IVF parameters (AR mode, same as paper)
C_val           = 0.11;
R_val           = 0.1;
M_val           = 0;      % AR mode
V_val           = 0;
Cycles_val      = 3;
S_val           = 1;
N_Offspring_val = 1;
EARN_val        = 0;
N_Obj_Limit_val = 0;

% 12 representative problem instances
problems = {
    @ZDT1,  2;   % Convex continuous (positive control)
    @ZDT6,  2;   % Concave non-uniform (regression guard)
    @WFG4,  2;   % Concave multimodal (ABL-DOM regressed)
    @WFG9,  2;   % Concave non-separable (mixed case)
    @DTLZ1, 3;   % Linear (positive control M=3)
    @DTLZ2, 3;   % Spherical regular (positive control M=3)
    @DTLZ4, 3;   % Spherical biased (FAILURE CASE)
    @DTLZ7, 3;   % Disconnected (marginal IVF win)
    @WFG2,  3;   % Disconnected non-sep (FAILURE CASE)
    @WFG5,  3;   % Concave degenerate (IVF success)
    @MaF1,  3;   % Linear inverted (diversity test)
    @MaF5,  3;   % Convex-inverted (FAILURE CASE)
};

% Algorithms for this batch: V4 + V5
algorithms = {
    'IVFSPEA2_V4_ADAPTIVE', @IVFSPEA2_V4_ADAPTIVE; % V4: stagnation-based trigger
    'IVFSPEA2_V5_MUTATION', @IVFSPEA2_V5_MUTATION;  % V5: post-SBX mutation
};

%% Output directory
output_base = fullfile(PROJECT_ROOT, 'data', 'ablation_v2', 'phase1');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool with 6 workers
if isempty(gcp('nocreate'))
    parpool('local', 6);
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

%% Run experiments
total_configs = size(algorithms, 1) * size(problems, 1);
total_runs    = total_configs * num_runs;
fprintf('=== ABLATION V2 BATCH C ===\n');
fprintf('Algorithms: %d | Problems: %d | Runs/config: %d | Total: %d runs\n', ...
    size(algorithms, 1), size(problems, 1), num_runs, total_runs);
fprintf('=============================\n\n');

global_errors = 0;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_func = algorithms{a, 2};

    for p = 1:size(problems, 1)
        prob_func = problems{p, 1};
        prob_M    = problems{p, 2};
        prob_name = func2str(prob_func);

        result_folder = fullfile(output_base, sprintf('%s_%s_M%d', algo_name, prob_name, prob_M));

        if isfolder(result_folder)
            existing = dir(fullfile(result_folder, '*.mat'));
            if length(existing) >= num_runs
                fprintf('[SKIP] %s on %s (M=%d) - already completed (%d files)\n', ...
                    algo_name, prob_name, prob_M, length(existing));
                continue;
            end
        end

        fprintf('[START] %s on %s (M=%d) - %d runs @ %s\n', ...
            algo_name, prob_name, prob_M, num_runs, datestr(now, 'HH:MM:SS'));
        tic;

        run_errors = cell(1, num_runs);

        parfor run = 1:num_runs
            try
                platemo('algorithm', {algo_func, C_val, R_val, M_val, V_val, ...
                                      Cycles_val, S_val, N_Offspring_val, ...
                                      EARN_val, N_Obj_Limit_val}, ...
                        'problem', prob_func, ...
                        'N', N_pop, ...
                        'M', prob_M, ...
                        'maxFE', maxFE, ...
                        'save', 1, ...
                        'run', run, ...
                        'metName', {'IGD'});
                run_errors{run} = '';
            catch ME
                run_errors{run} = sprintf('run %d: %s', run, ME.message);
            end
        end

        elapsed = toc;

        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            fprintf('[WARN] %d/%d runs FAILED:\n', length(failed_idx), num_runs);
            for fi = 1:length(failed_idx)
                fprintf('  %s\n', run_errors{failed_idx(fi)});
            end
            global_errors = global_errors + length(failed_idx);
        end

        default_folder = fullfile(PLATEMO_DATA, algo_name);
        if isfolder(default_folder)
            if ~isfolder(result_folder), mkdir(result_folder); end
            movefile(fullfile(default_folder, '*'), result_folder);
            rmdir(default_folder, 's');
        end

        actual_files = dir(fullfile(result_folder, '*.mat'));
        n_actual = length(actual_files);
        if n_actual == num_runs
            fprintf('[DONE]  %s on %s (M=%d) - %d/%d files OK - %.1f sec (%.1f sec/run)\n', ...
                algo_name, prob_name, prob_M, n_actual, num_runs, elapsed, elapsed/num_runs);
        else
            fprintf('[WARN]  %s on %s (M=%d) - %d/%d files (INCOMPLETE) - %.1f sec\n', ...
                algo_name, prob_name, prob_M, n_actual, num_runs, elapsed);
            existing_runs = zeros(1, n_actual);
            for fi = 1:n_actual
                tokens = regexp(actual_files(fi).name, '_(\d+)\.mat$', 'tokens');
                if ~isempty(tokens)
                    existing_runs(fi) = str2double(tokens{1}{1});
                end
            end
            missing = setdiff(1:num_runs, existing_runs);
            if ~isempty(missing)
                fprintf('         Missing runs: [%s]\n', num2str(missing));
            end
        end
    end
end

%% Summary
fprintf('\n=== BATCH C COMPLETE @ %s ===\n', datestr(now));
fprintf('Results saved in: %s\n', output_base);
if global_errors > 0
    fprintf('[ATTENTION] %d total run errors detected.\n', global_errors);
else
    fprintf('All runs completed successfully.\n');
end

%% Data Inventory
fprintf('\n--- Data Inventory (Batch C) ---\n');
fprintf('%-40s %-10s %s\n', 'Config', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 65));
for a = 1:size(algorithms, 1)
    for p = 1:size(problems, 1)
        folder_name = sprintf('%s_%s_M%d', algorithms{a,1}, func2str(problems{p,1}), problems{p,2});
        folder_path = fullfile(output_base, folder_name);
        if isfolder(folder_path)
            n = length(dir(fullfile(folder_path, '*.mat')));
        else
            n = 0;
        end
        if n >= num_runs, status = 'OK';
        elseif n > 0,     status = 'INCOMPLETE';
        else,             status = 'MISSING';
        end
        fprintf('%-40s %-10d %s\n', folder_name, n, status);
    end
end

%% Cleanup
diary off;
delete(gcp('nocreate'));
