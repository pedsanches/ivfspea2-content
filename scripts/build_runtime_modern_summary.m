%% build_runtime_modern_summary.m
% Builds an aggregated runtime summary including modern baselines
% (AGE-MOEA-II and AR-MOEA) from existing local consolidated data.
%
% Outputs:
%   - results/tables/runtime_modern_summary.csv

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
IN_CSV = fullfile(PROJECT_ROOT, 'data', 'processed', 'todas_metricas_consolidado_with_modern.csv');
OUT_CSV = fullfile(PROJECT_ROOT, 'results', 'tables', 'runtime_modern_summary.csv');

T = readtable(IN_CSV, 'TextType', 'string');

% Synthetic suites only (exclude engineering case).
T = T(~startsWith(T.Problema, "RWMOP"), :);

algorithms = ["IVFSPEA2", "SPEA2", "AGEMOEAII", "ARMOEA"];
rows = {};

for mtag = ["M2", "M3"]
    TM = T(T.M == mtag, :);
    probs = unique(TM.Problema);
    n_probs = numel(probs);

    per_problem = struct();
    for a = algorithms
        vals = nan(n_probs, 1);
        for p = 1:n_probs
            S = TM(TM.Algoritmo == a & TM.Problema == probs(p), :);
            if ~isempty(S)
                vals(p) = mean(S.runtime, 'omitnan');
            end
        end
        per_problem.(char(a)) = vals;
    end

    t_ivf = mean(per_problem.IVFSPEA2, 'omitnan');
    t_spea2 = mean(per_problem.SPEA2, 'omitnan');
    t_age = mean(per_problem.AGEMOEAII, 'omitnan');
    t_ar = mean(per_problem.ARMOEA, 'omitnan');

    rho_ivf_spea2 = mean(per_problem.IVFSPEA2 ./ per_problem.SPEA2, 'omitnan');
    rho_ivf_age = mean(per_problem.IVFSPEA2 ./ per_problem.AGEMOEAII, 'omitnan');
    rho_ivf_ar = mean(per_problem.IVFSPEA2 ./ per_problem.ARMOEA, 'omitnan');

    rows(end+1, :) = {mtag, n_probs, t_ivf, t_spea2, t_age, t_ar, rho_ivf_spea2, rho_ivf_age, rho_ivf_ar}; %#ok<AGROW>
end

Tout = cell2table(rows, 'VariableNames', {
    'M', 'NumProblems', 'IVFSPEA2_mean_runtime_s', 'SPEA2_mean_runtime_s', ...
    'AGEMOEAII_mean_runtime_s', 'ARMOEA_mean_runtime_s', ...
    'rho_IVF_over_SPEA2', 'rho_IVF_over_AGEMOEAII', 'rho_IVF_over_ARMOEA'});

writetable(Tout, OUT_CSV);
fprintf('Wrote runtime summary: %s\n', OUT_CSV);
disp(Tout);
