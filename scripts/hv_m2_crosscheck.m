%% hv_m2_crosscheck.m
% Cross-check IVF/SPEA2 vs SPEA2 on M=2 using IGD and HV.
% Uses existing consolidated metrics only (no new experiments).

clear; clc;

project_root = '/home/pedro/desenvolvimento/ivfspea2';
in_csv = fullfile(project_root, 'data', 'processed', 'todas_metricas_consolidado.csv');
out_csv = fullfile(project_root, 'results', 'tables', 'hv_igd_crosscheck_m2_ivf_vs_spea2.csv');

alpha = 0.05;

T = readtable(in_csv);
T = T(strcmp(T.M, 'M2'), :);

problems = unique(T.Problema);
n_prob = numel(problems);

rows = cell(n_prob, 13);

for i = 1:n_prob
    p = problems{i};

    x_igd = T.IGD(strcmp(T.Problema, p) & strcmp(T.Algoritmo, 'IVFSPEA2'));
    y_igd = T.IGD(strcmp(T.Problema, p) & strcmp(T.Algoritmo, 'SPEA2'));

    x_hv = T.HV(strcmp(T.Problema, p) & strcmp(T.Algoritmo, 'IVFSPEA2'));
    y_hv = T.HV(strcmp(T.Problema, p) & strcmp(T.Algoritmo, 'SPEA2'));
    x_hv = x_hv(~isnan(x_hv));
    y_hv = y_hv(~isnan(y_hv));

    [igd_sign, igd_p, igd_med_i, igd_med_s] = sign_igd(x_igd, y_igd, alpha);
    [hv_sign, hv_p, hv_med_i, hv_med_s] = sign_hv(x_hv, y_hv, alpha);

    rows{i,1} = p;
    rows{i,2} = numel(x_igd);
    rows{i,3} = numel(y_igd);
    rows{i,4} = numel(x_hv);
    rows{i,5} = numel(y_hv);
    rows{i,6} = igd_med_i;
    rows{i,7} = igd_med_s;
    rows{i,8} = igd_p;
    rows{i,9} = igd_sign;
    rows{i,10} = hv_med_i;
    rows{i,11} = hv_med_s;
    rows{i,12} = hv_p;
    rows{i,13} = hv_sign;
end

R = cell2table(rows, 'VariableNames', { ...
    'Problem', 'N_IGD_IVF', 'N_IGD_SPEA2', 'N_HV_IVF', 'N_HV_SPEA2', ...
    'IGD_Med_IVF', 'IGD_Med_SPEA2', 'IGD_p', 'IGD_sign', ...
    'HV_Med_IVF', 'HV_Med_SPEA2', 'HV_p', 'HV_sign'});

R = sortrows(R, 'Problem');
writetable(R, out_csv);

% Count summaries
igd_valid = ~cellfun(@isempty, R.IGD_sign);
hv_valid = ~cellfun(@isempty, R.HV_sign);

igd_plus = sum(strcmp(R.IGD_sign(igd_valid), '+'));
igd_eq = sum(strcmp(R.IGD_sign(igd_valid), '='));
igd_minus = sum(strcmp(R.IGD_sign(igd_valid), '-'));

hv_plus = sum(strcmp(R.HV_sign(hv_valid), '+'));
hv_eq = sum(strcmp(R.HV_sign(hv_valid), '='));
hv_minus = sum(strcmp(R.HV_sign(hv_valid), '-'));

% Holm-Bonferroni for HV
idx_hv = find(hv_valid);
p_hv = R.HV_p(idx_hv);
[p_sorted, ord] = sort(p_hv);
m = numel(p_sorted);
rej = false(m,1);
for k = 1:m
    if p_sorted(k) <= alpha / (m - k + 1)
        rej(k) = true;
    else
        break;
    end
end

holm_signs = repmat({'='}, m, 1);
for k = 1:m
    if rej(k)
        row_idx = idx_hv(ord(k));
        med_i = R.HV_Med_IVF(row_idx);
        med_s = R.HV_Med_SPEA2(row_idx);
        if med_i > med_s
            holm_signs{k} = '+';
        elseif med_i < med_s
            holm_signs{k} = '-';
        else
            holm_signs{k} = '=';
        end
    end
end

holm_plus = sum(strcmp(holm_signs, '+'));
holm_eq = sum(strcmp(holm_signs, '='));
holm_minus = sum(strcmp(holm_signs, '-'));

% Concordance on problems with both signs available
both = hv_valid & igd_valid;
exact_agree = sum(strcmp(R.IGD_sign(both), R.HV_sign(both)));

fprintf('M2 problems (IGD valid): %d\n', sum(igd_valid));
fprintf('IGD raw +/=/- : %d/%d/%d\n', igd_plus, igd_eq, igd_minus);
fprintf('M2 problems (HV valid): %d\n', sum(hv_valid));
fprintf('HV raw +/=/- : %d/%d/%d\n', hv_plus, hv_eq, hv_minus);
fprintf('HV Holm +/=/-: %d/%d/%d\n', holm_plus, holm_eq, holm_minus);
fprintf('IGD/HV exact sign agreement (M2): %d/%d\n', exact_agree, sum(both));
fprintf('Wrote %s\n', out_csv);


function [s, p, med_x, med_y] = sign_igd(x, y, alpha)
s = '';
p = NaN;
med_x = NaN;
med_y = NaN;

if numel(x) < 3 || numel(y) < 3
    return;
end

med_x = median(x);
med_y = median(y);
p = ranksum(x, y);

if p < alpha
    if med_x < med_y
        s = '+';
    elseif med_x > med_y
        s = '-';
    else
        s = '=';
    end
else
    s = '=';
end
end


function [s, p, med_x, med_y] = sign_hv(x, y, alpha)
s = '';
p = NaN;
med_x = NaN;
med_y = NaN;

if numel(x) < 3 || numel(y) < 3
    return;
end

med_x = median(x);
med_y = median(y);
p = ranksum(x, y);

if p < alpha
    if med_x > med_y
        s = '+';
    elseif med_x < med_y
        s = '-';
    else
        s = '=';
    end
else
    s = '=';
end
end
