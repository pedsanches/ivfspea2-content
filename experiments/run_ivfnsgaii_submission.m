%% run_ivfnsgaii_submission.m
% Comparative run: IVF/NSGA-II vs NSGA-II
%   - 2 algorithms × 52 problem instances × 30 runs
%   - Resume-safe (skips existing run files)
%   - Supports partitioned execution: RUNNER_ID=1..3, 6 workers each
%
% Usage (3 terminals, 6 workers each):
%   RUNNER_ID=1 matlab -batch "run('experiments/run_ivfnsgaii_submission.m')"
%   RUNNER_ID=2 matlab -batch "run('experiments/run_ivfnsgaii_submission.m')"
%   RUNNER_ID=3 matlab -batch "run('experiments/run_ivfnsgaii_submission.m')"

%% Configuration
NUM_RUNS        = 30;
RUN_BASE        = 4001;  % Dedicated range: 4001..4030
MAX_FE          = 100000;
N_SAVE          = 10;
NUM_WORKERS     = 6;
NUM_RUNNERS     = 3;
SUBMISSION_TAG  = 'SUB20260330_NSGAII';

% Algorithms: IVF/NSGA-II (AR, default params) and its base algorithm
algorithms = {
    'IVFNSGAII', {@IVFNSGAII, 0.5, 0.07, 5};   % R=0.5, C=0.07, Cycles=5
    'NSGAII',    {@NSGAII};
};

%% Problem suite (52 instances — same scope as manuscript)
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

all_problems = [problems_M2; problems_M3; {@RWMOP9, 2, 4}];

%% Runner setup
runner_id = str2double(getenv('RUNNER_ID'));
if isnan(runner_id) || runner_id < 1 || runner_id > NUM_RUNNERS
    error('Set RUNNER_ID=1..%d environment variable before running.', NUM_RUNNERS);
end

my_problems = runner_id:NUM_RUNNERS:size(all_problems, 1);

%% Paths and logging
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir      = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('ivfnsgaii_runner%d_%s.log', ...
    runner_id, datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVF/NSGA-II vs NSGA-II — Runner %d/%d ===\n', runner_id, NUM_RUNNERS);
fprintf('Start: %s | Tag: %s\n', datestr(now), SUBMISSION_TAG);
fprintf('Runs/config: %d | maxFE: %d | run range: %d..%d\n', ...
    NUM_RUNS, MAX_FE, RUN_BASE, RUN_BASE + NUM_RUNS - 1);
fprintf('This runner handles %d of %d problem configs\n\n', ...
    length(my_problems), size(all_problems, 1));

addpath(genpath(platemo_dir));
cd(platemo_dir);
data_dir = fullfile(platemo_dir, 'Data');

%% Parallel pool
if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
    fprintf('Parallel pool started with %d workers\n\n', min(NUM_WORKERS, c.NumWorkers));
end

%% Main loop (algorithms × problems, resume-safe)
t_start = tic;
for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};

    fprintf('\n--- Algorithm: %s ---\n', algo_name);

    for pi_local = 1:length(my_problems)
        p           = my_problems(pi_local);
        prob_handle = all_problems{p, 1};
        M_obj       = all_problems{p, 2};
        D_vars      = all_problems{p, 3};
        prob_name   = func2str(prob_handle);

        fprintf('[%d/%d] %s on %s (M=%d, D=%d) [global %d/%d]\n', ...
            pi_local, length(my_problems), algo_name, prob_name, ...
            M_obj, D_vars, p, size(all_problems,1));

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
                        'problem',   prob_handle, ...
                        'M',         M_obj, ...
                        'D',         D_vars, ...
                        'maxFE',     MAX_FE, ...
                        'save',      N_SAVE, ...
                        'run',       run_idx, ...
                        'metName',   {'IGD', 'HV'});
            catch ME
                fprintf('  [FAIL] %s/%s run %d: %s\n', algo_name, prob_name, run_idx, ME.message);
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
        fprintf('  -> files now: %d/%d\n', n_found, NUM_RUNS);
    end
end

elapsed = toc(t_start);
fprintf('\n=== Runner %d COMPLETE in %.2f hours ===\n', runner_id, elapsed/3600);
delete(gcp('nocreate'));
diary off;
