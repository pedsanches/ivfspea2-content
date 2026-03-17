%% diagnose_rwmop9.m — Investigate IVF/SPEA2 IGD anomaly on RWMOP9
%  Compares IVF/SPEA2 vs SPEA2 solutions on RWMOP9 to understand
%  why IVF/SPEA2 has catastrophic IGD but excellent HV.
%
%  Usage:
%    matlab -batch "run('experiments/diagnose_rwmop9.m')"

%% Setup
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
data_dir    = fullfile(platemo_dir, 'Data');
addpath(genpath(platemo_dir));

fprintf('=== RWMOP9 Diagnostic Analysis ===\n\n');

%% 1. Understand the reference point
fprintf('--- 1. RWMOP9 GetOptimum (reference point) ---\n');
prob = RWMOP9();
R = prob.GetOptimum(10000);
fprintf('GetOptimum returns: [%g, %g]\n', R(1,1), R(1,2));
fprintf('Size: [%d x %d]\n', size(R,1), size(R,2));
fprintf('Note: f1 = structural volume (min), f2 = structural compliance (min)\n\n');

%% 2. Load one run from each algorithm and compare
algorithms = {'SPEA2', 'IVFSPEA2', 'NSGAII', 'MOEAD', 'SPEA2SDE', 'AGEMOEAII', 'ARMOEA'};

fprintf('--- 2. Objective space comparison (run 1) ---\n');
fprintf('%15s | %15s %15s | %15s %15s | %10s %10s | %10s\n', ...
    'Algorithm', 'f1_min', 'f1_max', 'f2_min', 'f2_max', 'n_sols', 'n_feasible', 'IGD_to_ref');

for ai = 1:length(algorithms)
    algo = algorithms{ai};
    
    % Find run 1
    files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_1.mat', algo)));
    if isempty(files)
        fprintf('%15s | NOT FOUND\n', algo);
        continue;
    end
    
    fpath = fullfile(files(1).folder, files(1).name);
    d = load(fpath);
    
    % Get final population
    if isfield(d, 'result') && iscell(d.result)
        final_pop = d.result{end};
        if iscell(final_pop)
            final_pop = final_pop{end};
        end
    end
    
    % Try to get objectives
    try
        objs = final_pop.objs;
    catch
        if isnumeric(final_pop)
            objs = final_pop;
        else
            fprintf('%15s | Cannot extract objectives (class: %s)\n', algo, class(final_pop));
            continue;
        end
    end
    
    % Get constraint violations if available
    try
        cons = final_pop.cons;
        n_feasible = sum(all(cons <= 0, 2));
    catch
        n_feasible = size(objs, 1);
    end
    
    n_sols = size(objs, 1);
    
    % Compute IGD to single reference point
    igd_val = mean(min(pdist2(R, objs), [], 2));
    
    fprintf('%15s | %15.4f %15.4f | %15.6f %15.6f | %10d %10d | %10.4f\n', ...
        algo, min(objs(:,1)), max(objs(:,1)), min(objs(:,2)), max(objs(:,2)), ...
        n_sols, n_feasible, igd_val);
end

%% 3. Detailed analysis of IVF/SPEA2 vs SPEA2

fprintf('\n--- 3. Detailed objective value comparison (all 60 runs) ---\n');

% Collect f1 and f2 ranges across all runs
for algo_idx = 1:2
    if algo_idx == 1
        algo = 'SPEA2';
    else
        algo = 'IVFSPEA2';
    end
    
    all_f1 = [];
    all_f2 = [];
    
    for run = 1:60
        files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_%d.mat', algo, run)));
        if isempty(files), continue; end
        
        d = load(fullfile(files(1).folder, files(1).name));
        if isfield(d, 'result') && iscell(d.result)
            final_pop = d.result{end};
            if iscell(final_pop), final_pop = final_pop{end}; end
        end
        
        try
            objs = final_pop.objs;
            all_f1 = [all_f1; objs(:,1)];
            all_f2 = [all_f2; objs(:,2)];
        end
    end
    
    fprintf('\n%s across all 60 runs:\n', algo);
    fprintf('  f1 (volume):     min=%10.4f  median=%10.4f  max=%10.4f\n', ...
        min(all_f1), median(all_f1), max(all_f1));
    fprintf('  f2 (compliance): min=%10.6f  median=%10.6f  max=%10.6f\n', ...
        min(all_f2), median(all_f2), max(all_f2));
    fprintf('  Total solutions across 60 runs: %d\n', length(all_f1));
    
    % Check if solutions are within bounds
    lower = [1, sqrt(2), sqrt(2), 1];
    upper = [3, 3, 3, 3];
end

%% 4. Check the PROBLEM class to understand how GetOptimum is used for IGD
fprintf('\n--- 4. Understanding IGD computation ---\n');
fprintf('GetOptimum returns a single point: [%g, %g]\n', R(1,1), R(1,2));
fprintf('This is the HV reference point, NOT a Pareto front!\n');
fprintf('IGD = mean(min(pdist2(optimum, PopObj))) measures average distance\n');
fprintf('from this single reference point to the nearest solution.\n');
fprintf('Since this point [3048, 0.04] has very large f1, algorithms whose\n');
fprintf('solutions have SMALLER f1 (better convergence!) will have WORSE IGD.\n');
fprintf('\nThis means: IGD for RWMOP9 is UNRELIABLE as a quality indicator\n');
fprintf('because GetOptimum returns the HV reference point, not the true PF.\n');

%% 5. Compute a meaningful comparison: use best-known non-dominated front
fprintf('\n--- 5. Constructing best-known Pareto Front ---\n');

all_objs = [];
all_algos = {'SPEA2','IVFSPEA2','NSGAII','NSGAIII','MOEAD','MFOSPEA2','SPEA2SDE','AGEMOEAII','ARMOEA'};
for ai = 1:length(all_algos)
    algo = all_algos{ai};
    for run = 1:60
        files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_%d.mat', algo, run)));
        if isempty(files), continue; end
        d = load(fullfile(files(1).folder, files(1).name));
        if isfield(d, 'result') && iscell(d.result)
            final_pop = d.result{end};
            if iscell(final_pop), final_pop = final_pop{end}; end
        end
        try
            all_objs = [all_objs; final_pop.objs];
        catch
        end
    end
end

fprintf('Total solutions from all algorithms: %d\n', size(all_objs, 1));

% Find non-dominated solutions (Pareto front)
dominated = false(size(all_objs, 1), 1);
for i = 1:size(all_objs, 1)
    for j = 1:size(all_objs, 1)
        if i == j, continue; end
        if all(all_objs(j,:) <= all_objs(i,:)) && any(all_objs(j,:) < all_objs(i,:))
            dominated(i) = true;
            break;
        end
    end
end

pf = all_objs(~dominated,:);
fprintf('Non-dominated solutions (best-known PF): %d\n', size(pf, 1));
fprintf('PF f1 range: [%.4f, %.4f]\n', min(pf(:,1)), max(pf(:,1)));
fprintf('PF f2 range: [%.6f, %.6f]\n', min(pf(:,2)), max(pf(:,2)));

%% 6. Re-compute IGD using best-known PF
fprintf('\n--- 6. IGD using best-known PF (corrected) ---\n');
fprintf('%15s | %15s | %15s\n', 'Algorithm', 'IGD (ref point)', 'IGD (best PF)');

for ai = 1:length(all_algos)
    algo = all_algos{ai};
    igd_ref_vals = [];
    igd_pf_vals  = [];
    
    for run = 1:60
        files = dir(fullfile(data_dir, '**', sprintf('%s_RWMOP9_M2_D4_%d.mat', algo, run)));
        if isempty(files), continue; end
        d = load(fullfile(files(1).folder, files(1).name));
        if isfield(d, 'result') && iscell(d.result)
            final_pop = d.result{end};
            if iscell(final_pop), final_pop = final_pop{end}; end
        end
        try
            objs = final_pop.objs;
            igd_ref = mean(min(pdist2(R, objs), [], 2));
            igd_pf  = mean(min(pdist2(pf, objs), [], 2));
            igd_ref_vals(end+1) = igd_ref;
            igd_pf_vals(end+1) = igd_pf;
        end
    end
    
    fprintf('%15s | %15.4f | %15.6f\n', algo, median(igd_ref_vals), median(igd_pf_vals));
end

fprintf('\n=== Diagnostic complete ===\n');
