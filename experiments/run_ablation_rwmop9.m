%% run_ablation_rwmop9.m — Run ablation variants on RWMOP9 (post bound-clamping fix)
%  3 ablation variants × 1 problem × 60 runs
%  Uses parfor over runs for parallelism.
%  Resume-safe: skips completed files.
%
%  Usage:
%    matlab -batch "run('experiments/run_ablation_rwmop9.m')"

%% Configuration
NUM_RUNS = 60;
MAX_FE   = 100000;
N_SAVE   = 10;
M_OBJ    = 2;  % RWMOP9 is bi-objective

% IVF parameters (AR mode, same as all other RWMOP9 and ablation experiments)
C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

% Ablation variants only (IVFSPEA2 already re-run separately)
algorithms = {
    'IVFSPEA2ABL1C',   {@IVFSPEA2ABL1C,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'IVFSPEA2ABL4C',   {@IVFSPEA2ABL4C,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    'IVFSPEA2ABLDOM',  {@IVFSPEA2ABLDOM,   C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
};

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

data_dir = fullfile(platemo_dir, 'Data');

%% Start parallel pool
if isempty(gcp('nocreate'))
    parpool;
end

%% Main loop
t_start = tic;

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    algo_spec = algorithms{a, 2};

    fprintf('\n========================================\n');
    fprintf('  %s on RWMOP9 (M=%d)\n', algo_name, M_OBJ);
    fprintf('  %d runs, maxFE=%d\n', NUM_RUNS, MAX_FE);
    fprintf('  IVF params: C=%.2f R=%.1f M=%d V=%d Cycles=%d\n', ...
        C_val, R_val, M_val, V_val, Cycles_val);
    fprintf('========================================\n');

    target_folder = fullfile(data_dir, algo_name);

    % Detect which runs are missing
    runs_needed = [];
    for r = 1:NUM_RUNS
        pattern = sprintf('%s_RWMOP9_M%d_*_%d.mat', algo_name, M_OBJ, r);
        if isempty(dir(fullfile(target_folder, pattern)))
            runs_needed(end+1) = r; %#ok<AGROW>
        end
    end

    if isempty(runs_needed)
        fprintf('  Already complete (%d/%d runs). Skipping.\n', NUM_RUNS, NUM_RUNS);
        continue;
    end

    fprintf('  Runs needed: %d/%d\n\n', length(runs_needed), NUM_RUNS);

    parfor ri = 1:length(runs_needed)
        run_idx = runs_needed(ri);
        try
            platemo('algorithm', algo_spec, ...
                    'problem', @RWMOP9, ...
                    'M', M_OBJ, ...
                    'maxFE', MAX_FE, ...
                    'save', N_SAVE, ...
                    'run', run_idx);
            fprintf('  [OK] %s/RWMOP9 run %d complete\n', algo_name, run_idx);
        catch ME
            fprintf('  [FAIL] %s/RWMOP9 run %d: %s\n', algo_name, run_idx, ME.message);
        end
    end
end

elapsed = toc(t_start);

%% Quick diagnostic — verify bound clamping worked
fprintf('\n========================================\n');
fprintf('  Post-run Diagnostic\n');
fprintf('========================================\n\n');

lower_bounds = [1, sqrt(2), sqrt(2), 1];
upper_bounds = [3, 3, 3, 3];

for a = 1:size(algorithms, 1)
    algo_name = algorithms{a, 1};
    all_f1 = []; all_f2 = []; all_decs = [];
    n_loaded = 0;

    for run = 1:NUM_RUNS
        files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_*_%d.mat', algo_name, run)));
        if isempty(files), continue; end
        n_loaded = n_loaded + 1;

        d = load(fullfile(files(1).folder, files(1).name));
        if isfield(d, 'result') && iscell(d.result)
            final_pop = d.result{end};
            if iscell(final_pop), final_pop = final_pop{end}; end
        end

        try
            objs = final_pop.objs;
            decs = final_pop.decs;
            all_f1 = [all_f1; objs(:,1)]; %#ok<AGROW>
            all_f2 = [all_f2; objs(:,2)]; %#ok<AGROW>
            all_decs = [all_decs; decs];   %#ok<AGROW>
        end
    end

    fprintf('%s:\n', algo_name);
    fprintf('  Runs loaded: %d/%d\n', n_loaded, NUM_RUNS);
    if ~isempty(all_f1)
        fprintf('  f1 range: [%.4f, %.4f]\n', min(all_f1), max(all_f1));
        fprintf('  f2 range: [%.6f, %.6f]\n', min(all_f2), max(all_f2));
        n_oob = sum(any(all_decs < lower_bounds - 1e-10, 2) | any(all_decs > upper_bounds + 1e-10, 2));
        fprintf('  Out-of-bounds: %d/%d\n', n_oob, size(all_decs, 1));
        if min(all_f1) >= 0 && min(all_f2) >= 0
            fprintf('  STATUS: OK (all objectives non-negative)\n');
        else
            fprintf('  WARNING: Negative objectives detected!\n');
        end
    end
    fprintf('\n');
end

fprintf('=== Ablation RWMOP9 runs complete in %.1f min ===\n', elapsed/60);
delete(gcp('nocreate'));
