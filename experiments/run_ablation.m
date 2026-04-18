%% run_ablation.m — Phase 1.1: Ablation Study
%  4 variants × 5 problems × 60 runs
%  Uses parfor over runs for parallelism.
%  Resume-safe: skips completed files.
%
%  Usage:
%    matlab -batch "run('experiments/run_ablation.m')"

%% Configuration
NUM_RUNS = 60;
MAX_FE   = 100000;
N_SAVE   = 10;  % number of population snapshots saved

% IVF parameters (standard defaults)
C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

% Algorithms to test
algorithms = {
    'IVFSPEA2',        {@IVFSPEA2,        C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'IVFSPEA2ABL1C',   {@IVFSPEA2ABL1C,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'IVFSPEA2ABL4C',   {@IVFSPEA2ABL4C,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'IVFSPEA2ABLDOM',  {@IVFSPEA2ABLDOM,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
};

% Problems: {handle, M_objectives}
problems = {
    @ZDT1,  2;
    @DTLZ1, 3;
    @WFG4,  2;
    @MaF1,  3;
    @MaF4,  3;
};

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

%% Start parallel pool
if isempty(gcp('nocreate'))
    parpool;
end

%% Data output directory
data_dir = fullfile(platemo_dir, 'Data');

%% Main loop
total_combos = size(algorithms, 1) * size(problems, 1);
combo_count = 0;
t_start = tic;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};

    for p = 1:size(problems, 1)
        prob_handle = problems{p, 1};
        M_obj       = problems{p, 2};
        prob_name   = func2str(prob_handle);

        combo_count = combo_count + 1;
        fprintf('\n=== [%d/%d] %s on %s (M=%d) ===\n', combo_count, total_combos, algo_name, prob_name, M_obj);

        % Determine expected folder name (PlatEMO convention)
        target_folder = fullfile(data_dir, algo_name);

        % Count existing runs to detect resume
        existing = 0;
        if isfolder(target_folder)
            files = dir(fullfile(target_folder, sprintf('%s_%s_M%d_*_*.mat', algo_name, prob_name, M_obj)));
            existing = length(files);
        end

        if existing >= NUM_RUNS
            fprintf('  → Already complete (%d/%d runs). Skipping.\n', existing, NUM_RUNS);
            continue;
        end

        fprintf('  → Found %d existing runs, running %d-%d.\n', existing, existing+1, NUM_RUNS);

        % Determine which run indices still need execution
        runs_needed = [];
        for r = 1:NUM_RUNS
            pattern = sprintf('%s_%s_M%d_*_%d.mat', algo_name, prob_name, M_obj, r);
            if isempty(dir(fullfile(target_folder, pattern)))
                runs_needed(end+1) = r; %#ok<AGROW>
            end
        end

        % Execute missing runs in parallel
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
                fprintf('  ✓ %s/%s run %d complete\n', algo_name, prob_name, run_idx);
            catch ME
                fprintf('  ✗ %s/%s run %d FAILED: %s\n', algo_name, prob_name, run_idx, ME.message);
            end
        end
    end
end

elapsed = toc(t_start);
fprintf('\n=== Ablation study complete in %.1f min ===\n', elapsed/60);
delete(gcp('nocreate'));
