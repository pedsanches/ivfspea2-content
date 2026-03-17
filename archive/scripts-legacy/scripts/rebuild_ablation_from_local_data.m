%% rebuild_ablation_from_local_data.m
% Rebuilds ablation outputs from local MAT files with strict filtering.
% - 4 variants × 10 problems × 60 runs.
% - Uses common run IDs across all 4 variants per problem for balanced comparison.
% - Writes CSV/LaTeX outputs to results/ablation/.

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
DATA_DIR = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO', 'Data');
OUT_DIR = fullfile(PROJECT_ROOT, 'results', 'ablation');
if ~exist(OUT_DIR, 'dir')
    mkdir(OUT_DIR);
end

algos = {'IVFSPEA2', 'IVFSPEA2ABL1C', 'IVFSPEA2ABL4C', 'IVFSPEA2ABLDOM'};
algo_labels = {'IVF/SPEA2 (top-2c)', 'ABL-1C', 'ABL-4C', 'ABL-DOM'};

problems = {'ZDT1', 'ZDT6', 'WFG4', 'WFG9', 'DTLZ1', 'DTLZ4', 'DTLZ7', 'WFG2', 'MaF1', 'MaF5'};
Ms       = [   2,      2,      2,      2,       3,       3,       3,      3,     3,     3  ];
Ds       = [  30,     10,     11,     11,       7,      12,      22,     12,    12,    12  ];

MAX_RUNS = 60;
alpha = 0.05;

% Build regex pattern for problems
prob_pattern = strjoin(problems, '|');

fprintf('Scanning MAT files in %s\n', DATA_DIR);

entries = struct('Algorithm', {}, 'Problem', {}, 'M', {}, 'D', {}, 'Run', {}, 'Path', {});
key_to_idx = containers.Map('KeyType', 'char', 'ValueType', 'double');

for ai = 1:numel(algos)
    algo = algos{ai};
    algo_dir = fullfile(DATA_DIR, algo);
    if ~isfolder(algo_dir)
        fprintf('  WARNING: directory not found: %s\n', algo_dir);
        continue;
    end

    mat_files = dir(fullfile(algo_dir, '*.mat'));
    for i = 1:numel(mat_files)
        fname = mat_files(i).name;
        fpath = fullfile(mat_files(i).folder, fname);

        tok = regexp(fname, sprintf('^(%s)_(%s)_M(\\d+)_D(\\d+)_(\\d+)\\.mat$', algo, prob_pattern), 'tokens', 'once');
        if isempty(tok)
            continue;
        end

        prob = tok{2};
        M = str2double(tok{3});
        D = str2double(tok{4});
        run_id = str2double(tok{5});

        pidx = find(strcmp(problems, prob), 1);
        if isempty(pidx)
            continue;
        end

        if M ~= Ms(pidx) || D ~= Ds(pidx)
            continue;
        end

        if run_id < 1 || run_id > MAX_RUNS
            continue;
        end

        key = sprintf('%s|%s|%d', algo, prob, run_id);

        if ~isKey(key_to_idx, key)
            entries(end+1) = struct( ...
                'Algorithm', algo, ...
                'Problem', prob, ...
                'M', M, ...
                'D', D, ...
                'Run', run_id, ...
                'Path', fpath ...
            ); %#ok<AGROW>
            key_to_idx(key) = numel(entries);
        end
    end
end

if isempty(entries)
    error('No valid ablation MAT files found after filtering.');
end

fprintf('Found %d valid entries.\n', numel(entries));

% Read IGD values
n = numel(entries);
alg_col = cell(n,1);
prob_col = cell(n,1);
M_col = zeros(n,1);
D_col = zeros(n,1);
run_col = zeros(n,1);
igd_col = nan(n,1);
path_col = cell(n,1);

for i = 1:n
    alg_col{i} = entries(i).Algorithm;
    prob_col{i} = entries(i).Problem;
    M_col(i) = entries(i).M;
    D_col(i) = entries(i).D;
    run_col(i) = entries(i).Run;
    path_col{i} = entries(i).Path;
    igd_col(i) = load_igd(entries(i).Path);
end

T = table(alg_col, prob_col, M_col, D_col, run_col, igd_col, path_col, ...
    'VariableNames', {'Algorithm','Problem','M','D','Run','IGD','SourcePath'});

T = T(~isnan(T.IGD), :);
T = sortrows(T, {'Problem','Algorithm','Run'});

writetable(T, fullfile(OUT_DIR, 'ablation_filtered_runs.csv'));
fprintf('Wrote %s\n', fullfile(OUT_DIR, 'ablation_filtered_runs.csv'));

% Build matched/common-run subset per problem
raw_rows = {};
summary_rows = {};

plus_eq_minus = strings(numel(algos), 3);
plus_eq_minus(:,:) = "0";

for p = 1:numel(problems)
    prob = problems{p};
    M = Ms(p);

    run_sets = cell(numel(algos),1);
    for a = 1:numel(algos)
        mask = strcmp(T.Problem, prob) & strcmp(T.Algorithm, algos{a}) & (T.M == M);
        run_sets{a} = unique(T.Run(mask));
    end

    common_runs = run_sets{1};
    for a = 2:numel(algos)
        common_runs = intersect(common_runs, run_sets{a});
    end
    common_runs = sort(common_runs(:)');

    if isempty(common_runs)
        warning('No common runs for %s(M=%d). Skipping.', prob, M);
        continue;
    end

    vals = cell(numel(algos),1);
    med = nan(numel(algos),1);
    iqr_val = nan(numel(algos),1);
    fmt = cell(numel(algos),1);
    ind = repmat({' '}, numel(algos), 1);
    pval = nan(numel(algos),1);

    for a = 1:numel(algos)
        cur = nan(numel(common_runs), 1);
        for r = 1:numel(common_runs)
            mask = strcmp(T.Problem, prob) & strcmp(T.Algorithm, algos{a}) & (T.M == M) & (T.Run == common_runs(r));
            v = T.IGD(mask);
            if isempty(v)
                cur(r) = nan;
            else
                cur(r) = v(1);
            end

            raw_rows(end+1,:) = {algos{a}, prob, M, common_runs(r), cur(r)}; %#ok<AGROW>
        end

        cur = cur(~isnan(cur));
        vals{a} = cur;
        med(a) = median(cur);
        q = prctile(cur, [25 75]);
        iqr_val(a) = q(2) - q(1);
        fmt{a} = format_median_iqr(med(a), iqr_val(a));
    end

    % Indicators are relative to baseline (algo 1)
    base = vals{1};
    for a = 2:numel(algos)
        comp = vals{a};
        if numel(base) >= 3 && numel(comp) >= 3
            pval(a) = ranksum(base, comp);
            if pval(a) < alpha
                if median(base) < median(comp)
                    ind{a} = '+';
                else
                    ind{a} = '-';
                end
            else
                ind{a} = '=';
            end
        else
            ind{a} = '=';
        end
    end

    % +/=/- counters per variant
    for a = 2:numel(algos)
        if strcmp(ind{a}, '+')
            plus_eq_minus(a,1) = string(str2double(plus_eq_minus(a,1)) + 1);
        elseif strcmp(ind{a}, '=')
            plus_eq_minus(a,2) = string(str2double(plus_eq_minus(a,2)) + 1);
        elseif strcmp(ind{a}, '-')
            plus_eq_minus(a,3) = string(str2double(plus_eq_minus(a,3)) + 1);
        end
    end

    summary_rows(end+1,:) = { ...
        sprintf('%s($M$=%d)', prob, M), numel(common_runs), ...
        fmt{1}, med(1), iqr_val(1), ...
        fmt{2}, med(2), iqr_val(2), ind{2}, pval(2), ...
        fmt{3}, med(3), iqr_val(3), ind{3}, pval(3), ...
        fmt{4}, med(4), iqr_val(4), ind{4}, pval(4) ...
    }; %#ok<AGROW>
end

raw_tbl = cell2table(raw_rows, 'VariableNames', {'Algorithm','Problem','M','Run','IGD'});
raw_tbl = sortrows(raw_tbl, {'Problem','Algorithm','Run'});
writetable(raw_tbl, fullfile(OUT_DIR, 'ablation_raw_igd.csv'));
fprintf('Wrote %s\n', fullfile(OUT_DIR, 'ablation_raw_igd.csv'));

sum_tbl = cell2table(summary_rows, 'VariableNames', { ...
    'Problem', 'n_common', ...
    'IVFSPEA2_formatted', 'IVFSPEA2_median', 'IVFSPEA2_iqr', ...
    'ABL1C_formatted', 'ABL1C_median', 'ABL1C_iqr', 'ABL1C_indicator', 'ABL1C_pvalue', ...
    'ABL4C_formatted', 'ABL4C_median', 'ABL4C_iqr', 'ABL4C_indicator', 'ABL4C_pvalue', ...
    'ABLDOM_formatted', 'ABLDOM_median', 'ABLDOM_iqr', 'ABLDOM_indicator', 'ABLDOM_pvalue' ...
});
writetable(sum_tbl, fullfile(OUT_DIR, 'ablation_summary.csv'));
fprintf('Wrote %s\n', fullfile(OUT_DIR, 'ablation_summary.csv'));

% Build LaTeX table
tex_path = fullfile(OUT_DIR, 'ablation_table.tex');
fid = fopen(tex_path, 'w');
assert(fid ~= -1, 'Could not open ablation_table.tex for writing');

fprintf(fid, '\\begin{table}[t]\n');
fprintf(fid, '\\caption{Ablation study: median IGD (IQR) over common-run subsets ($n=60$ per variant). Symbols: $+$ = top-$2c$ significantly better, $-$ = significantly worse, $=$ = no significant difference (Wilcoxon rank-sum, $\\alpha=0.05$). Best median per instance in \\textbf{bold}.}\\label{tab:ablation}\n');
fprintf(fid, '\\centering\\scriptsize\n');
fprintf(fid, '\\setlength{\\tabcolsep}{3pt}\n');
fprintf(fid, '\\begin{tabular}{lrrrrr}\n');
fprintf(fid, '\\toprule\n');
fprintf(fid, 'Problem & $n$ & IVF/SPEA2 (top-$2c$) & ABL-1C & ABL-4C & ABL-DOM \\\\ \n');
fprintf(fid, '\\midrule\n');

for i = 1:height(sum_tbl)
    medians = [sum_tbl.IVFSPEA2_median(i), sum_tbl.ABL1C_median(i), sum_tbl.ABL4C_median(i), sum_tbl.ABLDOM_median(i)];
    best_val = min(medians);
    is_best = abs(medians - best_val) <= max(1e-15, 1e-9 * abs(best_val));

    c1 = sum_tbl.IVFSPEA2_formatted{i};
    c2 = sprintf('%s$^{%s}$', sum_tbl.ABL1C_formatted{i}, sum_tbl.ABL1C_indicator{i});
    c3 = sprintf('%s$^{%s}$', sum_tbl.ABL4C_formatted{i}, sum_tbl.ABL4C_indicator{i});
    c4 = sprintf('%s$^{%s}$', sum_tbl.ABLDOM_formatted{i}, sum_tbl.ABLDOM_indicator{i});

    if is_best(1), c1 = ['\textbf{' c1 '}']; end
    if is_best(2), c2 = ['\textbf{' c2 '}']; end
    if is_best(3), c3 = ['\textbf{' c3 '}']; end
    if is_best(4), c4 = ['\textbf{' c4 '}']; end

    fprintf(fid, '%s & %d & %s & %s & %s & %s \\\\ \n', ...
        sum_tbl.Problem{i}, sum_tbl.n_common(i), c1, c2, c3, c4);
end

fprintf(fid, '\\midrule\n');
fprintf(fid, '$+/=/-$ & --- & --- & %s/%s/%s & %s/%s/%s & %s/%s/%s \\\\ \n', ...
    plus_eq_minus(2,1), plus_eq_minus(2,2), plus_eq_minus(2,3), ...
    plus_eq_minus(3,1), plus_eq_minus(3,2), plus_eq_minus(3,3), ...
    plus_eq_minus(4,1), plus_eq_minus(4,2), plus_eq_minus(4,3));
fprintf(fid, '\\botrule\n');
fprintf(fid, '\\end{tabular}\n');
fprintf(fid, '\\end{table}\n');

fclose(fid);
fprintf('Wrote %s\n', tex_path);

fprintf('\nDone. Common-run sizes by problem:\n');
for i = 1:height(sum_tbl)
    fprintf('  %s: n=%d\n', sum_tbl.Problem{i}, sum_tbl.n_common(i));
end


function igd = load_igd(mat_path)
igd = NaN;
try
    s = load(mat_path);
    if ~isfield(s, 'metric') || ~isfield(s.metric, 'IGD')
        return;
    end
    v = s.metric.IGD;
    if isempty(v)
        return;
    end
    v = v(:);
    igd = double(v(end));
catch
    igd = NaN;
end
end


function txt = format_median_iqr(med, iqr_val)
if med == 0
    txt = '0.00(0.00)e+0';
    return;
end
expv = floor(log10(abs(med)));
m = med / (10^expv);
i = iqr_val / (10^expv);
txt = sprintf('%.2f(%.2f)e%+d', m, i, expv);
end
