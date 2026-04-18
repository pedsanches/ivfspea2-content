%% integrate_modern_baselines_main.m
% Integrates AGE-MOEA-II and AR-MOEA archived runs into the main benchmark
% analysis without rerunning experiments.
%
% Outputs:
%   - data/processed/todas_metricas_consolidado_with_modern.csv
%   - results/tables/pairwise_vs_spea2_with_modern.csv
%   - results/tables/pairwise_ivf_vs_modern.csv
%   - results/tables/modern_baselines_coverage.csv

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
CORE_CSV = fullfile(PROJECT_ROOT, 'data', 'processed', 'todas_metricas_consolidado.csv');
MODERN_DIR = fullfile(PROJECT_ROOT, 'data', 'modern_baselines');
OUT_CSV = fullfile(PROJECT_ROOT, 'data', 'processed', 'todas_metricas_consolidado_with_modern.csv');
OUT_DIR = fullfile(PROJECT_ROOT, 'results', 'tables');

if ~exist(OUT_DIR, 'dir')
    mkdir(OUT_DIR);
end

ALPHA = 0.05;
MODERN_ALGOS = {'AGEMOEAII', 'ARMOEA'};

fprintf('Loading core consolidated CSV: %s\n', CORE_CSV);
Tcore = readtable(CORE_CSV, 'TextType', 'string');

text_cols = {'Grupo','Algoritmo','Problema','M','D','arquivo_original'};
for i = 1:numel(text_cols)
    c = text_cols{i};
    if ~isstring(Tcore.(c))
        Tcore.(c) = string(Tcore.(c));
    end
end

numeric_cols = {'Run','IGD','runtime','HV','Spread','IGDp','Spacing'};
for i = 1:numel(numeric_cols)
    c = numeric_cols{i};
    if ~isnumeric(Tcore.(c))
        Tcore.(c) = double(Tcore.(c));
    end
end

% Build expected (Problem, M, D) signatures from core synthetic benchmark.
is_synth = ~startsWith(Tcore.Problema, "RWMOP");
sig_tbl = unique(Tcore(is_synth, {'Problema','M','D'}), 'rows');
spec_set = containers.Map('KeyType', 'char', 'ValueType', 'logical');
for i = 1:height(sig_tbl)
    key = char(sig_tbl.Problema(i) + "|" + sig_tbl.M(i) + "|" + sig_tbl.D(i));
    if ~isKey(spec_set, key)
        spec_set(key) = true;
    end
end

fprintf('Scanning modern baseline MAT files in: %s\n', MODERN_DIR);
all_files = dir(fullfile(MODERN_DIR, '**', '*.mat'));

entries = struct('Algorithm', {}, 'Problem', {}, 'M', {}, 'D', {}, 'Run', {}, 'FileName', {}, 'Path', {});
key_to_idx = containers.Map('KeyType', 'char', 'ValueType', 'double');

for i = 1:numel(all_files)
    fname = all_files(i).name;
    fpath = fullfile(all_files(i).folder, fname);

    tok = regexp(fname, '^(AGEMOEAII|ARMOEA)_([A-Za-z0-9]+)_M(\d+)_D(\d+)_(\d+)\.mat$', 'tokens', 'once');
    if isempty(tok)
        continue;
    end

    algo = tok{1};
    prob = tok{2};
    mnum = str2double(tok{3});
    dnum = str2double(tok{4});
    run_id = str2double(tok{5});

    if ~ismember(algo, MODERN_ALGOS)
        continue;
    end
    if run_id < 1 || run_id > 60
        continue;
    end

    mtag = "M" + string(mnum);
    dtag = "D" + string(dnum);
    sig_key = char(string(prob) + "|" + mtag + "|" + dtag);
    if ~isKey(spec_set, sig_key)
        continue;
    end

    key = sprintf('%s|%s|M%d|run%d', algo, prob, mnum, run_id);
    if ~isKey(key_to_idx, key)
        entries(end+1) = struct( ...
            'Algorithm', algo, ...
            'Problem', prob, ...
            'M', mtag, ...
            'D', dtag, ...
            'Run', run_id, ...
            'FileName', fname, ...
            'Path', fpath ...
        );
        key_to_idx(key) = numel(entries);
    else
        idx_old = key_to_idx(key);
        old_path = entries(idx_old).Path;
        canonical_dir = fullfile(MODERN_DIR, sprintf('%s_%s_M%d', algo, prob, mnum));
        if prefer_new_path(old_path, fpath, canonical_dir)
            entries(idx_old).Path = fpath;
            entries(idx_old).FileName = fname;
        end
    end
end

if isempty(entries)
    error('No valid modern baseline MAT files found after filtering.');
end

% Read metric fields from MAT files.
n = numel(entries);
Grupo = strings(n,1);
Algoritmo = strings(n,1);
Problema = strings(n,1);
Run = zeros(n,1);
M = strings(n,1);
D = strings(n,1);
arquivo_original = strings(n,1);
IGD = nan(n,1);
runtime = nan(n,1);
HV = nan(n,1);
Spread = nan(n,1);
IGDp = nan(n,1);
Spacing = nan(n,1);

for i = 1:n
    Algoritmo(i) = string(entries(i).Algorithm);
    Problema(i) = string(entries(i).Problem);
    M(i) = string(entries(i).M);
    D(i) = string(entries(i).D);
    Run(i) = entries(i).Run;
    arquivo_original(i) = string(entries(i).FileName);
    Grupo(i) = infer_group(Problema(i));

    [IGD(i), runtime(i), HV(i), Spread(i), IGDp(i), Spacing(i)] = load_metrics(entries(i).Path);
end

Tmodern = table(Grupo, Algoritmo, Problema, Run, M, D, arquivo_original, IGD, runtime, HV, Spread, IGDp, Spacing);
Tmodern = Tmodern(~isnan(Tmodern.IGD), :);

% Merge with core table (dropping any pre-existing modern rows).
Tcore_nomodern = Tcore(~ismember(Tcore.Algoritmo, string(MODERN_ALGOS)), :);
Tmerged = [Tcore_nomodern; Tmodern];
Tmerged = sortrows(Tmerged, {'M','Problema','Algoritmo','Run'});

writetable(Tmerged, OUT_CSV);
fprintf('Wrote merged dataset: %s\n', OUT_CSV);

% Coverage report for modern baselines (synthetic only).
is_modern = ismember(Tmerged.Algoritmo, string(MODERN_ALGOS));
is_synth = ~startsWith(Tmerged.Problema, "RWMOP");
U = unique(Tmerged(is_modern & is_synth, {'Algoritmo','M','Problema'}), 'rows');

rows = {};
for ai = 1:numel(MODERN_ALGOS)
    a = string(MODERN_ALGOS{ai});
    for mtag = ["M2", "M3"]
        mask = Tmerged.Algoritmo == a & Tmerged.M == mtag & is_synth;
        probs = unique(Tmerged.Problema(mask));
        n_probs = numel(probs);
        run_counts = nan(n_probs,1);
        for p = 1:n_probs
            run_counts(p) = sum(mask & Tmerged.Problema == probs(p));
        end
        rows(end+1,:) = {a, mtag, n_probs, min(run_counts), max(run_counts), median(run_counts)}; %#ok<AGROW>
    end
end

Tcov = cell2table(rows, 'VariableNames', {'Algorithm','M','NumProblems','MinRunsPerProblem','MaxRunsPerProblem','MedianRunsPerProblem'});
writetable(Tcov, fullfile(OUT_DIR, 'modern_baselines_coverage.csv'));
fprintf('Wrote coverage report: %s\n', fullfile(OUT_DIR, 'modern_baselines_coverage.csv'));

% Unified pairwise: IVF/SPEA2 vs all baselines (from IVF/SPEA2 perspective).
all_baselines = {'SPEA2','MFOSPEA2','SPEA2SDE','NSGAII','NSGAIII','MOEAD','AGEMOEAII','ARMOEA'};

% --- IGD pairwise (lower is better) ---
Tivf_igd_raw = pairwise_vs_reference_metric(Tmerged, 'IVFSPEA2', all_baselines, ALPHA, 'IGD', false);
Tivf_igd = Tivf_igd_raw;
tmp = Tivf_igd.Wins;
Tivf_igd.Wins = Tivf_igd.Losses;
Tivf_igd.Losses = tmp;
writetable(Tivf_igd, fullfile(OUT_DIR, 'pairwise_ivf_vs_all.csv'));
fprintf('Wrote IGD pairwise summary: %s\n', fullfile(OUT_DIR, 'pairwise_ivf_vs_all.csv'));

% --- HV pairwise (higher is better) ---
Tivf_hv_raw = pairwise_vs_reference_metric(Tmerged, 'IVFSPEA2', all_baselines, ALPHA, 'HV', true);
Tivf_hv = Tivf_hv_raw;
tmp = Tivf_hv.Wins;
Tivf_hv.Wins = Tivf_hv.Losses;
Tivf_hv.Losses = tmp;
writetable(Tivf_hv, fullfile(OUT_DIR, 'pairwise_ivf_vs_all_hv.csv'));
fprintf('Wrote HV pairwise summary: %s\n', fullfile(OUT_DIR, 'pairwise_ivf_vs_all_hv.csv'));

% Legacy: also keep vs-SPEA2 for cross-check (IGD).
compare_algos = {'IVFSPEA2','MFOSPEA2','SPEA2SDE','NSGAII','NSGAIII','MOEAD','AGEMOEAII','ARMOEA'};
Tpair = pairwise_vs_reference_metric(Tmerged, 'SPEA2', compare_algos, ALPHA, 'IGD', false);
writetable(Tpair, fullfile(OUT_DIR, 'pairwise_vs_spea2_with_modern.csv'));

% Also vs-SPEA2 for HV.
Tpair_hv = pairwise_vs_reference_metric(Tmerged, 'SPEA2', compare_algos, ALPHA, 'HV', true);
writetable(Tpair_hv, fullfile(OUT_DIR, 'pairwise_vs_spea2_with_modern_hv.csv'));

fprintf('\nDone. Key pairwise counts (IVF/SPEA2 vs all):\n');
fprintf('\n--- IGD (lower is better) ---\n');
disp(Tivf_igd);
fprintf('\n--- HV (higher is better) ---\n');
disp(Tivf_hv);


function g = infer_group(problem)
if startsWith(problem, "ZDT")
    g = "ZDT";
elseif startsWith(problem, "DTLZ")
    g = "DTLZ";
elseif startsWith(problem, "WFG")
    g = "WFG";
elseif startsWith(problem, "MaF")
    g = "MaF";
elseif startsWith(problem, "RWMOP")
    g = "RWMOP";
else
    g = extractBefore(problem + "___", "_");
end
end


function [igd, rt, hv, spread, igdp, spacing] = load_metrics(mat_path)
igd = NaN;
rt = NaN;
hv = NaN;
spread = NaN;
igdp = NaN;
spacing = NaN;

try
    s = load(mat_path, 'metric');
    if ~isfield(s, 'metric') || ~isstruct(s.metric)
        return;
    end
    m = s.metric;

    if isfield(m, 'IGD')
        igd = scalar_last(m.IGD);
    end
    if isfield(m, 'runtime')
        rt = scalar_last(m.runtime);
    end
    if isfield(m, 'HV')
        hv = scalar_last(m.HV);
    end
    if isfield(m, 'Spread')
        spread = scalar_last(m.Spread);
    end
    if isfield(m, 'IGDp')
        igdp = scalar_last(m.IGDp);
    end
    if isfield(m, 'Spacing')
        spacing = scalar_last(m.Spacing);
    end
catch
    igd = NaN;
end
end


function v = scalar_last(x)
v = NaN;
if isempty(x)
    return;
end
if isnumeric(x)
    xx = x(:);
    v = double(xx(end));
    return;
end
if iscell(x)
    try
        y = x{end};
        if isnumeric(y)
            yy = y(:);
            v = double(yy(end));
        end
    catch
        v = NaN;
    end
end
end


function Tsummary = pairwise_vs_reference_metric(T, ref_algo, algos, alpha, metric_name, higher_is_better)
% Generic pairwise comparison for any metric column.
%   metric_name     : column name in T (e.g. 'IGD', 'HV')
%   higher_is_better: logical — true for HV, false for IGD
rows = {};
for mtag = ["M2", "M3"]
    for ai = 1:numel(algos)
        algo = string(algos{ai});
        probs_ref = unique(T.Problema(T.M == mtag & T.Algoritmo == ref_algo));
        probs_alg = unique(T.Problema(T.M == mtag & T.Algoritmo == algo));
        probs = intersect(probs_ref, probs_alg);

        plus = 0;
        eq = 0;
        minus = 0;

        for pi = 1:numel(probs)
            p = probs(pi);
            x_alg = T.(metric_name)(T.M == mtag & T.Problema == p & T.Algoritmo == algo);
            x_ref = T.(metric_name)(T.M == mtag & T.Problema == p & T.Algoritmo == ref_algo);
            sgn = wilcoxon_sign_metric(x_alg, x_ref, alpha, higher_is_better);
            if sgn == '+'
                plus = plus + 1;
            elseif sgn == '-'
                minus = minus + 1;
            else
                eq = eq + 1;
            end
        end

        rows(end+1,:) = {char(mtag), char(ref_algo), char(algo), plus, minus, eq, numel(probs)}; %#ok<AGROW>
    end
end

Tsummary = cell2table(rows, 'VariableNames', ...
    {'M','Reference','Algorithm','Wins','Losses','Ties','NumProblems'});
end


function sgn = wilcoxon_sign_metric(x_a, x_b, alpha, higher_is_better)
% Generic Wilcoxon rank-sum sign test for any metric.
%   higher_is_better = false  →  lower is better  (IGD)
%   higher_is_better = true   →  higher is better (HV)
% Returns sign from the perspective of the first sample:
% '+' = first sample significantly better; '-' = significantly worse; '=' tie.
sgn = '=';
x_a = x_a(~isnan(x_a));
x_b = x_b(~isnan(x_b));
if numel(x_a) < 3 || numel(x_b) < 3
    return;
end

p = ranksum(x_a, x_b);
if p < alpha
    m_a = median(x_a);
    m_b = median(x_b);
    if higher_is_better
        % HV: higher is better
        if m_a > m_b
            sgn = '+';
        elseif m_a < m_b
            sgn = '-';
        end
    else
        % IGD: lower is better
        if m_a < m_b
            sgn = '+';
        elseif m_a > m_b
            sgn = '-';
        end
    end
end
end


function tf = prefer_new_path(old_path, new_path, canonical_dir)
old_norm = strrep(old_path, '\\', '/');
new_norm = strrep(new_path, '\\', '/');
can_norm = strrep(canonical_dir, '\\', '/');

old_is_canonical = startsWith(old_norm, can_norm);
new_is_canonical = startsWith(new_norm, can_norm);

if new_is_canonical && ~old_is_canonical
    tf = true;
elseif ~new_is_canonical && old_is_canonical
    tf = false;
else
    tf = false;
end
end
