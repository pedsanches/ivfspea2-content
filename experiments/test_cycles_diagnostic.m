%% test_cycles_diagnostic.m — Diagnóstico do parâmetro Cycles (FIXED)
%  Testa Cycles ∈ {1, 2, 3, 5, 10, 20} em 10 problemas representativos.
%  30 runs por configuração. Mede IGD/HV + ciclos efetivos reais.
%
%  Roda como instância MATLAB separada.
%
%  Usage:
%    nohup matlab -nodisplay -nosplash -batch "run('experiments/test_cycles_diagnostic.m')" \
%      > experiments/logs/cycles_diagnostic_launch.log 2>&1 &

%% Configuration
CYCLES_VALUES = [1, 2, 3, 5, 10, 20];
NUM_RUNS  = 30;
RUN_BASE  = 5001;  % Starting base for runs
MAX_FE    = 100000;
N_SAVE    = 10;

% Fixed IVF params (same as submission rerun)
C_val = 0.11;
R_val = 0.10;
M_val = 0;
V_val = 0;
S_val = 1;
N_Offspring_val = 1;
EARN_val = 0;
N_Obj_Limit_val = 0;

% 2 representative problems (quick diagnostic)
test_problems = {
    @ZDT1,  2, 30;   % Bi-objective
    @DTLZ1, 3,  7;   % Tri-objective, multi-modal
};

%% Setup
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
results_dir  = fullfile(project_root, 'results');
log_dir      = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
if ~isfolder(results_dir), mkdir(results_dir); end

addpath(genpath(platemo_dir));
cd(platemo_dir);

data_dir = fullfile(platemo_dir, 'Data');
% PlatEMO saves to Data/IVFSPEA2 because we use the IVFSPEA2 class
target_folder = fullfile(data_dir, 'IVFSPEA2');

diary(fullfile(log_dir, sprintf('cycles_diagnostic_%s.log', datestr(now, 'yyyymmdd_HHMMSS'))));

fprintf('=== CYCLES DIAGNOSTIC (FIXED) ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Cycles to test: %s\n', mat2str(CYCLES_VALUES));
fprintf('Problems: %d | Runs: %d | maxFE: %d\n', size(test_problems,1), NUM_RUNS, MAX_FE);
fprintf('Fixed: C=%.2f, R=%.2f\n\n', C_val, R_val);

%% Start parallel pool (separate from baselines)
if isempty(gcp('nocreate'))
    % Try to start pool with 6 workers
    try
        parpool(6);
    catch
        parpool; % Fallback
    end
end

%% Collect results
% Pre-allocate results table
all_results = {};

t_start = tic;
total_combos = length(CYCLES_VALUES) * size(test_problems, 1);
combo_idx = 0;

for ci = 1:length(CYCLES_VALUES)
    cyc = CYCLES_VALUES(ci);
    
    % Shift runs for this cycle value to avoid overwriting files
    run_start_idx = RUN_BASE + (ci-1)*NUM_RUNS;
    run_end_idx   = run_start_idx + NUM_RUNS - 1;

    display_name = sprintf('IVFSPEA2_CYC%d', cyc);
    algo_spec = {@IVFSPEA2, C_val, R_val, M_val, V_val, cyc, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

    for pi = 1:size(test_problems, 1)
        prob_handle = test_problems{pi, 1};
        M_obj       = test_problems{pi, 2};
        D_vars      = test_problems{pi, 3};
        prob_name   = func2str(prob_handle);

        combo_idx = combo_idx + 1;
        fprintf('\n[%d/%d] Cycles=%d on %s (M=%d, D=%d) [Runs %d-%d]\n', ...
                combo_idx, total_combos, cyc, prob_name, M_obj, D_vars, run_start_idx, run_end_idx);

        % Check existing runs in target_folder (Data/IVFSPEA2)
        runs_needed = [];
        for r = run_start_idx:run_end_idx
            fname = sprintf('IVFSPEA2_%s_M%d_D%d_%d.mat', prob_name, M_obj, D_vars, r);
            if ~isfile(fullfile(target_folder, fname))
                runs_needed(end+1) = r; %#ok<AGROW>
            end
        end

        if isempty(runs_needed)
            fprintf('  -> Already complete.\n');
        else
            fprintf('  -> %d runs needed.\n', length(runs_needed));

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
                    fprintf('  [FAIL] Cyc=%d %s run %d: %s\n', cyc, prob_name, run_idx, ME.message);
                end
            end
        end

        % === Collect IGD values from saved .mat files ===
        igd_values = nan(NUM_RUNS, 1);
        hv_values  = nan(NUM_RUNS, 1);

        for r_idx = 1:NUM_RUNS
            actual_run_id = run_start_idx + r_idx - 1;
            fname = sprintf('IVFSPEA2_%s_M%d_D%d_%d.mat', prob_name, M_obj, D_vars, actual_run_id);
            fpath = fullfile(target_folder, fname);

            if isfile(fpath)
                data = load(fpath);
                % PlatEMO saves metric as a struct with fields: .IGD, .HV, .runtime
                if isfield(data, 'metric')
                    met = data.metric;
                    if isfield(met, 'IGD')
                        igd_trace = met.IGD;
                        if ~isempty(igd_trace)
                            igd_values(r_idx) = igd_trace(end);
                        end
                    end
                    if isfield(met, 'HV')
                        hv_trace = met.HV;
                        if ~isempty(hv_trace)
                            hv_values(r_idx) = hv_trace(end);
                        end
                    end
                end
            end
        end

        med_igd = nanmedian(igd_values);
        mean_igd = nanmean(igd_values);
        std_igd = nanstd(igd_values);
        med_hv  = nanmedian(hv_values);

        fprintf('  -> IGD: median=%.6f, mean=%.6f, std=%.6f | HV median=%.6f\n', ...
                med_igd, mean_igd, std_igd, med_hv);

        % Store
        all_results{end+1, 1} = cyc;
        all_results{end, 2} = prob_name;
        all_results{end, 3} = M_obj;
        all_results{end, 4} = D_vars;
        all_results{end, 5} = med_igd;
        all_results{end, 6} = mean_igd;
        all_results{end, 7} = std_igd;
        all_results{end, 8} = med_hv;
        all_results{end, 9} = sum(~isnan(igd_values));
    end
end

elapsed = toc(t_start);
fprintf('\n=== DIAGNOSTIC COMPLETE in %.1f min ===\n', elapsed/60);

%% Write CSV
csv_file = fullfile(results_dir, 'cycles_diagnostic.csv');
fid = fopen(csv_file, 'w');
fprintf(fid, 'Cycles,Problem,M,D,Median_IGD,Mean_IGD,Std_IGD,Median_HV,N_runs\n');
for i = 1:size(all_results, 1)
    fprintf(fid, '%d,%s,%d,%d,%.8f,%.8f,%.8f,%.8f,%d\n', ...
            all_results{i,1}, all_results{i,2}, all_results{i,3}, all_results{i,4}, ...
            all_results{i,5}, all_results{i,6}, all_results{i,7}, all_results{i,8}, all_results{i,9});
end
fclose(fid);
fprintf('Results saved to: %s\n', csv_file);

%% Print summary table
fprintf('\n=== SUMMARY: Median IGD by Cycles ===\n');
fprintf('%-8s', 'Cycles');
for pi = 1:size(test_problems, 1)
    fprintf('%-18s', func2str(test_problems{pi,1}));
end
fprintf('\n');
fprintf('%s\n', repmat('-', 1, 8 + 18 * size(test_problems,1)));

for ci = 1:length(CYCLES_VALUES)
    cyc = CYCLES_VALUES(ci);
    fprintf('%-8d', cyc);
    for pi = 1:size(test_problems, 1)
        prob_name = func2str(test_problems{pi,1});
        % Find matching result
        for ri = 1:size(all_results, 1)
            if all_results{ri,1} == cyc && strcmp(all_results{ri,2}, prob_name)
                fprintf('%-18.6f', all_results{ri,5});
                break;
            end
        end
    end
    fprintf('\n');
end

%% Print ranking (best Cycles for each problem)
fprintf('\n=== BEST CYCLES PER PROBLEM ===\n');
for pi = 1:size(test_problems, 1)
    prob_name = func2str(test_problems{pi,1});
    best_igd = Inf;
    best_cyc = -1;
    for ri = 1:size(all_results, 1)
        if strcmp(all_results{ri,2}, prob_name) && all_results{ri,5} < best_igd
            best_igd = all_results{ri,5};
            best_cyc = all_results{ri,1};
        end
    end
    fprintf('  %s: best Cycles=%d (median IGD=%.6f)\n', prob_name, best_cyc, best_igd);
end

delete(gcp('nocreate'));
diary off;
exit;
