%% build_detailed_tables_with_modern.m
% Builds detailed IGD tables (M2/M3) including modern baselines
% AGE-MOEA-II and AR-MOEA, with best-per-problem values in bold.
%
% Inputs:
%   - data/processed/todas_metricas_consolidado_with_modern.csv
%
% Outputs:
%   - results/tables/igd_m2_detailed_with_modern_table.tex
%   - results/tables/igd_m3_detailed_with_modern_table.tex

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
IN_CSV = fullfile(PROJECT_ROOT, 'data', 'processed', 'todas_metricas_consolidado_with_modern.csv');
OUT_DIR = fullfile(PROJECT_ROOT, 'results', 'tables');

if ~exist(OUT_DIR, 'dir')
    mkdir(OUT_DIR);
end

ALPHA = 0.05;

% Keep IVF/SPEA2 in the rightmost column (reviewer request)
alg_order = ["MFOSPEA2", "SPEA2SDE", "NSGAII", "NSGAIII", "MOEAD", "AGEMOEAII", "ARMOEA", "SPEA2", "IVFSPEA2"];
alg_header = {'MFO-SPEA2', 'SPEA2+SDE', 'NSGA-II', 'NSGA-III', 'MOEA/D', 'AGE-MOEA-II', 'AR-MOEA', 'SPEA2', 'IVF/SPEA2'};

T = readtable(IN_CSV, 'TextType', 'string');
T = T(~startsWith(T.Problema, "RWMOP"), :);

% Canonical synthetic run cohorts:
%   - IVF/SPEA2 v2 submission track: runs 3001..3060
%   - Baselines: runs 1..60
if ~isnumeric(T.Run)
    T.Run = str2double(string(T.Run));
end
is_ivf = T.Algoritmo == "IVFSPEA2";
keep_ivf = is_ivf & T.Run >= 3001 & T.Run <= 3060;
keep_base = ~is_ivf & T.Run >= 1 & T.Run <= 60;
T = T(keep_ivf | keep_base, :);

for mtag = ["M2", "M3"]
    TM = T(T.M == mtag, :);
    probs = unique(TM.Problema);
    probs = sort_problem_names(probs);

    lines = {};
    lines{end+1} = '\begin{table*}[tp]'; %#ok<AGROW>
    if mtag == "M2"
        cap = ['\caption{Comparison of IGD (median) between IVF/SPEA2 and baselines for $M=2$ ', ...
               '(ZDT1--ZDT6, DTLZ1--DTLZ7, WFG1--WFG9, and MaF1--MaF7), including AGE-MOEA-II and AR-MOEA. ', ...
               'Symbols $+$, $-$, and $=$ are from unadjusted Wilcoxon rank-sum tests ($p<0.05$) and are reported from IVF/SPEA2''s perspective in each baseline column: $+$ means IVF/SPEA2 is better, $-$ worse, and $=$ no significant difference against the column algorithm (e.g., in the SPEA2 column, $+$ means IVF/SPEA2 beats SPEA2). ', ...
               'The IVF/SPEA2 column is reported without a significance symbol. ', ...
               'Best median per instance in \textbf{bold}.}\label{tab:igd_m2_detailed}%'];
    else
        cap = ['\caption{Comparison of IGD (median) between IVF/SPEA2 and baselines for $M=3$ ', ...
               '(DTLZ1--DTLZ7, WFG1--WFG9, and MaF1--MaF7), including AGE-MOEA-II and AR-MOEA. ', ...
               'Symbols $+$, $-$, and $=$ are from unadjusted Wilcoxon rank-sum tests ($p<0.05$) and are reported from IVF/SPEA2''s perspective in each baseline column: $+$ means IVF/SPEA2 is better, $-$ worse, and $=$ no significant difference against the column algorithm (e.g., in the SPEA2 column, $+$ means IVF/SPEA2 beats SPEA2). ', ...
               'The IVF/SPEA2 column is reported without a significance symbol. ', ...
               'Best median per instance in \textbf{bold}.}\label{tab:igd_m3_detailed}%'];
    end
    lines{end+1} = cap; %#ok<AGROW>
    lines{end+1} = '\centering'; %#ok<AGROW>
    lines{end+1} = '\scriptsize'; %#ok<AGROW>
    lines{end+1} = '\setlength{\tabcolsep}{2.9pt}'; %#ok<AGROW>
    lines{end+1} = '\resizebox{\textwidth}{!}{%'; %#ok<AGROW>
    lines{end+1} = '\begin{tabular}{lrrrrrrrrrr}'; %#ok<AGROW>
    lines{end+1} = '\toprule'; %#ok<AGROW>
    lines{end+1} = ['Problem & $D$ & ', strjoin(alg_header, ' & '), ' \\']; %#ok<AGROW>
    lines{end+1} = '\midrule'; %#ok<AGROW>

    prev_suite = "";
    for pi = 1:numel(probs)
        p = probs(pi);
        suite = suite_name(p);
        if pi > 1 && suite ~= prev_suite
            lines{end+1} = '\midrule'; %#ok<AGROW>
        end
        prev_suite = suite;

        Tp = TM(TM.Problema == p, :);
        dstr = string(Tp.D(1));
        dnum = str2double(erase(dstr, "D"));
        if isnan(dnum)
            dnum = 0;
        end

        meds = nan(numel(alg_order), 1);
        vals_by_alg = cell(numel(alg_order), 1);
        for ai = 1:numel(alg_order)
            a = alg_order(ai);
            v = Tp.IGD(Tp.Algoritmo == a);
            v = v(~isnan(v));
            vals_by_alg{ai} = v;
            if ~isempty(v)
                meds(ai) = median(v);
            end
        end

        best_mask = false(numel(alg_order),1);
        if any(~isnan(meds))
            mmin = min(meds, [], 'omitnan');
            tol = max(1e-14, 1e-10 * max(1, abs(mmin)));
            best_mask = abs(meds - mmin) <= tol;
        end

        ivf_vals = vals_by_alg{alg_order == "IVFSPEA2"};

        cells = strings(1, numel(alg_order));
        for ai = 1:numel(alg_order)
            a = alg_order(ai);
            v = vals_by_alg{ai};

            if isempty(v)
                cells(ai) = "---";
                continue;
            end

            med_tex = sci_tex(median(v));
            if best_mask(ai)
                med_tex = "\mathbf{" + med_tex + "}";
            end

            ind = "";
            if a == "IVFSPEA2"
                ind = "";
            else
                ind = wilcoxon_sign_igd(ivf_vals, v, ALPHA);
            end

            if ind == ""
                cells(ai) = "\(\," + med_tex + "\,\)";
            else
                cells(ai) = "\(\," + med_tex + "\,^{" + ind + "}\)";
            end
        end

        row = string(p) + " & " + string(dnum);
        for ai = 1:numel(alg_order)
            row = row + " & " + cells(ai);
        end
        row = row + " " + string(char([92 92]));
        lines{end+1} = char(row); %#ok<AGROW>
    end

    lines{end+1} = '\botrule'; %#ok<AGROW>
    lines{end+1} = '\end{tabular}'; %#ok<AGROW>
    lines{end+1} = '}% end resizebox'; %#ok<AGROW>
    lines{end+1} = '\end{table*}'; %#ok<AGROW>

    if mtag == "M2"
        out_file = fullfile(OUT_DIR, 'igd_m2_detailed_with_modern_table.tex');
    else
        out_file = fullfile(OUT_DIR, 'igd_m3_detailed_with_modern_table.tex');
    end

    fid = fopen(out_file, 'w');
    assert(fid ~= -1, 'Cannot write %s', out_file);
    for i = 1:numel(lines)
        fprintf(fid, '%s\n', lines{i});
    end
    fclose(fid);

    fprintf('Wrote: %s\n', out_file);
end


function out = sci_tex(v)
if v == 0
    out = '0';
    return;
end
e = floor(log10(abs(v)));
m = v / (10^e);
out = sprintf('%.4f\\times 10^{%d}', m, e);
end


function s = suite_name(p)
p = string(p);
if startsWith(p, "ZDT")
    s = "ZDT";
elseif startsWith(p, "DTLZ")
    s = "DTLZ";
elseif startsWith(p, "WFG")
    s = "WFG";
elseif startsWith(p, "MaF")
    s = "MaF";
else
    s = "OTHER";
end
end


function sorted = sort_problem_names(probs)
probs = string(probs(:));
n = numel(probs);
suite_rank = zeros(n,1);
num_rank = zeros(n,1);
for i = 1:n
    [suite_rank(i), num_rank(i)] = problem_rank(probs(i));
end
[~, idx] = sortrows([suite_rank, num_rank]);
sorted = probs(idx);
end


function [s, k] = problem_rank(p)
p = string(p);
s = 99;
k = 0;
if startsWith(p, "ZDT")
    s = 1;
    k = parse_suffix_number(extractAfter(p, "ZDT"));
elseif startsWith(p, "DTLZ")
    s = 2;
    k = parse_suffix_number(extractAfter(p, "DTLZ"));
elseif startsWith(p, "WFG")
    s = 3;
    k = parse_suffix_number(extractAfter(p, "WFG"));
elseif startsWith(p, "MaF")
    s = 4;
    k = parse_suffix_number(extractAfter(p, "MaF"));
end
end


function n = parse_suffix_number(x)
x = char(x);
tok = regexp(x, '\\d+', 'match', 'once');
if isempty(tok)
    n = 0;
else
    n = str2double(tok);
end
end


function sgn = wilcoxon_sign_igd(x_a, x_b, alpha)
% Returns sign from the perspective of first sample (lower IGD is better):
% '+' better, '-' worse, '=' tie.
sgn = "=";
x_a = x_a(~isnan(x_a));
x_b = x_b(~isnan(x_b));

if numel(x_a) < 3 || numel(x_b) < 3
    return;
end

p = ranksum(x_a, x_b);
if p < alpha
    m_a = median(x_a);
    m_b = median(x_b);
    if m_a < m_b
        sgn = "+";
    elseif m_a > m_b
        sgn = "-";
    else
        sgn = "=";
    end
end
end
