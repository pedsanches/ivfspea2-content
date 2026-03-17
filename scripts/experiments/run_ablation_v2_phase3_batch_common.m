% run_ablation_v2_phase3_batch_common.m
% =========================================================================
% ABLATION V2 - PHASE 3 FULL-SUITE VALIDATION (COMMON BATCH SCRIPT)
% =========================================================================
%
% Expected caller contract:
%   BATCH_ID must exist in workspace as one of: 'A', 'B', 'C'
%
% Phase 3 scope (from protocol):
%   - Winner config only: P2_C05 (H1=1, H2=1, H3=0, H4=0)
%   - Full synthetic suite: 51 instances (ZDT/DTLZ/WFG/MaF)
%   - 60 runs per instance
%   - Mandatory metrics: IGD + HV
%
% Design goals:
%   - Absolute-path IO (no cwd ambiguity)
%   - Resume-safe by expected run IDs
%   - Retry execution for missing runs
%   - Collect-only expected files from shared PlatEMO Data folder
%   - Hard fail on any missing run or execution error
%
% =========================================================================

%% Batch id validation
if ~exist('BATCH_ID', 'var')
    error('BATCH_ID is required (''A'', ''B'', or ''C'').');
end

BATCH_ID = upper(char(BATCH_ID));
if ~ismember(BATCH_ID, {'A','B','C'})
    error('Invalid BATCH_ID: %s (expected A/B/C).', BATCH_ID);
end

%% Absolute paths
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ablation_v2_phase3_batch%s_%s.log', BATCH_ID, datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== ABLATION V2 PHASE 3 BATCH %s - Log started: %s ===\n', BATCH_ID, datestr(now));
fprintf('MATLAB: %s\n', version);
fprintf('Log file: %s\n\n', log_file);

%% Setup paths
addpath(genpath(PLATEMO_DIR));

% Use isolated working directory to avoid path/cwd side effects
batch_workdir = fullfile(PROJECT_ROOT, 'logs', sprintf('workdir_phase3_batch%s', BATCH_ID));
if ~isfolder(batch_workdir), mkdir(batch_workdir); end
cd(batch_workdir);
fprintf('Working directory: %s\n', pwd);

%% Canonical algorithm path check
algo_paths_raw = which('IVFSPEA2_P2', '-all');
if isempty(algo_paths_raw)
    error('IVFSPEA2_P2 was not found in MATLAB path.');
end
algo_paths = cellstr(algo_paths_raw);
algo_paths = strtrim(algo_paths);
fprintf('IVFSPEA2_P2 path precedence:\n');
for i = 1:length(algo_paths)
    fprintf('  %d) %s\n', i, algo_paths{i});
end

expected_algo_dir = fullfile(PLATEMO_DIR, 'Algorithms', 'Multi-objective optimization', 'IVFSPEA2-P2-COMBINED');
if ~contains(algo_paths{1}, expected_algo_dir)
    error('Invalid IVFSPEA2_P2 path precedence. First path must be under: %s', expected_algo_dir);
end

%% Experimental configuration
cfg_name = 'P2_C05';
H1_flag = 1;
H2_flag = 1;
H3_flag = 0;
H4_flag = 0;

num_runs = 60;
maxFE    = 100000;
N_pop    = 100;

% Isolated run-id range for Phase 3 (avoid any legacy overlap)
run_id_base = 300000;
expected_runs = run_id_base + (1:num_runs);

max_retry_attempts = 3;
max_collect_attempts = 5;
workers_per_batch = 6;

% IVF parameters (same defaults as phase2)
C_val           = 0.11;
R_val           = 0.10;
M_val           = 0;
V_val           = 0;
Cycles_val      = 3;
S_val           = 1;
N_Offspring_val = 1;
EARN_val        = 0;
N_Obj_Limit_val = 0;

% Full synthetic suite (51 instances)
% Columns: {problem_handle, M, D}
all_problems = {
    @ZDT1, 2, 30;  @ZDT2, 2, 30;  @ZDT3, 2, 30;  @ZDT4, 2, 10;  @ZDT6, 2, 10;
    @DTLZ1, 2, 6;  @DTLZ2, 2, 11; @DTLZ3, 2, 11; @DTLZ4, 2, 11; @DTLZ5, 2, 11;
    @DTLZ6, 2, 11; @DTLZ7, 2, 21;
    @WFG1, 2, 11;  @WFG2, 2, 11;  @WFG3, 2, 11;  @WFG4, 2, 11;  @WFG5, 2, 11;
    @WFG6, 2, 11;  @WFG7, 2, 11;  @WFG8, 2, 11;  @WFG9, 2, 11;
    @MaF1, 2, 11;  @MaF2, 2, 11;  @MaF3, 2, 11;  @MaF4, 2, 11;  @MaF5, 2, 11;
    @MaF6, 2, 11;  @MaF7, 2, 21;
    @DTLZ1, 3, 7;  @DTLZ2, 3, 12; @DTLZ3, 3, 12; @DTLZ4, 3, 12; @DTLZ5, 3, 12;
    @DTLZ6, 3, 12; @DTLZ7, 3, 22;
    @WFG1, 3, 12;  @WFG2, 3, 12;  @WFG3, 3, 12;  @WFG4, 3, 12;  @WFG5, 3, 12;
    @WFG6, 3, 12;  @WFG7, 3, 12;  @WFG8, 3, 12;  @WFG9, 3, 12;
    @MaF1, 3, 12;  @MaF2, 3, 12;  @MaF3, 3, 12;  @MaF4, 3, 12;  @MaF5, 3, 12;
    @MaF6, 3, 12;  @MaF7, 3, 22;
};

% Deterministic split: round-robin over the 51-instance list
switch BATCH_ID
    case 'A'
        batch_mod = 0;
    case 'B'
        batch_mod = 1;
    otherwise
        batch_mod = 2;
end

all_idx = 1:size(all_problems, 1);
batch_idx = all_idx(mod(all_idx - 1, 3) == batch_mod);
problems = all_problems(batch_idx, :);

%% Output directory
output_base = fullfile(PROJECT_ROOT, 'data', 'ablation_v2', 'phase3');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool with isolated job storage
job_storage = fullfile(PROJECT_ROOT, 'logs', sprintf('parjobs_phase3_batch%s', BATCH_ID));
if ~isfolder(job_storage), mkdir(job_storage); end

myCluster = parcluster('local');
myCluster.JobStorageLocation = job_storage;
myCluster.NumWorkers = workers_per_batch;

if ~isempty(myCluster.Jobs)
    fprintf('Cleaning %d stale parallel jobs...\n', length(myCluster.Jobs));
    delete(myCluster.Jobs);
end

if isempty(gcp('nocreate'))
    parpool(myCluster, workers_per_batch);
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

%% Run experiments
total_configs = size(problems, 1);
total_runs    = total_configs * num_runs;

fprintf('=== ABLATION V2 PHASE 3 BATCH %s ===\n', BATCH_ID);
fprintf('Winner config: %s [H1=%d H2=%d H3=%d H4=%d]\n', cfg_name, H1_flag, H2_flag, H3_flag, H4_flag);
fprintf('Problems in this batch: %d\n', total_configs);
fprintf('Runs/problem: %d | Total runs in batch: %d\n', num_runs, total_runs);
fprintf('Run-ID range: %d-%d\n', min(expected_runs), max(expected_runs));
fprintf('Output base: %s\n', output_base);
fprintf('====================================\n\n');

global_errors = 0;
global_missing_runs = 0;
inventory = cell(0, 3); % {folder_name, n_expected, status}

for p = 1:size(problems, 1)
    prob_func = problems{p, 1};
    prob_M    = problems{p, 2};
    prob_D    = problems{p, 3};
    prob_name = func2str(prob_func);

    algo_label = sprintf('IVFSPEA2_%s', cfg_name);
    folder_name = sprintf('%s_%s_M%d', algo_label, prob_name, prob_M);
    result_folder = fullfile(output_base, folder_name);

    [n_existing, existing_runs] = count_expected_runs(result_folder, expected_runs);

    if n_existing >= num_runs
        fprintf('[SKIP] %s (D=%d) - already completed (%d expected files)\n', folder_name, prob_D, n_existing);
        inventory(end+1, :) = {folder_name, n_existing, 'OK'}; %#ok<AGROW>
        continue;
    end

    fprintf('[START] %s (D=%d) - %d missing runs @ %s\n', ...
        folder_name, prob_D, num_runs - n_existing, datestr(now, 'HH:MM:SS'));
    tic;

    for attempt = 1:max_retry_attempts
        [n_existing, existing_runs] = count_expected_runs(result_folder, expected_runs);
        missing_global = setdiff(expected_runs, existing_runs);
        if isempty(missing_global)
            break;
        end

        missing_local = missing_global - run_id_base;
        fprintf('[TRY %d/%d] %s - launching %d missing runs\n', ...
            attempt, max_retry_attempts, folder_name, length(missing_local));

        run_errors = cell(1, length(missing_local));

        parfor mi = 1:length(missing_local)
            local_run  = missing_local(mi);
            global_run = run_id_base + local_run;
            try
                platemo('algorithm', {@IVFSPEA2_P2, C_val, R_val, M_val, V_val, ...
                                      Cycles_val, S_val, N_Offspring_val, ...
                                      EARN_val, N_Obj_Limit_val, ...
                                      H1_flag, H2_flag, H3_flag, H4_flag}, ...
                        'problem', prob_func, ...
                        'N', N_pop, ...
                        'M', prob_M, ...
                        'D', prob_D, ...
                        'maxFE', maxFE, ...
                        'save', 1, ...
                        'run', global_run, ...
                        'metName', {'IGD','HV'});
                run_errors{mi} = '';
            catch ME
                run_errors{mi} = sprintf('local run %d (global %d): %s', local_run, global_run, ME.message);
            end
        end

        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            fprintf('[WARN] %d/%d launched runs FAILED:\n', length(failed_idx), length(missing_local));
            for fi = 1:length(failed_idx)
                fprintf('  %s\n', run_errors{failed_idx(fi)});
            end
            global_errors = global_errors + length(failed_idx);
        end

        source_folder = fullfile(PLATEMO_DATA, 'IVFSPEA2_P2');
        if isfolder(source_folder)
            [n_collected, ~] = collect_with_retries(source_folder, result_folder, ...
                prob_name, prob_M, prob_D, expected_runs, max_collect_attempts);
            fprintf('         Collected %d/%d expected files\n', n_collected, num_runs);
        else
            fprintf('[WARN] Source folder not found: %s\n', source_folder);
        end
    end

    elapsed = toc;

    [n_actual, existing_runs] = count_expected_runs(result_folder, expected_runs);
    if n_actual == num_runs
        fprintf('[DONE]  %s (D=%d) - %d/%d expected files OK - %.1f sec (%.1f sec/run)\n', ...
            folder_name, prob_D, n_actual, num_runs, elapsed, elapsed/num_runs);
        inventory(end+1, :) = {folder_name, n_actual, 'OK'}; %#ok<AGROW>
    else
        fprintf('[WARN]  %s (D=%d) - %d/%d expected files (INCOMPLETE) - %.1f sec\n', ...
            folder_name, prob_D, n_actual, num_runs, elapsed);
        missing_global = setdiff(expected_runs, existing_runs);
        missing_local = missing_global - run_id_base;
        fprintf('         Missing local runs:  [%s]\n', num2str(missing_local));
        fprintf('         Missing global runs: [%s]\n', num2str(missing_global));
        global_missing_runs = global_missing_runs + length(missing_global);
        inventory(end+1, :) = {folder_name, n_actual, 'INCOMPLETE'}; %#ok<AGROW>
    end
end

%% Summary
fprintf('\n=== PHASE 3 BATCH %s COMPLETE @ %s ===\n', BATCH_ID, datestr(now));
fprintf('Results saved in: %s\n', output_base);

if global_errors > 0 || global_missing_runs > 0
    fprintf('[ATTENTION] %d run errors and %d missing runs detected.\n', ...
        global_errors, global_missing_runs);
else
    fprintf('All runs completed successfully with full integrity.\n');
end

fprintf('\n--- Data Inventory (Phase 3 Batch %s) ---\n', BATCH_ID);
fprintf('%-40s %-10s %s\n', 'Folder', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 65));
for i = 1:size(inventory, 1)
    fprintf('%-40s %-10d %s\n', inventory{i,1}, inventory{i,2}, inventory{i,3});
end

%% Cleanup
diary off;
delete(gcp('nocreate'));

if global_errors > 0 || global_missing_runs > 0
    error('Phase 3 Batch %s failed integrity checks: %d errors, %d missing runs.', ...
        BATCH_ID, global_errors, global_missing_runs);
end

function [n_expected, present_expected] = count_expected_runs(result_folder, expected_runs)
    present_expected = [];
    if ~isfolder(result_folder)
        n_expected = 0;
        return;
    end

    files = dir(fullfile(result_folder, '*.mat'));
    if isempty(files)
        n_expected = 0;
        return;
    end

    run_ids = nan(1, length(files));
    n_ids = 0;
    for i = 1:length(files)
        token = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
        if ~isempty(token)
            n_ids = n_ids + 1;
            run_ids(n_ids) = str2double(token{1});
        end
    end

    if n_ids == 0
        n_expected = 0;
        return;
    end

    present_expected = intersect(unique(run_ids(1:n_ids)), expected_runs);
    n_expected = length(present_expected);
end

function moved = collect_expected_files(source_folder, result_folder, prob_name, prob_M, prob_D, expected_runs)
    moved = 0;
    if ~isfolder(result_folder)
        mkdir(result_folder);
    end

    pattern = sprintf('IVFSPEA2_P2_%s_M%d_D%d_*.mat', prob_name, prob_M, prob_D);
    files = dir(fullfile(source_folder, pattern));
    if isempty(files)
        return;
    end

    for i = 1:length(files)
        token = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
        if isempty(token)
            continue;
        end
        run_id = str2double(token{1});
        if ~ismember(run_id, expected_runs)
            continue;
        end

        src = fullfile(files(i).folder, files(i).name);
        dst = fullfile(result_folder, files(i).name);
        if isfile(dst)
            continue;
        end

        [ok, msg] = movefile(src, dst);
        if ok
            moved = moved + 1;
        else
            fprintf('[WARN] movefile failed for %s: %s\n', files(i).name, msg);
        end
    end
end

function [n_collected, present_expected] = collect_with_retries(source_folder, result_folder, prob_name, prob_M, prob_D, expected_runs, max_attempts)
    n_collected = 0;
    present_expected = [];
    for attempt = 1:max_attempts
        collect_expected_files(source_folder, result_folder, prob_name, prob_M, prob_D, expected_runs);
        [n_collected, present_expected] = count_expected_runs(result_folder, expected_runs);
        if n_collected == length(expected_runs)
            return;
        end
        if attempt < max_attempts
            pause(2);
        end
    end
end
