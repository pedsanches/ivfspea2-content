% run_engineering_rwmop9.m
% =========================================================================
% ENGINEERING BENCHMARK: RWMOP9 (Four Bar Plane Truss)
% =========================================================================
%
% Runs all algorithms on RWMOP9 to validate IVF/SPEA2 on a real-world
% engineering optimization problem.
%
% RWMOP9 characteristics:
%   - 2 objectives (structural volume, displacement)
%   - 4 decision variables (cross-sectional areas)
%   - 0 constraints (unconstrained)
%   - Source: Kumar et al., "A benchmark-suite of real-world constrained
%     multi-objective optimization problems," SWEVO, 2021.
%
% Algorithms (9 total = 7 original + 2 modern baselines):
%   IVFSPEA2, SPEA2, SPEA2+SDE, MFO-SPEA2, NSGA-II, NSGA-III, MOEA/D,
%   AGE-MOEA-II, AR-MOEA
%
% Protocol:
%   - 100 independent runs per algorithm
%   - 100,000 max FE, N=100
%   - Metric: IGD
%
% Data quality measures:
%   - Per-run error tracking via cell array (parfor-safe)
%   - Post-parfor file count validation
%   - Full session log via diary
%
% Usage:
%   matlab -nodisplay -r "run('/home/pedro/desenvolvimento/ivfspea2/scripts/experiments/run_engineering_rwmop9.m')"
%
% =========================================================================

%% Absolute paths (immune to platemo cwd changes)
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Runtime controls (via environment variables)
% ENG_GROUP: ALL (default) | G1 | G2 | G3
% ENG_WORKERS: number of local workers for parpool (default = local profile default)
ENG_GROUP = strtrim(getenv('ENG_GROUP'));
if isempty(ENG_GROUP)
    ENG_GROUP = 'ALL';
end
ENG_WORKERS = str2double(getenv('ENG_WORKERS'));
if isnan(ENG_WORKERS) || ENG_WORKERS <= 0
    ENG_WORKERS = [];
end

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('engineering_%s_%s.log', lower(ENG_GROUP), datestr(now, 'yyyymmdd_HHMMSS')));
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
prob_M   = 2;  % RWMOP9 is bi-objective

% IVF parameters (AR mode, same as paper)
C_val           = 0.11;
R_val           = 0.1;
M_val           = 0;
V_val           = 0;
Cycles_val      = 3;
S_val           = 1;
N_Offspring_val = 1;
EARN_val        = 0;
N_Obj_Limit_val = 0;

% All algorithms (9 total)
algorithms = {
    'IVFSPEA2',  {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'SPEA2',     @SPEA2;
    'SPEA2SDE',  @SPEA2SDE;
    'MFOSPEA2',  @MFOSPEA2;
    'NSGAII',    @NSGAII;
    'NSGAIII',   @NSGAIII;
    'MOEAD',     @MOEAD;
    'AGEMOEAII', @AGEMOEAII;
    'ARMOEA',    @ARMOEA;
};

% Optional algorithm subset by group (for multi-process execution)
switch upper(ENG_GROUP)
    case 'G1'
        selected_names = {'IVFSPEA2', 'SPEA2', 'SPEA2SDE'};
    case 'G2'
        selected_names = {'MFOSPEA2', 'NSGAII', 'NSGAIII'};
    case 'G3'
        selected_names = {'MOEAD', 'AGEMOEAII', 'ARMOEA'};
    otherwise
        selected_names = algorithms(:, 1);
end

mask = ismember(algorithms(:, 1), selected_names);
algorithms = algorithms(mask, :);

if isempty(algorithms)
    error('No algorithms selected for ENG_GROUP=%s', ENG_GROUP);
end

%% Output directory (absolute path)
output_base = fullfile(PROJECT_ROOT, 'data', 'engineering');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool
if isempty(gcp('nocreate'))
    if isempty(ENG_WORKERS)
        parpool('local');
    else
        parpool('local', ENG_WORKERS);
    end
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

fprintf('=== ENGINEERING BENCHMARK: RWMOP9 ===\n');
fprintf('Group: %s\n', upper(ENG_GROUP));
fprintf('Algorithms: %d | Runs: %d | Total: %d runs\n', ...
    size(algorithms, 1), num_runs, size(algorithms, 1) * num_runs);
fprintf('======================================\n\n');

%% Run experiments
global_errors = 0;

for a = 1:size(algorithms, 1)
    algo_name   = algorithms{a, 1};
    algo_config = algorithms{a, 2};

    result_folder = fullfile(output_base, sprintf('%s_RWMOP9_M%d', algo_name, prob_M));

    % Skip if completed
    if isfolder(result_folder)
        existing = dir(fullfile(result_folder, '*.mat'));
        if length(existing) >= num_runs
            fprintf('[SKIP] %s on RWMOP9 - already completed (%d files)\n', algo_name, length(existing));
            continue;
        end
    end

    fprintf('[START] %s on RWMOP9 - %d runs @ %s\n', algo_name, num_runs, datestr(now, 'HH:MM:SS'));
    tic;

    run_errors = cell(1, num_runs);
    parfor run = 1:num_runs
        try
            platemo('algorithm', algo_config, ...
                    'problem', @RWMOP9, ...
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
        for fi = 1:min(5, length(failed_idx))
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
        fprintf('[DONE]  %s on RWMOP9 - %d/%d files OK - %.1f sec\n', ...
            algo_name, n_actual, num_runs, elapsed);
    else
        fprintf('[WARN]  %s on RWMOP9 - %d/%d files (INCOMPLETE) - %.1f sec\n', ...
            algo_name, n_actual, num_runs, elapsed);
    end
end

%% Summary
fprintf('\n=== ENGINEERING BENCHMARK COMPLETE @ %s ===\n', datestr(now));
fprintf('Results saved in: %s\n', output_base);
if global_errors > 0
    fprintf('[ATTENTION] %d total run errors detected.\n', global_errors);
else
    fprintf('All runs completed successfully.\n');
end

fprintf('\n--- Data Inventory ---\n');
fprintf('%-20s %-10s %s\n', 'Algorithm', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 45));
for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    folder = fullfile(output_base, sprintf('%s_RWMOP9_M%d', algo_name, prob_M));
    if isfolder(folder)
        n = length(dir(fullfile(folder, '*.mat')));
    else
        n = 0;
    end
    if n >= num_runs, status = 'OK';
    elseif n > 0,     status = 'INCOMPLETE';
    else,             status = 'MISSING';
    end
    fprintf('%-20s %-10d %s\n', algo_name, n, status);
end

%% Cleanup
diary off;
delete(gcp('nocreate'));
