%% run_ivfspea2v2_submission_traces.m
% Trace-enabled synthetic-suite rerun for IVF/SPEA2 v2.
%   - 51 synthetic problem instances x 30 runs
%   - Saves 10 checkpoints per run to match the standard NSGA cohorts
%   - Resume-safe (skips existing run files)
%   - Supports partitioned execution: RUNNER_ID=1..3, 6 workers each
%
% Usage (3 terminals, 6 workers each):
%   RUNNER_ID=1 matlab -batch "run('experiments/run_ivfspea2v2_submission_traces.m')"
%   RUNNER_ID=2 matlab -batch "run('experiments/run_ivfspea2v2_submission_traces.m')"
%   RUNNER_ID=3 matlab -batch "run('experiments/run_ivfspea2v2_submission_traces.m')"

%% Configuration
NUM_RUNS = 30;
RUN_BASE = 3001;
MAX_FE = 100000;
N_SAVE = 10;
NUM_WORKERS = 6;
NUM_RUNNERS = 3;
SUBMISSION_TAG = 'SUB20260228_V2_TRACES';

profiles = struct();
profiles.prod_default = struct( ...
    'collection_rate', 0.12, ...
    'ivf_activation_ratio', 0.225, ...
    'mother_mutation_fraction', 0.3, ...
    'variable_mutation_fraction', 0.1, ...
    'max_ivf_cycles', 2, ...
    'offspring_per_mother', 1, ...
    'exploration_mode', 0);

profile_name = lower(strtrim(getenv('IVF_PROFILE')));
if isempty(profile_name)
    profile_name = 'prod_default';
end
if ~isfield(profiles, profile_name)
    error('Invalid IVF_PROFILE="%s". Use prod_default.', profile_name);
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

all_problems = [problems_M2; problems_M3];

runner_id = str2double(getenv('RUNNER_ID'));
if isnan(runner_id) || runner_id < 1 || runner_id > NUM_RUNNERS
    error('Set RUNNER_ID=1..%d environment variable before running.', NUM_RUNNERS);
end
my_problems = runner_id:NUM_RUNNERS:size(all_problems, 1);

project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir)
    mkdir(log_dir);
end
log_file = fullfile(log_dir, sprintf('ivfspea2v2_submission_traces_runner%d_%s.log', ...
    runner_id, datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVF/SPEA2 V2 TRACE RERUN — Runner %d/%d ===\n', runner_id, NUM_RUNNERS);
fprintf('Start: %s | Tag: %s\n', datestr(now), SUBMISSION_TAG);
fprintf('Runs/config: %d | maxFE: %d | save: %d | run range: %d..%d\n', ...
    NUM_RUNS, MAX_FE, N_SAVE, RUN_BASE, RUN_BASE + NUM_RUNS - 1);
fprintf('Synthetic instances: %d\n', size(all_problems, 1));
fprintf('This runner handles %d problem configs\n', length(my_problems));
fprintf('Log file: %s\n\n', log_file);

addpath(genpath(platemo_dir));
cd(platemo_dir);
data_dir = fullfile(platemo_dir, 'Data');

if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
    fprintf('Parallel pool started with %d workers\n\n', min(NUM_WORKERS, c.NumWorkers));
end

t_start = tic;
for pi = 1:length(my_problems)
    p = my_problems(pi);
    prob_handle = all_problems{p, 1};
    M_obj = all_problems{p, 2};
    D_vars = all_problems{p, 3};
    prob_name = func2str(prob_handle);

    fprintf('[%d/%d] %s (M=%d, D=%d) [global %d/%d]\n', ...
        pi, length(my_problems), prob_name, M_obj, D_vars, p, size(all_problems, 1));

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
            fprintf('  [FAIL] %s run %d: %s\n', prob_name, run_idx, ME.message);
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

elapsed = toc(t_start);
fprintf('\n=== Runner %d COMPLETE in %.2f hours ===\n', runner_id, elapsed / 3600);
delete(gcp('nocreate'));
diary off;
