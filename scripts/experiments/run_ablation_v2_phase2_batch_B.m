% run_ablation_v2_phase2_batch_B.m
% =========================================================================
% ABLATION V2 - PHASE 2 BATCH B: Configs C6-C10 (5 configs × 12 instances)
% =========================================================================
%
% This batch runs on Process 2 with 6 parpool workers.
% 60 runs per config-instance pair.
%
% Usage:
%   matlab -nodisplay -r "run('/home/pedro/desenvolvimento/ivfspea2/scripts/experiments/run_ablation_v2_phase2_batch_B.m')"
%
% =========================================================================

%% Absolute paths
PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
PLATEMO_DATA = fullfile(PLATEMO_DIR, 'Data');

%% Persistent logging
log_dir = fullfile(PROJECT_ROOT, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ablation_v2_phase2_batchB_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== ABLATION V2 PHASE 2 BATCH B - Log started: %s ===\n', datestr(now));
fprintf('MATLAB: %s\n', version);
fprintf('Log file: %s\n\n', log_file);

%% Setup paths
addpath(genpath(PLATEMO_DIR));

% Use an isolated working directory so PlatEMO's relative 'Data/' folder
% does not collide with other parallel batch processes
batch_workdir = fullfile(PROJECT_ROOT, 'logs', 'workdir_batchB');
if ~isfolder(batch_workdir), mkdir(batch_workdir); end
cd(batch_workdir);
fprintf('Working directory: %s\n', pwd);

%% Experimental configuration
num_runs = 60;
maxFE    = 100000;
N_pop    = 100;

% Run-ID isolation and recovery
% Using a high base avoids collisions with legacy files (e.g., run 1..60)
run_id_base        = 100000;
max_retry_attempts = 3;
max_collect_attempts = 5;

% IVF parameters (AR mode, same as paper)
C_val           = 0.11;
R_val           = 0.1;
M_val           = 0;      % AR mode (no mother mutation)
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
    @WFG4,  2;   % Concave multimodal
    @WFG9,  2;   % Concave non-separable
    @DTLZ1, 3;   % Linear (positive control M=3)
    @DTLZ2, 3;   % Spherical regular (positive control M=3)
    @DTLZ4, 3;   % Spherical biased (failure case)
    @DTLZ7, 3;   % Disconnected
    @WFG2,  3;   % Disconnected non-sep (failure case)
    @WFG5,  3;   % Concave degenerate
    @MaF1,  3;   % Linear inverted
    @MaF5,  3;   % Convex-inverted (failure case)
};

% Phase 2 factorial combinations for this batch: C6-C10
% Each row: {name, H1, H2, H3, H4}
configs = {
    'P2_C06', 1, 0, 1, 0;   % C6:  H1+H3
    'P2_C07', 1, 0, 0, 1;   % C7:  H1+H4
    'P2_C08', 0, 1, 1, 0;   % C8:  H2+H3
    'P2_C09', 0, 1, 0, 1;   % C9:  H2+H4
    'P2_C10', 0, 0, 1, 1;   % C10: H3+H4
};

%% Output directory
output_base = fullfile(PROJECT_ROOT, 'data', 'ablation_v2', 'phase2');
if ~isfolder(output_base), mkdir(output_base); end

%% Initialize parallel pool with 6 workers
% Use isolated job storage to avoid conflicts with parallel MATLAB processes
job_storage = fullfile(PROJECT_ROOT, 'logs', 'parjobs_batchB');
if ~isfolder(job_storage), mkdir(job_storage); end

myCluster = parcluster('local');
myCluster.JobStorageLocation = job_storage;
myCluster.NumWorkers = 6;

% Clean up any stale jobs in this isolated storage
if ~isempty(myCluster.Jobs)
    fprintf('Cleaning %d stale parallel jobs...\n', length(myCluster.Jobs));
    delete(myCluster.Jobs);
end

if isempty(gcp('nocreate'))
    parpool(myCluster, 6);
end
pool = gcp;
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

%% Run experiments
total_configs = size(configs, 1) * size(problems, 1);
total_runs    = total_configs * num_runs;
cfg_ids = cellfun(@parse_config_index, configs(:,1));
batch_run_min = run_id_base + min(cfg_ids) * num_runs + 1;
batch_run_max = run_id_base + max(cfg_ids) * num_runs + num_runs;
fprintf('=== ABLATION V2 PHASE 2 BATCH B ===\n');
fprintf('Configs: %d | Problems: %d | Runs/config: %d | Total: %d runs\n', ...
    size(configs, 1), size(problems, 1), num_runs, total_runs);
fprintf('Run-ID base: %d (global run range %d-%d)\n', ...
    run_id_base, batch_run_min, batch_run_max);
fprintf('====================================\n\n');

global_errors = 0;
global_missing_runs = 0;

for c = 1:size(configs, 1)
    cfg_name = configs{c, 1};
    H1_flag  = configs{c, 2};
    H2_flag  = configs{c, 3};
    H3_flag  = configs{c, 4};
    H4_flag  = configs{c, 5};

    for p = 1:size(problems, 1)
        prob_func = problems{p, 1};
        prob_M    = problems{p, 2};
        prob_name = func2str(prob_func);

        cfg_idx = parse_config_index(cfg_name);
        expected_runs = run_id_base + cfg_idx * num_runs + (1:num_runs);

        % Algorithm name used by PlatEMO for output
        algo_label = sprintf('IVFSPEA2_%s', cfg_name);

        % Organized output folder
        result_folder = fullfile(output_base, sprintf('%s_%s_M%d', algo_label, prob_name, prob_M));

        [n_existing, existing_runs] = count_expected_runs(result_folder, expected_runs);

        % Skip if already completed (expected run IDs only)
        if n_existing >= num_runs
            fprintf('[SKIP] %s on %s (M=%d) - already completed (%d expected files)\n', ...
                algo_label, prob_name, prob_M, n_existing);
            continue;
        end

        missing_initial = num_runs - n_existing;
        fprintf('[START] %s [H1=%d H2=%d H3=%d H4=%d] on %s (M=%d) - %d missing runs @ %s\n', ...
            cfg_name, H1_flag, H2_flag, H3_flag, H4_flag, prob_name, prob_M, missing_initial, datestr(now, 'HH:MM:SS'));
        tic;

        for attempt = 1:max_retry_attempts
            [n_existing, existing_runs] = count_expected_runs(result_folder, expected_runs);
            missing_global = setdiff(expected_runs, existing_runs);
            if isempty(missing_global)
                break;
            end

            missing_local = missing_global - (run_id_base + cfg_idx * num_runs);
            fprintf('[TRY %d/%d] %s on %s (M=%d) - launching %d missing runs\n', ...
                attempt, max_retry_attempts, cfg_name, prob_name, prob_M, length(missing_local));

            run_errors = cell(1, length(missing_local));

            parfor mi = 1:length(missing_local)
                local_run = missing_local(mi);
                global_run = run_id_base + cfg_idx * num_runs + local_run;
                try
                    platemo('algorithm', {@IVFSPEA2_P2, C_val, R_val, M_val, V_val, ...
                                          Cycles_val, S_val, N_Offspring_val, ...
                                          EARN_val, N_Obj_Limit_val, ...
                                          H1_flag, H2_flag, H3_flag, H4_flag}, ...
                            'problem', prob_func, ...
                            'N', N_pop, ...
                            'M', prob_M, ...
                            'maxFE', maxFE, ...
                            'save', 1, ...
                            'run', global_run, ...
                            'metName', {'IGD','HV'});
                    run_errors{mi} = '';
                catch ME
                    run_errors{mi} = sprintf('local run %d (global %d): %s', ...
                        local_run, global_run, ME.message);
                end
            end

            % Report errors from this retry pass
            failed_idx = find(~cellfun(@isempty, run_errors));
            if ~isempty(failed_idx)
                fprintf('[WARN] %d/%d launched runs FAILED:\n', length(failed_idx), length(missing_local));
                for fi = 1:length(failed_idx)
                    fprintf('  %s\n', run_errors{failed_idx(fi)});
                end
                global_errors = global_errors + length(failed_idx);
            end

            % Collect only expected run IDs from PlatEMO Data root.
            % Important: do NOT remove the shared source folder, as other
            % phase2 batches may still be writing concurrently.
            source_folder = fullfile(PLATEMO_DATA, 'IVFSPEA2_P2');
            if isfolder(source_folder)
                [n_collected, ~] = collect_with_retries(source_folder, result_folder, ...
                    prob_name, prob_M, expected_runs, max_collect_attempts);
                fprintf('         Collected %d/%d expected files\n', n_collected, num_runs);
            else
                fprintf('[WARN] Source folder not found: %s\n', source_folder);
            end
        end

        elapsed = toc;

        % Post-collection validation (expected run IDs only)
        [n_actual, existing_runs] = count_expected_runs(result_folder, expected_runs);
        if n_actual == num_runs
            fprintf('[DONE]  %s on %s (M=%d) - %d/%d expected files OK - %.1f sec (%.1f sec/run)\n', ...
                algo_label, prob_name, prob_M, n_actual, num_runs, elapsed, elapsed/num_runs);
        else
            fprintf('[WARN]  %s on %s (M=%d) - %d/%d expected files (INCOMPLETE) - %.1f sec\n', ...
                algo_label, prob_name, prob_M, n_actual, num_runs, elapsed);
            missing_global = setdiff(expected_runs, existing_runs);
            missing_local = missing_global - (run_id_base + cfg_idx * num_runs);
            fprintf('         Missing local runs:  [%s]\n', num2str(missing_local));
            fprintf('         Missing global runs: [%s]\n', num2str(missing_global));
            global_missing_runs = global_missing_runs + length(missing_global);
        end
    end
end

%% Summary
fprintf('\n=== PHASE 2 BATCH B COMPLETE @ %s ===\n', datestr(now));
fprintf('Results saved in: %s\n', output_base);
if global_errors > 0 || global_missing_runs > 0
    fprintf('[ATTENTION] %d run errors and %d missing runs detected.\n', ...
        global_errors, global_missing_runs);
else
    fprintf('All runs completed successfully with full integrity.\n');
end

%% Data Inventory
fprintf('\n--- Data Inventory (Phase 2 Batch B) ---\n');
fprintf('%-50s %-10s %s\n', 'Config', 'Files', 'Status');
fprintf('%s\n', repmat('-', 1, 75));
for c = 1:size(configs, 1)
    cfg_name = configs{c,1};
    cfg_idx = parse_config_index(cfg_name);
    expected_runs = run_id_base + cfg_idx * num_runs + (1:num_runs);
    for p = 1:size(problems, 1)
        folder_name = sprintf('IVFSPEA2_%s_%s_M%d', cfg_name, func2str(problems{p,1}), problems{p,2});
        folder_path = fullfile(output_base, folder_name);
        [n, ~] = count_expected_runs(folder_path, expected_runs);
        if n >= num_runs, status = 'OK';
        elseif n > 0,     status = 'INCOMPLETE';
        else,             status = 'MISSING';
        end
        fprintf('%-50s %-10d %s\n', folder_name, n, status);
    end
end

%% Cleanup
diary off;
delete(gcp('nocreate'));

if global_errors > 0 || global_missing_runs > 0
    error('Phase 2 Batch B failed integrity checks: %d errors, %d missing runs.', ...
        global_errors, global_missing_runs);
end

function cfg_idx = parse_config_index(cfg_name)
    token = regexp(cfg_name, '^P2_C(\d+)$', 'tokens', 'once');
    if isempty(token)
        error('Invalid config name: %s', cfg_name);
    end
    cfg_idx = str2double(token{1});
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

function moved = collect_expected_files(source_folder, result_folder, prob_name, prob_M, expected_runs)
    moved = 0;
    if ~isfolder(result_folder)
        mkdir(result_folder);
    end

    pattern = sprintf('IVFSPEA2_P2_%s_M%d_D*_*.mat', prob_name, prob_M);
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

function [n_collected, present_expected] = collect_with_retries(source_folder, result_folder, prob_name, prob_M, expected_runs, max_attempts)
    n_collected = 0;
    present_expected = [];
    for attempt = 1:max_attempts
        collect_expected_files(source_folder, result_folder, prob_name, prob_M, expected_runs);
        [n_collected, present_expected] = count_expected_runs(result_folder, expected_runs);
        if n_collected == length(expected_runs)
            return;
        end
        if attempt < max_attempts
            pause(2);
        end
    end
end
