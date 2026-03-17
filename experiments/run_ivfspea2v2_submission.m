%% run_ivfspea2v2_submission.m
% Submission run for IVFSPEA2V2 with tuned config C26:
% - Tuned parameters: C=0.12, R=0.225, M=0.3, V=0.1, Cycles=2 (EAR light)
% - Full benchmark scope: ZDT/DTLZ/WFG/MaF (51 instances) + RWMOP9
% - Resume-safe (skips existing run files)
% - Supports partitioned execution: set RUNNER_ID=1..3 for 3 parallel instances
%
% Usage (3 terminals, 6 workers each):
%   RUNNER_ID=1 matlab -batch "run('experiments/run_ivfspea2v2_submission.m')"
%   RUNNER_ID=2 matlab -batch "run('experiments/run_ivfspea2v2_submission.m')"
%   RUNNER_ID=3 matlab -batch "run('experiments/run_ivfspea2v2_submission.m')"

%% Configuration
NUM_RUNS = 60;
RUN_BASE = 3001; % Dedicated range for v2 submission (3001..3060)
MAX_FE   = 100000;
N_SAVE   = 10;
NUM_WORKERS = 6;
NUM_RUNNERS = 3;
SUBMISSION_TAG = 'SUB20260228_V2';

% IVF production profiles (named fields -> positional PlatEMO parameters)
profiles = struct();
profiles.prod_default = struct( ...
    'collection_rate', 0.12, ...
    'ivf_activation_ratio', 0.225, ...
    'mother_mutation_fraction', 0.3, ...
    'variable_mutation_fraction', 0.1, ...
    'max_ivf_cycles', 2, ...
    'offspring_per_mother', 1, ...
    'exploration_mode', 0); % 0: EAR, 1: EARN

profiles.prod_conservative = struct( ...
    'collection_rate', 0.16, ...
    'ivf_activation_ratio', 0.20, ...
    'mother_mutation_fraction', 0.0, ...
    'variable_mutation_fraction', 0.0, ...
    'max_ivf_cycles', 2, ...
    'offspring_per_mother', 1, ...
    'exploration_mode', 0); % AR-like profile (no mother mutation)

profile_name = lower(strtrim(getenv('IVF_PROFILE')));
if isempty(profile_name)
    profile_name = 'prod_default';
end
if ~isfield(profiles, profile_name)
    error('Invalid IVF_PROFILE="%s". Use prod_default or prod_conservative.', profile_name);
end
ivf_cfg = profiles.(profile_name);

algo_name = 'IVFSPEA2V2';
algo_spec = {@IVFSPEA2V2, ...
    ivf_cfg.collection_rate, ...
    ivf_cfg.ivf_activation_ratio, ...
    ivf_cfg.mother_mutation_fraction, ...
    ivf_cfg.variable_mutation_fraction, ...
    ivf_cfg.max_ivf_cycles, ...
    ivf_cfg.offspring_per_mother, ...
    ivf_cfg.exploration_mode};

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

%% Get runner ID (1..NUM_RUNNERS)
runner_id = str2double(getenv('RUNNER_ID'));
if isnan(runner_id) || runner_id < 1 || runner_id > NUM_RUNNERS
    error('Set RUNNER_ID=1..%d environment variable before running.', NUM_RUNNERS);
end

% Assign problems to this runner (round-robin)
my_problems = runner_id:NUM_RUNNERS:size(all_problems, 1);

%% Setup and logging
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir      = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ivfspea2v2_submission_runner%d_%s.log', runner_id, datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVF/SPEA2 V2 SUBMISSION RUN — Runner %d/%d ===\n', runner_id, NUM_RUNNERS);
fprintf('Start: %s\n', datestr(now));
fprintf('Algorithm: %s\n', algo_name);
fprintf('IVF profile: %s\n', profile_name);
fprintf('IVF params: C=%.2f, R=%.3f, M=%.1f, V=%.1f, Cycles=%d, N_Offspring=%d, EARN=%d\n', ...
    ivf_cfg.collection_rate, ivf_cfg.ivf_activation_ratio, ...
    ivf_cfg.mother_mutation_fraction, ivf_cfg.variable_mutation_fraction, ...
    ivf_cfg.max_ivf_cycles, ivf_cfg.offspring_per_mother, ivf_cfg.exploration_mode);
fprintf('Runs/config: %d | maxFE: %d | save: %d | workers: %d\n', NUM_RUNS, MAX_FE, N_SAVE, NUM_WORKERS);
fprintf('Run range: %d..%d | tag: %s\n', RUN_BASE, RUN_BASE + NUM_RUNS - 1, SUBMISSION_TAG);
fprintf('This runner handles %d of %d problem configs\n', length(my_problems), size(all_problems, 1));
fprintf('Log file: %s\n\n', log_file);

addpath(genpath(platemo_dir));
cd(platemo_dir);

data_dir = fullfile(platemo_dir, 'Data');
results_dir = fullfile(project_root, 'results');
if ~isfolder(results_dir), mkdir(results_dir); end

% Start parallel pool with 6 workers
if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
    fprintf('Parallel pool started with %d workers\n', min(NUM_WORKERS, c.NumWorkers));
end

%% Main loop (resume-safe)
t_start = tic;
for pi = 1:length(my_problems)
    p = my_problems(pi);
    prob_handle = all_problems{p,1};
    M_obj       = all_problems{p,2};
    D_vars      = all_problems{p,3};
    prob_name   = func2str(prob_handle);

    fprintf('\n[%d/%d] %s (M=%d, D=%d) [global %d/%d]\n', ...
        pi, length(my_problems), prob_name, M_obj, D_vars, p, size(all_problems,1));

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
    n_found = 0;
    for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
        fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
        if isfile(fullfile(target_folder, fname))
            n_found = n_found + 1;
        end
    end
    fprintf('  -> files now (submission range): %d/%d\n', n_found, NUM_RUNS);
end

elapsed = toc(t_start);
fprintf('\n=== Runner %d COMPLETE in %.2f hours ===\n', runner_id, elapsed/3600);

delete(gcp('nocreate'));
diary off;
