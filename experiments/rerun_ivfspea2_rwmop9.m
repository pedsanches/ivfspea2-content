%% rerun_ivfspea2_rwmop9.m — Re-run IVFSPEA2 on RWMOP9 after bound-clamping fix
%  Re-runs only IVFSPEA2 (60 runs) and then compares against existing baselines.
%
%  Usage:
%    matlab -batch "run('experiments/rerun_ivfspea2_rwmop9.m')"

%% Configuration
NUM_RUNS = 60;
MAX_FE   = 100000;
N_SAVE   = 10;
M_OBJ    = 2;

% IVF parameters (AR mode, same as original run_rwmop9.m)
C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

data_dir = fullfile(platemo_dir, 'Data');

%% Start parallel pool
if isempty(gcp('nocreate'))
    parpool;
end

%% ===================== PHASE 1: Re-run IVFSPEA2 =====================
fprintf('\n========================================\n');
fprintf('  IVFSPEA2 RWMOP9 Re-run (bound-clamping fix)\n');
fprintf('  %d runs, maxFE=%d\n', NUM_RUNS, MAX_FE);
fprintf('  IVF params: C=%.2f R=%.1f M=%d V=%d Cycles=%d\n', ...
    C_val, R_val, M_val, V_val, Cycles_val);
fprintf('========================================\n\n');

algo_spec = {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

target_folder = fullfile(data_dir, 'IVFSPEA2');

% Detect which runs are missing
runs_needed = [];
for r = 1:NUM_RUNS
    pattern = sprintf('IVFSPEA2_RWMOP9_M%d_*_%d.mat', M_OBJ, r);
    if isempty(dir(fullfile(target_folder, pattern)))
        runs_needed(end+1) = r; %#ok<AGROW>
    end
end

fprintf('Runs needed: %d/%d\n\n', length(runs_needed), NUM_RUNS);

t_start = tic;

parfor ri = 1:length(runs_needed)
    run_idx = runs_needed(ri);
    try
        platemo('algorithm', algo_spec, ...
                'problem', @RWMOP9, ...
                'M', M_OBJ, ...
                'maxFE', MAX_FE, ...
                'save', N_SAVE, ...
                'run', run_idx);
        fprintf('  [OK] IVFSPEA2/RWMOP9 run %d complete\n', run_idx);
    catch ME
        fprintf('  [FAIL] IVFSPEA2/RWMOP9 run %d: %s\n', run_idx, ME.message);
    end
end

elapsed_run = toc(t_start);
fprintf('\nIVFSPEA2 re-run complete in %.1f min\n', elapsed_run/60);

%% ===================== PHASE 2: Quick Diagnostic =====================
fprintf('\n========================================\n');
fprintf('  Post-fix Diagnostic\n');
fprintf('========================================\n\n');

algorithms = {'SPEA2', 'IVFSPEA2', 'NSGAII', 'MOEAD', 'SPEA2SDE', 'AGEMOEAII', 'ARMOEA'};

% Reference point from RWMOP9.GetOptimum
prob = RWMOP9();
R = prob.GetOptimum(10000);
fprintf('RWMOP9 HV reference point: [%g, %g]\n\n', R(1,1), R(1,2));

% RWMOP9 bounds for validation
lower_bounds = [1, sqrt(2), sqrt(2), 1];
upper_bounds = [3, 3, 3, 3];

fprintf('--- Objective space comparison (run 1) ---\n');
fprintf('%15s | %12s %12s | %12s %12s | %10s | %8s\n', ...
    'Algorithm', 'f1_min', 'f1_max', 'f2_min', 'f2_max', 'IGD_to_ref', 'bounded?');

for ai = 1:length(algorithms)
    algo = algorithms{ai};

    files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_1.mat', algo)));
    if isempty(files)
        fprintf('%15s | NOT FOUND\n', algo);
        continue;
    end

    d = load(fullfile(files(1).folder, files(1).name));
    if isfield(d, 'result') && iscell(d.result)
        final_pop = d.result{end};
        if iscell(final_pop), final_pop = final_pop{end}; end
    end

    try
        objs = final_pop.objs;
        decs = final_pop.decs;
    catch
        fprintf('%15s | Cannot extract data\n', algo);
        continue;
    end

    % Check if decision variables are within bounds
    all_bounded = all(all(decs >= lower_bounds - 1e-10, 2) & all(decs <= upper_bounds + 1e-10, 2));
    if all_bounded
        bounded_str = 'YES';
    else
        bounded_str = 'NO';
    end

    igd_val = mean(min(pdist2(R, objs), [], 2));

    fprintf('%15s | %12.4f %12.4f | %12.6f %12.6f | %10.4f | %8s\n', ...
        algo, min(objs(:,1)), max(objs(:,1)), min(objs(:,2)), max(objs(:,2)), ...
        igd_val, bounded_str);
end

%% All-run summary for IVFSPEA2 (before/after comparison)
fprintf('\n--- IVFSPEA2 across all %d runs (POST-FIX) ---\n', NUM_RUNS);
all_f1 = [];
all_f2 = [];
all_decs = [];
n_runs_found = 0;

for run = 1:NUM_RUNS
    files = dir(fullfile(data_dir, '**', sprintf('IVFSPEA2_RWMOP9_M2_D4_%d.mat', run)));
    if isempty(files), continue; end
    n_runs_found = n_runs_found + 1;

    d = load(fullfile(files(1).folder, files(1).name));
    if isfield(d, 'result') && iscell(d.result)
        final_pop = d.result{end};
        if iscell(final_pop), final_pop = final_pop{end}; end
    end

    try
        objs = final_pop.objs;
        decs = final_pop.decs;
        all_f1 = [all_f1; objs(:,1)];
        all_f2 = [all_f2; objs(:,2)];
        all_decs = [all_decs; decs];
    end
end

fprintf('  Runs loaded: %d/%d\n', n_runs_found, NUM_RUNS);
fprintf('  f1 (volume):     min=%10.4f  median=%10.4f  max=%10.4f\n', ...
    min(all_f1), median(all_f1), max(all_f1));
fprintf('  f2 (compliance): min=%10.6f  median=%10.6f  max=%10.6f\n', ...
    min(all_f2), median(all_f2), max(all_f2));
fprintf('  Total solutions: %d\n', length(all_f1));

% Bounds check
n_oob = sum(any(all_decs < lower_bounds - 1e-10, 2) | any(all_decs > upper_bounds + 1e-10, 2));
fprintf('  Out-of-bounds solutions: %d/%d (%.2f%%)\n', n_oob, size(all_decs, 1), 100*n_oob/size(all_decs,1));

if min(all_f1) >= 0 && min(all_f2) >= 0
    fprintf('  STATUS: ALL objectives non-negative - FIX CONFIRMED\n');
else
    fprintf('  WARNING: Some objectives still negative - investigate further\n');
end

%% HV comparison across all algorithms
fprintf('\n--- HV comparison (all %d runs) ---\n', NUM_RUNS);
fprintf('%15s | %12s %12s %12s\n', 'Algorithm', 'HV_median', 'HV_mean', 'HV_std');

% HV reference point (same as GetOptimum, used by PlatEMO)
hv_ref = R;

for ai = 1:length(algorithms)
    algo = algorithms{ai};
    hv_vals = [];

    for run = 1:NUM_RUNS
        files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_%d.mat', algo, run)));
        if isempty(files), continue; end

        d = load(fullfile(files(1).folder, files(1).name));
        if isfield(d, 'result') && iscell(d.result)
            final_pop = d.result{end};
            if iscell(final_pop), final_pop = final_pop{end}; end
        end

        try
            objs = final_pop.objs;
            % Normalize objectives for HV calculation
            fmin = min(objs, [], 1);
            fmax = hv_ref;
            norm_objs = (objs - fmin) ./ (fmax - fmin + 1e-10);
            % Only keep solutions dominated by reference point
            valid = all(objs <= hv_ref, 2);
            if any(valid)
                hv = stk_dominatedhv(objs(valid,:), hv_ref);
                hv_vals(end+1) = hv;
            else
                hv_vals(end+1) = 0;
            end
        catch
            % If stk_dominatedhv not available, skip HV
        end
    end

    if ~isempty(hv_vals)
        fprintf('%15s | %12.6f %12.6f %12.6f  (n=%d)\n', ...
            algo, median(hv_vals), mean(hv_vals), std(hv_vals), length(hv_vals));
    else
        fprintf('%15s | (HV computation unavailable)\n', algo);
    end
end

fprintf('\n=== Re-run and diagnostic complete ===\n');
delete(gcp('nocreate'));
