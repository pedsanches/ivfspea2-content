%% sanity_check_ivfspea2_nonrwmop9.m
% Quick integrity check: re-run IVFSPEA2 on selected non-RWMOP9 benchmarks
% and compare IGD distribution against historical processed results.
%
% Usage:
%   matlab -batch "run('experiments/sanity_check_ivfspea2_nonrwmop9.m')"

%% Configuration
NUM_RUNS = 30;
BASE_RUN = 1001;   % avoid collision with historical runs
MAX_FE   = 100000;
N_SAVE   = 10;

% IVF parameters (same protocol used in current experiment scripts)
C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;
algo_spec = {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

cases = {
    'ZDT4',  @ZDT4,  2, 10;
    'DTLZ4', @DTLZ4, 3, 12;
    'WFG9',  @WFG9,  3, 12;
    'MaF5',  @MaF5,  3, 12;
};

%% Setup
project_dir = fileparts(mfilename('fullpath'));
project_dir = fullfile(project_dir, '..');
platemo_dir = fullfile(project_dir, 'src', 'matlab', 'lib', 'PlatEMO');
data_dir    = fullfile(platemo_dir, 'Data');
results_dir = fullfile(project_dir, 'results');
if ~isfolder(results_dir), mkdir(results_dir); end

addpath(genpath(platemo_dir));
cd(platemo_dir);

if isempty(gcp('nocreate'))
    parpool;
end

fprintf('=== Sanity check IVFSPEA2 (non-RWMOP9) ===\n');
fprintf('Cases: %d | Runs/case: %d | maxFE: %d\n\n', size(cases,1), NUM_RUNS, MAX_FE);

%% Execute runs
for ci = 1:size(cases,1)
    prob_name = cases{ci,1};
    prob_fun  = cases{ci,2};
    prob_M    = cases{ci,3};
    prob_D    = cases{ci,4};

    fprintf('[%d/%d] %s (M=%d, D=%d)\n', ci, size(cases,1), prob_name, prob_M, prob_D);

    run_ids = BASE_RUN:(BASE_RUN + NUM_RUNS - 1);
    parfor ri = 1:numel(run_ids)
        run_idx = run_ids(ri);

        % Skip if already exists
        pattern = sprintf('IVFSPEA2_%s_M%d_D%d_%d.mat', prob_name, prob_M, prob_D, run_idx);
        existing = dir(fullfile(data_dir, 'IVFSPEA2', pattern));
        if ~isempty(existing)
            continue;
        end

        try
            platemo('algorithm', algo_spec, ...
                    'problem', prob_fun, ...
                    'M', prob_M, ...
                    'D', prob_D, ...
                    'maxFE', MAX_FE, ...
                    'save', N_SAVE, ...
                    'run', run_idx, ...
                    'metName', {'IGD'});
        catch ME
            fprintf('  [FAIL] %s run %d: %s\n', prob_name, run_idx, ME.message);
        end
    end

    fprintf('  done\n\n');
end

%% Collect new IGD values
new_rows = {};
for ci = 1:size(cases,1)
    prob_name = cases{ci,1};
    prob_M    = cases{ci,3};
    prob_D    = cases{ci,4};

    vals = nan(NUM_RUNS,1);
    run_ids = BASE_RUN:(BASE_RUN + NUM_RUNS - 1);

    for ri = 1:numel(run_ids)
        run_idx = run_ids(ri);
        pattern = sprintf('IVFSPEA2_%s_M%d_D%d_%d.mat', prob_name, prob_M, prob_D, run_idx);
        files = dir(fullfile(data_dir, 'IVFSPEA2', pattern));
        if isempty(files)
            continue;
        end

        d = load(fullfile(files(1).folder, files(1).name));
        vals(ri) = local_extract_igd(d);
    end

    vals = vals(~isnan(vals));
    if isempty(vals)
        continue;
    end

    new_rows{end+1} = struct( ...
        'Problem', prob_name, ...
        'M', prob_M, ...
        'D', prob_D, ...
        'N_new', length(vals), ...
        'Median_new', median(vals), ...
        'IQR_new', iqr(vals), ...
        'Min_new', min(vals), ...
        'Max_new', max(vals)); %#ok<AGROW>
end

%% Load historical reference (processed file)
hist_file = fullfile(project_dir, 'data', 'processed', 'metrica_IGD.csv');
T = readtable(hist_file, 'Delimiter', ',');

for i = 1:length(new_rows)
    r = new_rows{i};
    sel = strcmp(T.Algoritmo, 'IVFSPEA2') & strcmp(T.Problema, r.Problem) & strcmp(T.M, sprintf('M%d', r.M));
    hvals = T.IGD(sel);

    if isempty(hvals)
        r.N_hist = 0;
        r.Median_hist = NaN;
        r.IQR_hist = NaN;
        r.RelDiffPct = NaN;
    else
        r.N_hist = length(hvals);
        r.Median_hist = median(hvals);
        r.IQR_hist = iqr(hvals);
        r.RelDiffPct = 100 * (r.Median_new - r.Median_hist) / r.Median_hist;
    end

    new_rows{i} = r;
end

%% Save summary CSV
out_csv = fullfile(results_dir, 'sanity_check_ivfspea2_30runs.csv');
fid = fopen(out_csv, 'w');
fprintf(fid, 'Problem,M,D,N_new,Median_new,IQR_new,Min_new,Max_new,N_hist,Median_hist,IQR_hist,RelDiffPct\n');
for i = 1:length(new_rows)
    r = new_rows{i};
    fprintf(fid, '%s,%d,%d,%d,%.10e,%.10e,%.10e,%.10e,%d,%.10e,%.10e,%.6f\n', ...
        r.Problem, r.M, r.D, r.N_new, r.Median_new, r.IQR_new, r.Min_new, r.Max_new, ...
        r.N_hist, r.Median_hist, r.IQR_hist, r.RelDiffPct);
end
fclose(fid);

fprintf('Summary saved: %s\n\n', out_csv);

for i = 1:length(new_rows)
    r = new_rows{i};
    fprintf('%s M%d D%d | new med=%.6e (IQR=%.3e, n=%d) | hist med=%.6e (IQR=%.3e, n=%d) | diff=%.2f%%\n', ...
        r.Problem, r.M, r.D, r.Median_new, r.IQR_new, r.N_new, r.Median_hist, r.IQR_hist, r.N_hist, r.RelDiffPct);
end

fprintf('\n=== Sanity check complete ===\n');

delete(gcp('nocreate'));

%% Local helper
function igd = local_extract_igd(d)
igd = NaN;
if isfield(d,'metric') && isstruct(d.metric) && isfield(d.metric,'IGD')
    series = d.metric.IGD;
    if iscell(series)
        igd = series{end};
    else
        igd = series(end);
    end
end
end
