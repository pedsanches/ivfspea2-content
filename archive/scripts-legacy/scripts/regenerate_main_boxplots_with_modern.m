%% regenerate_main_boxplots_with_modern.m
% Regenerates main synthetic-benchmark IGD boxplots including modern baselines
% (AGE-MOEA-II and AR-MOEA) from archived consolidated data.
%
% Inputs:
%   - data/processed/todas_metricas_consolidado_with_modern.csv
%
% Outputs:
%   - results/figures/boxplot_igd_M2_all_problems_with_modern.pdf
%   - results/figures/boxplot_igd_M3_all_problems_with_modern.pdf
%   - paper/figures/results_m2.pdf
%   - paper/figures/results_m3.pdf

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
IN_CSV = fullfile(PROJECT_ROOT, 'data', 'processed', 'todas_metricas_consolidado_with_modern.csv');
OUT_RESULTS_DIR = fullfile(PROJECT_ROOT, 'results', 'figures');
OUT_PAPER_DIR = fullfile(PROJECT_ROOT, 'paper', 'figures');

if ~exist(OUT_RESULTS_DIR, 'dir')
    mkdir(OUT_RESULTS_DIR);
end
if ~exist(OUT_PAPER_DIR, 'dir')
    mkdir(OUT_PAPER_DIR);
end

T = readtable(IN_CSV, 'TextType', 'string');
T = T(~startsWith(T.Problema, "RWMOP"), :);

alg_order = ["IVFSPEA2", "SPEA2", "MFOSPEA2", "SPEA2SDE", "NSGAII", "NSGAIII", "MOEAD", "AGEMOEAII", "ARMOEA"];
alg_labels = {'IVF/SPEA2', 'SPEA2', 'MFO-SPEA2', 'SPEA2+SDE', 'NSGA-II', 'NSGA-III', 'MOEA/D', 'AGE-II', 'AR-MOEA'};

for mtag = ["M2", "M3"]
    S = T(T.M == mtag, :);
    probs = unique(S.Problema);
    probs = sort_problem_names(probs);

    n_probs = numel(probs);
    ncols = 3;
    nrows = ceil(n_probs / ncols);

    % Springer large-journal guidance target: ~174 mm width and <=234 mm height
    fig_width_in = 6.85;
    if mtag == "M2"
        fig_height_in = 9.15;
    else
        fig_height_in = 8.90;
    end

    f = figure('Visible', 'off', 'Units', 'inches', ...
        'Position', [0.4 0.4 fig_width_in fig_height_in], 'Color', 'w');

    for pi = 1:n_probs
        subplot(nrows, ncols, pi);
        p = probs(pi);

        vals = [];
        grp = [];
        for ai = 1:numel(alg_order)
            v = S.IGD(S.Problema == p & S.Algoritmo == alg_order(ai));
            v = v(~isnan(v));
            if isempty(v)
                continue;
            end
            vals = [vals; v]; %#ok<AGROW>
            grp = [grp; repmat(ai, numel(v), 1)]; %#ok<AGROW>
        end

        if isempty(vals)
            axis off;
            title(sprintf('%s (no data)', char(p)), 'Interpreter', 'none', 'FontSize', 9);
            continue;
        end

        boxplot(vals, grp, 'Labels', alg_labels, 'Symbol', '.');
        title(char(p), 'Interpreter', 'none', 'FontSize', 9);
        ylabel('IGD');
        set(gca, 'FontName', 'Helvetica', 'FontSize', 6.5, ...
            'XTickLabelRotation', 35, 'TickDir', 'out', 'LineWidth', 0.6);
        grid on;
        box on;
    end

    sgtitle(sprintf('IGD distribution by problem (%s) - includes AGE-II and AR-MOEA', char(mtag)), 'FontSize', 11);

    out_results = fullfile(OUT_RESULTS_DIR, sprintf('boxplot_igd_%s_all_problems_with_modern.pdf', char(mtag)));
    out_paper = fullfile(OUT_PAPER_DIR, sprintf('results_%s.pdf', lower(char(mtag))));

    exportgraphics(f, out_results, 'ContentType', 'vector');
    exportgraphics(f, out_paper, 'ContentType', 'vector');
    close(f);

    fprintf('Wrote: %s\n', out_results);
    fprintf('Wrote: %s\n', out_paper);
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
elseif startsWith(p, "RWMOP")
    s = 5;
    k = parse_suffix_number(extractAfter(p, "RWMOP"));
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
