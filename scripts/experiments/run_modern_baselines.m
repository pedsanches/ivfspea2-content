% run_modern_baselines.m
% =========================================================================
% MODERN BASELINES: AGE-MOEA-II and AR-MOEA on all 51 instances
% =========================================================================
%
% Runs 2 modern MOEAs (2020-2025) under the same experimental protocol as
% the original paper to enable fair comparison.
%
% Algorithms:
%   1. AGE-MOEA-II (Panichella, 2022) - Adaptive geometry-based MOEA
%   2. AR-MOEA (Tian et al., 2018)    - Adaptive reference-point based MOEA
%
% Protocol (identical to main experiments):
%   - 100 independent runs per algorithm per instance
%   - 100,000 max FE, N=100
%   - PlatEMO defaults for algorithm-specific parameters
%   - Metric: IGD
%
% Data quality measures:
%   - Per-run error tracking via cell array (parfor-safe)
%   - Post-parfor file count validation
%   - Missing run identification
%   - Full session log via diary
%
% Usage:
%   matlab -nodisplay -r "run('/home/pedro/desenvolvimento/ivfspea2/scripts/experiments/run_modern_baselines.m')"
%
% =========================================================================

%% Absolute paths (immune to platemo cwd changes)
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('modern_baselines_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== Log started: %s ===\n', datestr(now));
fprintf('MATLAB: %s\n', version);
fprintf('Log file: %s\n\n', log_file);

%% Setup paths
addpath(genpath(PLATEMO_DIR));
addpath(fullfile(PROJECT_ROOT, 'src', 'matlab', 'ivf_spea2'));

%% Experimental configuration
num_runs = 100;
maxFE    = 100000;
N_pop    = 100;

% Problem instances (same as paper: 28 M=2, 23 M=3 = 51 total)
problems_M2 = {
    @DTLZ1, @DTLZ2, @DTLZ3, @DTLZ4, @DTLZ5, @DTLZ6, @DTLZ7, ...
    @MaF1,  @MaF2,  @MaF3,  @MaF4,  @MaF5,  @MaF6,  @MaF7,  ...
    @WFG1,  @WFG2,  @WFG3,  @WFG4,  @WFG5,  @WFG6,  @WFG7,  @WFG8, @WFG9, ...
    @ZDT1,  @ZDT2,  @ZDT3,  @ZDT4,  @ZDT6
};

problems_M3 = {
    @DTLZ1, @DTLZ2, @DTLZ3, @DTLZ4, @DTLZ5, @DTLZ6, @DTLZ7, ...
    @MaF1,  @MaF2,  @MaF3,  @MaF4,  @MaF5,  @MaF6,  @MaF7,  ...
    @WFG1,  @WFG2,  @WFG3,  @WFG4,  @WFG5,  @WFG6,  @WFG7,  @WFG8, @WFG9
};

% Algorithms
algorithms = {
    'AGEMOEAII', @AGEMOEAII;
    'ARMOEA',    @ARMOEA;
};

%% Output directory (absolute path)
output_base = fullfile(PROJECT_ROOT, 'data', 'modern_baselines');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool
if isempty(gcp('nocreate'))
    parpool('local');
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

%% Helper: run one algorithm on one problem set
%  (avoids duplicating the same parfor block for M=2 and M=3)
global_errors = 0;
inventory = {};  % {folder_name, n_files, status}

    function [global_errors, inventory] = run_batch(prob_list, prob_M, algorithms, num_runs, N_pop, maxFE, PLATEMO_DATA, output_base, global_errors, inventory)
        for a = 1:size(algorithms, 1)
            algo_name = algorithms{a, 1};
            algo_func = algorithms{a, 2};
            for p = 1:length(prob_list)
                prob_func = prob_list{p};
                prob_name = func2str(prob_func);
                folder_name = sprintf('%s_%s_M%d', algo_name, prob_name, prob_M);
                result_folder = fullfile(output_base, folder_name);

                % Skip if completed
                if isfolder(result_folder)
                    existing = dir(fullfile(result_folder, '*.mat'));
                    if length(existing) >= num_runs
                        fprintf('[SKIP] %s - already completed (%d files)\n', folder_name, length(existing));
                        inventory{end+1, 1} = folder_name; %#ok<AGROW>
                        inventory{end,   2} = length(existing);
                        inventory{end,   3} = 'OK';
                        continue;
                    end
                end

                fprintf('[START] %s - %d runs @ %s\n', folder_name, num_runs, datestr(now, 'HH:MM:SS'));
                tic;

                run_errors = cell(1, num_runs);
                parfor run = 1:num_runs
                    try
                        platemo('algorithm', algo_func, ...
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

                % Report errors
                failed_idx = find(~cellfun(@isempty, run_errors));
                if ~isempty(failed_idx)
                    fprintf('[WARN] %d/%d runs FAILED:\n', length(failed_idx), num_runs);
                    for fi = 1:min(5, length(failed_idx))  % print first 5
                        fprintf('  %s\n', run_errors{failed_idx(fi)});
                    end
                    if length(failed_idx) > 5
                        fprintf('  ... and %d more\n', length(failed_idx) - 5);
                    end
                    global_errors = global_errors + length(failed_idx);
                end

                % Move results
                default_folder = fullfile(PLATEMO_DATA, algo_name);
                if isfolder(default_folder)
                    if ~isfolder(result_folder), mkdir(result_folder); end
                    movefile(fullfile(default_folder, '*'), result_folder);
                    rmdir(default_folder, 's');
                end

                % Validate
                actual_files = dir(fullfile(result_folder, '*.mat'));
                n_actual = length(actual_files);
                if n_actual >= num_runs
                    status = 'OK';
                elseif n_actual > 0
                    status = 'INCOMPLETE';
                else
                    status = 'MISSING';
                end
                fprintf('[DONE]  %s - %d/%d files (%s) - %.1f sec\n', ...
                    folder_name, n_actual, num_runs, status, elapsed);
                inventory{end+1, 1} = folder_name; %#ok<AGROW>
                inventory{end,   2} = n_actual;
                inventory{end,   3} = status;
            end
        end
    end

%% Run experiments
total_instances = length(problems_M2) + length(problems_M3);
fprintf('=== MODERN BASELINES EXPERIMENT ===\n');
fprintf('Algorithms: %d | Instances: %d | Runs/instance: %d | Total: %d runs\n', ...
    size(algorithms, 1), total_instances, num_runs, ...
    size(algorithms, 1) * total_instances * num_runs);
fprintf('====================================\n\n');

fprintf('--- Phase 1: M=2 instances (%d problems) ---\n', length(problems_M2));
[global_errors, inventory] = run_batch(problems_M2, 2, algorithms, num_runs, N_pop, maxFE, PLATEMO_DATA, output_base, global_errors, inventory);

fprintf('\n--- Phase 2: M=3 instances (%d problems) ---\n', length(problems_M3));
[global_errors, inventory] = run_batch(problems_M3, 3, algorithms, num_runs, N_pop, maxFE, PLATEMO_DATA, output_base, global_errors, inventory);

%% Summary
fprintf('\n=== MODERN BASELINES COMPLETE @ %s ===\n', datestr(now));
fprintf('Results saved in: %s\n', output_base);
if global_errors > 0
    fprintf('[ATTENTION] %d total run errors detected.\n', global_errors);
else
    fprintf('All runs completed successfully.\n');
end

fprintf('\n--- Data Inventory ---\n');
fprintf('%-30s %-10s %s\n', 'Config', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 55));
for i = 1:size(inventory, 1)
    fprintf('%-30s %-10d %s\n', inventory{i,1}, inventory{i,2}, inventory{i,3});
end

%% Cleanup
diary off;
delete(gcp('nocreate'));
