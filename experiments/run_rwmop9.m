%% run_rwmop9.m — Phase 1.4: Engineering Problem RWMOP9
%  9 algorithms × 60 runs on RWMOP9 (2-obj, 4-var, constrained)
%  Uses parfor over runs for parallelism.
%  Resume-safe: skips completed files.
%
%  Usage:
%    matlab -batch "run('experiments/run_rwmop9.m')"

%% Configuration
NUM_RUNS = 60;
MAX_FE   = 100000;
N_SAVE   = 10;
M_OBJ    = 2;  % RWMOP9 is bi-objective

% IVF parameters (for IVF/SPEA2 only)
C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

% Algorithms
algorithms = {
    'SPEA2',       {@SPEA2};
    'NSGAII',      {@NSGAII};
    'NSGAIII',     {@NSGAIII};
    'MOEAD',       {@MOEAD};
    'MFOSPEA2',    {@MFOSPEA2};
    'SPEA2SDE',    {@SPEA2SDE};
    'AGEMOEAII',   {@AGEMOEAII};
    'ARMOEA',      {@ARMOEA};
    'IVFSPEA2',    {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
};

prob_handle = @RWMOP9;
prob_name   = 'RWMOP9';

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
t_start = tic;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};

    fprintf('\n=== [%d/%d] %s on %s ===\n', a, size(algorithms, 1), algo_name, prob_name);

    target_folder = fullfile(data_dir, algo_name);

    % Detect which runs are missing
    runs_needed = [];
    for r = 1:NUM_RUNS
        pattern = sprintf('%s_%s_M%d_*_%d.mat', algo_name, prob_name, M_OBJ, r);
        if isempty(dir(fullfile(target_folder, pattern)))
            runs_needed(end+1) = r; %#ok<AGROW>
        end
    end

    if isempty(runs_needed)
        fprintf('  → Already complete (%d/%d runs). Skipping.\n', NUM_RUNS, NUM_RUNS);
        continue;
    end

    fprintf('  → %d runs needed (%d existing).\n', length(runs_needed), NUM_RUNS - length(runs_needed));

    parfor ri = 1:length(runs_needed)
        run_idx = runs_needed(ri);
        try
            platemo('algorithm', algo_spec, ...
                    'problem', prob_handle, ...
                    'M', M_OBJ, ...
                    'maxFE', MAX_FE, ...
                    'save', N_SAVE, ...
                    'run', run_idx, ...
                    'metName', {'IGD', 'HV'});
            fprintf('  ✓ %s/%s run %d complete\n', algo_name, prob_name, run_idx);
        catch ME
            fprintf('  ✗ %s/%s run %d FAILED: %s\n', algo_name, prob_name, run_idx, ME.message);
        end
    end
end

elapsed = toc(t_start);
fprintf('\n=== RWMOP9 experiment complete in %.1f min ===\n', elapsed/60);
delete(gcp('nocreate'));
