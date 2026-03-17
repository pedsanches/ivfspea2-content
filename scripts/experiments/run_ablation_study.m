% run_ablation_study.m
% =========================================================================
% ABLATION STUDY: Validate the top-2c acceptance criterion
% =========================================================================
%
% Compares 4 variants of IVF/SPEA2:
%   1. IVFSPEA2       - Standard (top-2c, SPEA2 fitness-based)
%   2. IVFSPEA2ABL1C  - Ablation: top-1c (same pool as mothers)
%   3. IVFSPEA2ABL4C  - Ablation: top-4c (broader pool)
%   4. IVFSPEA2ABLDOM - Ablation: Pareto dominance-based (NSGA-II style)
%
% Experimental protocol:
%   - 5 representative instances (covering success/failure/diversity)
%   - 30 independent runs per variant per instance
%   - 100,000 max FE, N=100, c=0.11, r=0.1 (AR mode: M=0)
%   - Metrics: IGD
%
% Data quality measures:
%   - Per-run error tracking via cell array (parfor-safe)
%   - Post-parfor file count validation
%   - Missing run identification
%   - Full session log via diary
%
% Usage:
%   matlab -nodisplay -r "run('/home/pedro/desenvolvimento/ivfspea2/scripts/experiments/run_ablation_study.m')"
%
% =========================================================================

%% Absolute paths (immune to platemo cwd changes)
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ablation_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== Log started: %s ===\n', datestr(now));
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

% Representative problem instances
problems = {
    @DTLZ1, 3;   % Regular front, success case
    @DTLZ7, 3;   % Disconnected front, failure case
    @WFG4,  2;   % Multimodal
    @MaF1,  3;   % Many-objective
    @ZDT1,  2;   % Simple baseline
};

% Algorithms to compare
algorithms = {
    'IVFSPEA2',       @IVFSPEA2;
    'IVFSPEA2ABL1C',  @IVFSPEA2ABL1C;
    'IVFSPEA2ABL4C',  @IVFSPEA2ABL4C;
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM;
};

%% Output directory (absolute path)
output_base = fullfile(PROJECT_ROOT, 'data', 'ablation');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool
if isempty(gcp('nocreate'))
    parpool('local');
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

%% Run experiments
total_configs = size(algorithms, 1) * size(problems, 1);
total_runs    = total_configs * num_runs;
fprintf('=== ABLATION STUDY: top-2c criterion validation ===\n');
fprintf('Algorithms: %d | Problems: %d | Runs/config: %d | Total: %d runs\n', ...
    size(algorithms, 1), size(problems, 1), num_runs, total_runs);
fprintf('====================================================\n\n');

global_errors = 0;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_func = algorithms{a, 2};

    for p = 1:size(problems, 1)
        prob_func = problems{p, 1};
        prob_M    = problems{p, 2};
        prob_name = func2str(prob_func);

        % Organized output folder (absolute path)
        result_folder = fullfile(output_base, sprintf('%s_%s_M%d', algo_name, prob_name, prob_M));

        % Skip if already completed
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

        % Error tracking (parfor-safe: each cell written by one worker)
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

        % Report errors
        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            fprintf('[WARN] %d/%d runs FAILED:\n', length(failed_idx), num_runs);
            for fi = 1:length(failed_idx)
                fprintf('  %s\n', run_errors{failed_idx(fi)});
            end
            global_errors = global_errors + length(failed_idx);
        end

        % Move results from PlatEMO's default Data dir to organized folder
        default_folder = fullfile(PLATEMO_DATA, algo_name);
        if isfolder(default_folder)
            if ~isfolder(result_folder), mkdir(result_folder); end
            movefile(fullfile(default_folder, '*'), result_folder);
            rmdir(default_folder, 's');
        end

        % Post-move validation: count files
        actual_files = dir(fullfile(result_folder, '*.mat'));
        n_actual = length(actual_files);
        if n_actual == num_runs
            fprintf('[DONE]  %s on %s (M=%d) - %d/%d files OK - %.1f sec (%.1f sec/run)\n', ...
                algo_name, prob_name, prob_M, n_actual, num_runs, elapsed, elapsed/num_runs);
        else
            fprintf('[WARN]  %s on %s (M=%d) - %d/%d files (INCOMPLETE) - %.1f sec\n', ...
                algo_name, prob_name, prob_M, n_actual, num_runs, elapsed);
            % Identify missing run numbers
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
fprintf('\n=== ABLATION STUDY COMPLETE @ %s ===\n', datestr(now));
fprintf('Results saved in: %s\n', output_base);
if global_errors > 0
    fprintf('[ATTENTION] %d total run errors detected. Check log for details.\n', global_errors);
else
    fprintf('All runs completed successfully.\n');
end
fprintf('Log file: %s\n', log_file);

%% Final validation: summary table
fprintf('\n--- Data Inventory ---\n');
fprintf('%-25s %-10s %s\n', 'Config', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 50));
for a = 1:size(algorithms, 1)
    for p = 1:size(problems, 1)
        folder_name = sprintf('%s_%s_M%d', algorithms{a,1}, func2str(problems{p,1}), problems{p,2});
        folder_path = fullfile(output_base, folder_name);
        if isfolder(folder_path)
            n = length(dir(fullfile(folder_path, '*.mat')));
        else
            n = 0;
        end
        if n >= num_runs
            status = 'OK';
        elseif n > 0
            status = 'INCOMPLETE';
        else
            status = 'MISSING';
        end
        fprintf('%-25s %-10d %s\n', folder_name, n, status);
    end
end

%% Cleanup
diary off;
delete(gcp('nocreate'));
