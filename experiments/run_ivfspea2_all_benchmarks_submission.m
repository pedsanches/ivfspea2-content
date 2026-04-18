%% run_ivfspea2_all_benchmarks_submission.m
% Submission rerun protocol (IVFSPEA2 only):
% - Fixed IVF defaults: C=0.11, R=0.10 (10 mothers + 1 father)
% - Full benchmark scope: ZDT/DTLZ/WFG/MaF (51 instances) + RWMOP9
% - Resume-safe (skips existing run files)
%
% Usage:
%   matlab -batch "run('experiments/run_ivfspea2_all_benchmarks_submission.m')"

%% Configuration
NUM_RUNS = 100;
RUN_BASE = 2001; % Dedicated range for submission rerun (2001..2100)
MAX_FE   = 100000;
N_SAVE   = 10;
SUBMISSION_TAG = 'SUB20260218';

% Fixed IVF defaults (DO NOT CHANGE)
C_val = 0.11;
R_val = 0.10;
M_val = 0;
V_val = 0;
Cycles_val = 3;
S_val = 1;
N_Offspring_val = 1;
EARN_val = 0;
N_Obj_Limit_val = 0;

algo_name = 'IVFSPEA2';
algo_spec = {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

% 51 synthetic instances (same scope as manuscript)
problems_M2 = {
    @ZDT1, 2, 30;   @ZDT2, 2, 30;   @ZDT3, 2, 30;   @ZDT4, 2, 10;   @ZDT6, 2, 10;
    @DTLZ1, 2, 6;   @DTLZ2, 2, 11;  @DTLZ3, 2, 11;  @DTLZ4, 2, 11;
    @DTLZ5, 2, 11;  @DTLZ6, 2, 11;  @DTLZ7, 2, 21;
    @WFG1, 2, 11;   @WFG2, 2, 11;   @WFG3, 2, 11;   @WFG4, 2, 11;
    @WFG5, 2, 11;   @WFG6, 2, 11;   @WFG7, 2, 11;   @WFG8, 2, 11;   @WFG9, 2, 11;
    @MaF1, 2, 11;   @MaF2, 2, 11;   @MaF3, 2, 11;   @MaF4, 2, 11;
    @MaF5, 2, 11;   @MaF6, 2, 11;   @MaF7, 2, 21;
};

problems_M3 = {
    @DTLZ1, 3, 7;   @DTLZ2, 3, 12;  @DTLZ3, 3, 12;  @DTLZ4, 3, 12;
    @DTLZ5, 3, 12;  @DTLZ6, 3, 12;  @DTLZ7, 3, 22;
    @WFG1, 3, 12;   @WFG2, 3, 12;   @WFG3, 3, 12;   @WFG4, 3, 12;
    @WFG5, 3, 12;   @WFG6, 3, 12;   @WFG7, 3, 12;   @WFG8, 3, 12;   @WFG9, 3, 12;
    @MaF1, 3, 12;   @MaF2, 3, 12;   @MaF3, 3, 12;   @MaF4, 3, 12;
    @MaF5, 3, 12;   @MaF6, 3, 12;   @MaF7, 3, 22;
};

% Engineering benchmark
problem_rwmop9 = {@RWMOP9, 2, 4};

all_problems = [problems_M2; problems_M3; problem_rwmop9];

%% Setup and logging
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir      = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ivfspea2_full_rerun_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVF/SPEA2 FULL BENCHMARK RERUN ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Algorithm: %s\n', algo_name);
fprintf('Fixed defaults: C=%.2f, R=%.2f\n', C_val, R_val);
fprintf('Runs/config: %d | maxFE: %d | save: %d\n', NUM_RUNS, MAX_FE, N_SAVE);
fprintf('Run range: %d..%d | tag: %s\n', RUN_BASE, RUN_BASE + NUM_RUNS - 1, SUBMISSION_TAG);
fprintf('Total configs: %d\n', size(all_problems,1));
fprintf('Log file: %s\n\n', log_file);

addpath(genpath(platemo_dir));
cd(platemo_dir);

data_dir = fullfile(platemo_dir, 'Data');
results_dir = fullfile(project_root, 'results');
if ~isfolder(results_dir), mkdir(results_dir); end
manifest_file = fullfile(results_dir, sprintf('ivfspea2_submission_manifest_%s.csv', SUBMISSION_TAG));
fid_manifest = fopen(manifest_file, 'w');
fprintf(fid_manifest, 'Tag,Algorithm,Problem,M,D,RunBase,NumRuns,ExpectedStart,ExpectedEnd,FoundRuns,MissingRuns,Status\n');

if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, c.NumWorkers);
    fprintf('Parallel pool started with %d workers\\n', c.NumWorkers);
end

%% Main loop (resume-safe)
t_start = tic;
for p = 1:size(all_problems,1)
    prob_handle = all_problems{p,1};
    M_obj       = all_problems{p,2};
    D_vars      = all_problems{p,3};
    prob_name   = func2str(prob_handle);

    fprintf('\n[%d/%d] %s (M=%d, D=%d)\n', p, size(all_problems,1), prob_name, M_obj, D_vars);

    target_folder = fullfile(data_dir, algo_name);

    runs_needed = [];
    for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
        fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
        if ~isfile(fullfile(target_folder, fname))
            runs_needed(end+1) = r; %#ok<AGROW>
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
                    'metName', {'IGD','HV'});
        catch ME
            fprintf('  [FAIL] %s run %d: %s\n', prob_name, run_idx, ME.message);
        end
    end

    % post-check
    found_runs = [];
    for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
        fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
        if isfile(fullfile(target_folder, fname))
            found_runs(end+1) = r; %#ok<AGROW>
        end
    end

    n_files = numel(found_runs);
    fprintf('  -> files now (submission range): %d/%d\n', n_files, NUM_RUNS);

    all_expected_runs = RUN_BASE:(RUN_BASE + NUM_RUNS - 1);
    missing_runs = setdiff(all_expected_runs, found_runs);

    if isempty(found_runs)
        found_runs_str = '';
    else
        found_runs_str = char(strjoin(string(found_runs), ';'));
    end

    if isempty(missing_runs)
        missing_runs_str = '';
    else
        missing_runs_str = char(strjoin(string(missing_runs), ';'));
    end

    if n_files == NUM_RUNS
        status = 'OK';
    elseif n_files == 0
        status = 'MISSING';
    else
        status = 'INCOMPLETE';
    end

    fprintf(fid_manifest, '%s,%s,%s,%d,%d,%d,%d,%d,%d,"%s","%s",%s\n', ...
        SUBMISSION_TAG, algo_name, prob_name, M_obj, D_vars, RUN_BASE, NUM_RUNS, RUN_BASE, RUN_BASE + NUM_RUNS - 1, ...
        found_runs_str, missing_runs_str, status);
end

elapsed = toc(t_start);
fprintf('\n=== FULL RERUN COMPLETE in %.2f hours ===\n', elapsed/3600);
fprintf('Manifest: %s\n', manifest_file);

delete(gcp('nocreate'));
fclose(fid_manifest);
diary off;
