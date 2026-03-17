%% run_baselines.m — Phase 1.2: Modern Baselines
%  2 algorithms (AGE-MOEA-II, AR-MOEA) × 51 problem instances × 60 runs
%  Uses parfor over runs for parallelism.
%  Resume-safe: skips completed files.
%
%  Usage:
%    matlab -batch "run('experiments/run_baselines.m')"

%% Configuration
NUM_RUNS = 100;
MAX_FE   = 100000;
N_SAVE   = 10;

% Algorithms (no special parameters needed)
algorithms = {
    'AGEMOEAII',  {@AGEMOEAII};
    'ARMOEA',     {@ARMOEA};
};

% 51 problem instances matching Data_original
% M=2 problems (28 instances)
problems_M2 = {
    @ZDT1, 2, 30;   @ZDT2, 2, 30;   @ZDT3, 2, 30;   @ZDT4, 2, 10;   @ZDT6, 2, 10;
    @DTLZ1, 2, 6;   @DTLZ2, 2, 11;  @DTLZ3, 2, 11;  @DTLZ4, 2, 11;
    @DTLZ5, 2, 11;  @DTLZ6, 2, 11;  @DTLZ7, 2, 21;
    @WFG1, 2, 11;   @WFG2, 2, 11;   @WFG3, 2, 11;   @WFG4, 2, 11;
    @WFG5, 2, 11;   @WFG6, 2, 11;   @WFG7, 2, 11;   @WFG8, 2, 11;   @WFG9, 2, 11;
    @MaF1, 2, 11;   @MaF2, 2, 11;   @MaF3, 2, 11;   @MaF4, 2, 11;
    @MaF5, 2, 11;   @MaF6, 2, 11;   @MaF7, 2, 21;
};

% M=3 problems (23 instances)
problems_M3 = {
    @DTLZ1, 3, 7;   @DTLZ2, 3, 12;  @DTLZ3, 3, 12;  @DTLZ4, 3, 12;
    @DTLZ5, 3, 12;  @DTLZ6, 3, 12;  @DTLZ7, 3, 22;
    @WFG1, 3, 12;   @WFG2, 3, 12;   @WFG3, 3, 12;   @WFG4, 3, 12;
    @WFG5, 3, 12;   @WFG6, 3, 12;   @WFG7, 3, 12;   @WFG8, 3, 12;   @WFG9, 3, 12;
    @MaF1, 3, 12;   @MaF2, 3, 12;   @MaF3, 3, 12;   @MaF4, 3, 12;
    @MaF5, 3, 12;   @MaF6, 3, 12;   @MaF7, 3, 22;
};

% Combine all + engineering benchmark
all_problems = [problems_M2; problems_M3; {@RWMOP9, 2, 4}];

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

%% Start parallel pool
if isempty(gcp('nocreate'))
    parpool;
end

data_dir = fullfile(platemo_dir, 'Data');

%% Main loop
total_combos = size(algorithms, 1) * size(all_problems, 1);
combo_count = 0;
t_start = tic;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};

    for p = 1:size(all_problems, 1)
        prob_handle = all_problems{p, 1};
        M_obj       = all_problems{p, 2};
        D_vars      = all_problems{p, 3};
        prob_name   = func2str(prob_handle);

        combo_count = combo_count + 1;
        fprintf('\n=== [%d/%d] %s on %s (M=%d, D=%d) ===\n', ...
                combo_count, total_combos, algo_name, prob_name, M_obj, D_vars);

        target_folder = fullfile(data_dir, algo_name);

        % Detect which runs are missing
        runs_needed = [];
        for r = 1:NUM_RUNS
            pattern = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
            if ~isfile(fullfile(target_folder, pattern))
                runs_needed(end+1) = r; %#ok<AGROW>
            end
        end

        if isempty(runs_needed)
            fprintf('  → Already complete. Skipping.\n');
            continue;
        end

        fprintf('  → %d runs needed.\n', length(runs_needed));

        parfor ri = 1:length(runs_needed)
            run_idx = runs_needed(ri);
            try
                platemo('algorithm', algo_spec, ...
                        'problem', prob_handle, ...
                        'M', M_obj, ...
                        'maxFE', MAX_FE, ...
                        'save', N_SAVE, ...
                        'run', run_idx, ...
                        'metName', {'IGD', 'HV'});
                fprintf('  ✓ %s/%s run %d\n', algo_name, prob_name, run_idx);
            catch ME
                fprintf('  ✗ %s/%s run %d: %s\n', algo_name, prob_name, run_idx, ME.message);
            end
        end
    end
end

elapsed = toc(t_start);
fprintf('\n=== Modern baselines complete in %.1f min ===\n', elapsed/60);
delete(gcp('nocreate'));
