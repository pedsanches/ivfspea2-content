%% process_rwmop9.m — Recompute robust IGD/HV for RWMOP9
%  Recomputes metrics directly from final populations (instead of relying on
%  saved metric fields), includes ablation variants, and uses an empirical
%  reference front for IGD to avoid the RWMOP9 GetOptimum anomaly.
%
%  Outputs:
%    - results/rwmop9_igd_results.csv   (IGD vs empirical PF)
%    - results/rwmop9_hv_results.csv    (HV with RWMOP9 reference point)
%    - results/rwmop9_table.tex         (combined IGD/HV table)
%
%  Usage:
%    matlab -batch "run('experiments/process_rwmop9.m')"

%% Setup
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
data_dir    = fullfile(platemo_dir, 'Data');
results_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'results');
if ~isfolder(results_dir), mkdir(results_dir); end

addpath(genpath(platemo_dir));

NUM_RUNS = 60;
M_OBJ    = 2;

algorithms = {
    'IVFSPEA2',      'IVF/SPEA2';
    'IVFSPEA2ABLDOM','IVF/SPEA2-ABL-DOM';
    'IVFSPEA2ABL4C', 'IVF/SPEA2-ABL-4C';
    'IVFSPEA2ABL1C', 'IVF/SPEA2-ABL-1C';
    'SPEA2',         'SPEA2';
    'MFOSPEA2',      'MFO/SPEA2';
    'SPEA2SDE',      'SPEA2+SDE';
    'NSGAII',        'NSGA-II';
    'NSGAIII',       'NSGA-III';
    'MOEAD',         'MOEA/D';
    'AGEMOEAII',     'AGE-MOEA-II';
    'ARMOEA',        'AR-MOEA';
};

ref_algo = 'IVFSPEA2';

% RWMOP9 reference point used for HV
prob = RWMOP9();
hv_ref = prob.GetOptimum(10000);
if size(hv_ref,1) > 1
    hv_ref = hv_ref(1,:);
end

%% Pass 1: Load final populations for all algorithms/runs
objs_per_run = struct();
all_objs = [];

fprintf('=== Loading final populations (RWMOP9) ===\n');
for ai = 1:size(algorithms,1)
    algo = algorithms{ai,1};
    objs_per_run.(algo) = cell(NUM_RUNS,1);

    loaded = 0;
    for run_idx = 1:NUM_RUNS
        pattern = sprintf('%s_RWMOP9_M%d_*_%d.mat', algo, M_OBJ, run_idx);
        files = dir(fullfile(data_dir, '**', pattern));
        if isempty(files)
            continue;
        end

        fpath = fullfile(files(1).folder, files(1).name);
        try
            d = load(fpath);
            [objs, cons] = local_extract_final(d);
            if isempty(objs)
                continue;
            end

            % Prefer feasible subset when constraints are available
            if ~isempty(cons)
                feasible = all(cons <= 0, 2);
                if any(feasible)
                    objs = objs(feasible,:);
                end
            end

            objs_per_run.(algo){run_idx} = objs;
            all_objs = [all_objs; objs]; %#ok<AGROW>
            loaded = loaded + 1;
        catch ME
            fprintf('  Warning: %s run %d failed to load (%s)\n', algo, run_idx, ME.message);
        end
    end

    fprintf('  %-16s : %d/%d runs\n', algo, loaded, NUM_RUNS);
end

if isempty(all_objs)
    error('No RWMOP9 populations found.');
end

%% Build empirical reference PF (non-dominated set from all runs)
all_objs = unique(all_objs, 'rows');
front_no = NDSort(all_objs, 1);
pf_empirical = all_objs(front_no == 1, :);

fprintf('\nEmpirical PF size: %d solutions\n', size(pf_empirical,1));
fprintf('PF ranges: f1=[%.4f, %.4f], f2=[%.6f, %.6f]\n', ...
    min(pf_empirical(:,1)), max(pf_empirical(:,1)), ...
    min(pf_empirical(:,2)), max(pf_empirical(:,2)));

%% Pass 2: Compute per-run metrics
igd_pf_data  = struct();
igd_ref_data = struct(); % diagnostic only
hv_data      = struct();

fprintf('\n=== Recomputing IGD/HV ===\n');
for ai = 1:size(algorithms,1)
    algo = algorithms{ai,1};

    igd_pf_vals  = nan(NUM_RUNS,1);
    igd_ref_vals = nan(NUM_RUNS,1);
    hv_vals      = nan(NUM_RUNS,1);

    for run_idx = 1:NUM_RUNS
        objs = objs_per_run.(algo){run_idx};
        if isempty(objs)
            continue;
        end

        % IGD against empirical PF (corrected)
        igd_pf_vals(run_idx) = mean(min(pdist2(pf_empirical, objs), [], 2));

        % Diagnostic IGD against single GetOptimum point
        igd_ref_vals(run_idx) = mean(min(pdist2(hv_ref, objs), [], 2));

        % HV against RWMOP9 reference point
        hv_vals(run_idx) = local_hv2d(objs, hv_ref);
    end

    igd_pf_data.(algo)  = igd_pf_vals(~isnan(igd_pf_vals));
    igd_ref_data.(algo) = igd_ref_vals(~isnan(igd_ref_vals));
    hv_data.(algo)      = hv_vals(~isnan(hv_vals));

    fprintf('  %-16s : IGD=%d, HV=%d\n', algo, length(igd_pf_data.(algo)), length(hv_data.(algo)));
end

if ~isfield(igd_pf_data, ref_algo) || isempty(igd_pf_data.(ref_algo))
    error('Reference algorithm %s has no IGD data.', ref_algo);
end

%% Build statistics + tests vs IVF/SPEA2
ref_igd = igd_pf_data.(ref_algo);
ref_hv  = hv_data.(ref_algo);

rows = {};
for ai = 1:size(algorithms,1)
    algo = algorithms{ai,1};
    disp_name = algorithms{ai,2};

    igd_vals = igd_pf_data.(algo);
    hv_vals  = hv_data.(algo);
    if isempty(igd_vals) || isempty(hv_vals)
        continue;
    end

    r = struct();
    r.algo = disp_name;

    r.igd_median = median(igd_vals);
    r.igd_iqr    = iqr(igd_vals);
    r.igd_mean   = mean(igd_vals);
    r.igd_std    = std(igd_vals);
    r.igd_q25    = quantile(igd_vals,0.25);
    r.igd_q75    = quantile(igd_vals,0.75);
    r.igd_ref_median = median(igd_ref_data.(algo));

    r.hv_median  = median(hv_vals);
    r.hv_iqr     = iqr(hv_vals);
    r.hv_mean    = mean(hv_vals);
    r.hv_std     = std(hv_vals);
    r.hv_q25     = quantile(hv_vals,0.25);
    r.hv_q75     = quantile(hv_vals,0.75);

    r.n = min(length(igd_vals), length(hv_vals));

    if strcmp(algo, ref_algo)
        r.p_igd = NaN;
        r.sym_igd = '';
        r.p_hv = NaN;
        r.sym_hv = '';
    else
        r.p_igd = ranksum(ref_igd, igd_vals);
        if r.p_igd < 0.05
            if r.igd_median > median(ref_igd)
                r.sym_igd = '+';   % IVF better (IGD lower)
            else
                r.sym_igd = '-';   % algorithm better
            end
        else
            r.sym_igd = '≈';
        end

        r.p_hv = ranksum(ref_hv, hv_vals);
        if r.p_hv < 0.05
            if r.hv_median < median(ref_hv)
                r.sym_hv = '+';    % IVF better (HV higher)
            else
                r.sym_hv = '-';    % algorithm better
            end
        else
            r.sym_hv = '≈';
        end
    end

    rows{end+1} = r; %#ok<AGROW>
end

%% Save IGD CSV (corrected)
csv_igd = fullfile(results_dir, 'rwmop9_igd_results.csv');
fid = fopen(csv_igd, 'w');
fprintf(fid, 'Algorithm,Median_IGD_PF,IQR_IGD_PF,Mean_IGD_PF,Std_IGD_PF,Q25_IGD_PF,Q75_IGD_PF,Median_IGD_GetOptimum,N,p_vs_IVFSPEA2,Symbol\n');
for ri = 1:length(rows)
    r = rows{ri};
    fprintf(fid, '%s,%.10e,%.10e,%.10e,%.10e,%.10e,%.10e,%.10e,%d,%.6e,%s\n', ...
        r.algo, r.igd_median, r.igd_iqr, r.igd_mean, r.igd_std, r.igd_q25, r.igd_q75, r.igd_ref_median, r.n, r.p_igd, r.sym_igd);
end
fclose(fid);

%% Save HV CSV
csv_hv = fullfile(results_dir, 'rwmop9_hv_results.csv');
fid = fopen(csv_hv, 'w');
fprintf(fid, 'Algorithm,Median_HV,IQR_HV,Mean_HV,Std_HV,Q25_HV,Q75_HV,N,p_vs_IVFSPEA2,Symbol\n');
for ri = 1:length(rows)
    r = rows{ri};
    fprintf(fid, '%s,%.10e,%.10e,%.10e,%.10e,%.10e,%.10e,%d,%.6e,%s\n', ...
        r.algo, r.hv_median, r.hv_iqr, r.hv_mean, r.hv_std, r.hv_q25, r.hv_q75, r.n, r.p_hv, r.sym_hv);
end
fclose(fid);

%% Save combined LaTeX table
latex_file = fullfile(results_dir, 'rwmop9_table.tex');
fid = fopen(latex_file, 'w');

best_igd = inf;
best_hv  = -inf;
for ri = 1:length(rows)
    best_igd = min(best_igd, rows{ri}.igd_median);
    best_hv  = max(best_hv, rows{ri}.hv_median);
end

fprintf(fid, '\\begin{table}[t]\n');
fprintf(fid, '\\centering\n');
fprintf(fid, '\\caption{RWMOP9 results ($M=2$, $D=4$, $100\\,000$ FEs, 60 runs). IGD is recomputed against an empirical non-dominated reference front built from all algorithms/runs. HV uses the RWMOP9 reference point from \\texttt{GetOptimum}. Symbols: $+$ IVF/SPEA2 significantly better, $-$ significantly worse, $\\approx$ no significant difference (Wilcoxon rank-sum, $\\alpha=0.05$).}\n');
fprintf(fid, '\\label{tab:rwmop9}\n');
fprintf(fid, '\\scriptsize\n');
fprintf(fid, '\\begin{tabular}{lcccc}\n');
fprintf(fid, '\\toprule\n');
fprintf(fid, 'Algorithm & IGD$_{PF}$ median (IQR) & HV median (IQR) & vs IVF (IGD) & vs IVF (HV) \\\\\n');
fprintf(fid, '\\midrule\n');

for ri = 1:length(rows)
    r = rows{ri};

    if abs(r.igd_median - best_igd) < 1e-15
        igd_str = sprintf('\\textbf{%.4e} (%.3e)', r.igd_median, r.igd_iqr);
    else
        igd_str = sprintf('%.4e (%.3e)', r.igd_median, r.igd_iqr);
    end

    if abs(r.hv_median - best_hv) < 1e-15
        hv_str = sprintf('\\textbf{%.4e} (%.3e)', r.hv_median, r.hv_iqr);
    else
        hv_str = sprintf('%.4e (%.3e)', r.hv_median, r.hv_iqr);
    end

    if isnan(r.p_igd)
        sym_igd = '---';
    else
        sym_igd = sprintf('$%s$ ($p=%.3f$)', r.sym_igd, r.p_igd);
    end

    if isnan(r.p_hv)
        sym_hv = '---';
    else
        sym_hv = sprintf('$%s$ ($p=%.3f$)', r.sym_hv, r.p_hv);
    end

    fprintf(fid, '%s & %s & %s & %s & %s \\\\\n', ...
        r.algo, igd_str, hv_str, sym_igd, sym_hv);
end

fprintf(fid, '\\bottomrule\n');
fprintf(fid, '\\end{tabular}\n');
fprintf(fid, '\\end{table}\n');
fclose(fid);

fprintf('\nSaved:\n  %s\n  %s\n  %s\n', csv_igd, csv_hv, latex_file);
fprintf('\n=== RWMOP9 processing complete ===\n');

%% ===== Local functions =====
function [objs, cons] = local_extract_final(data_struct)
objs = [];
cons = [];

if isfield(data_struct, 'result') && iscell(data_struct.result) && ~isempty(data_struct.result)
    final_pop = data_struct.result{end};
    if iscell(final_pop) && ~isempty(final_pop)
        final_pop = final_pop{end};
    end

    if isobject(final_pop)
        try objs = final_pop.objs; end %#ok<TRYNC>
        try cons = final_pop.cons; end %#ok<TRYNC>
    elseif isnumeric(final_pop)
        objs = final_pop;
    end
end

% Fallback for non-standard saved structs
if isempty(objs)
    fields = fieldnames(data_struct);
    for fi = 1:length(fields)
        val = data_struct.(fields{fi});
        if isstruct(val) && isfield(val,'objs')
            objs = val.objs;
            if isfield(val,'cons')
                cons = val.cons;
            end
            return;
        end
    end
end
end

function hv = local_hv2d(pop_obj, ref_point)
hv = NaN;
if isempty(pop_obj)
    return;
end

% Keep only points inside/under the reference point (minimization)
valid = all(pop_obj <= ref_point, 2);
P = pop_obj(valid,:);
if isempty(P)
    hv = 0;
    return;
end

% Keep only non-dominated points
front_no = NDSort(P, 1);
P = P(front_no == 1, :);

% Sort by first objective ascending
P = sortrows(P, 1);

hv = 0;
prev_f2 = ref_point(2);
for i = 1:size(P,1)
    f1 = P(i,1);
    f2 = P(i,2);
    if f2 < prev_f2
        hv = hv + max(ref_point(1) - f1, 0) * (prev_f2 - f2);
        prev_f2 = f2;
    end
end
end
