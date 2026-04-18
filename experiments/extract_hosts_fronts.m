%% extract_hosts_fronts.m
% Extract final-population objective vectors from PlatEMO .mat result files
% for Pareto-front overlay figures in the IVF hosts paper.
%
% Selected cases (M=2 only):
%   1) DTLZ2, M=2, D=11  (gain scenario)
%   2) WFG4,  M=2, D=11  (neutral scenario)
%   3) MaF1,  M=2, D=11  (adverse scenario)
%
% Six algorithms are extracted per case:
%   IVF variants : IVFSPEA2, IVFNSGAII, IVFNSGAIII
%   Base hosts   : SPEA2,    NSGAII,    NSGAIII
%
% Output CSVs:
%   data/processed/fronts/hosts/
%     <PROBLEM>_M2_<ALGO>_median.csv   (columns: f1, f2)
%     <PROBLEM>_M2_truePF.csv
%
% Usage from project root:
%   matlab -batch "run('experiments/extract_hosts_fronts.m')"

fprintf('=== Extracting Pareto fronts for hosts paper figures ===\n');

script_dir   = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);

platemo_root = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
addpath(genpath(platemo_root));

outdir = fullfile(project_root, 'data', 'processed', 'fronts', 'hosts');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

data_root         = fullfile(platemo_root, 'Data');
data_original_root = fullfile(platemo_root, 'Data_original');

%% =========================================================================
%% Algorithm data-directory mapping
%% =========================================================================
%
%  IVFSPEA2  → Data_original/IVFSPEA2/   (all *.mat)
%  SPEA2     → Data_original/SPEA2/      (all *.mat)
%  IVFNSGAII → Data/IVFNSGAII/           (*_40*.mat)
%  NSGAII    → Data/NSGAII/              (*_40*.mat)
%  IVFNSGAIII→ Data/IVFNSGAIII/          (*_50*.mat)
%  NSGAIII   → Data/NSGAIII/             (*_50*.mat)

algo_config = {
    'IVFSPEA2',   fullfile(data_original_root, 'IVFSPEA2'),  '*.mat';
    'SPEA2',      fullfile(data_original_root, 'SPEA2'),     '*.mat';
    'IVFNSGAII',  fullfile(data_root, 'IVFNSGAII'),          '*_40*.mat';
    'NSGAII',     fullfile(data_root, 'NSGAII'),             '*_40*.mat';
    'IVFNSGAIII', fullfile(data_root, 'IVFNSGAIII'),         '*_50*.mat';
    'NSGAIII',    fullfile(data_root, 'NSGAIII'),            '*_50*.mat';
};

%% =========================================================================
%% Cases to extract
%% =========================================================================

cases = {
    'DTLZ2', 2, 11;
    'WFG4',  2, 11;
    'MaF1',  2, 11;
};

%% =========================================================================
%% Main extraction loop
%% =========================================================================

for ci = 1:size(cases, 1)
    prob_name = cases{ci, 1};
    M_val     = cases{ci, 2};
    D_val     = cases{ci, 3};

    fprintf('\n--- %s M=%d D=%d ---\n', prob_name, M_val, D_val);

    % ---- True Pareto front ----
    pf_csv = fullfile(outdir, sprintf('%s_M%d_truePF.csv', prob_name, M_val));
    if ~isfile(pf_csv)
        try
            prob_handle = str2func(prob_name);
            prob_obj    = prob_handle('M', M_val, 'D', D_val);
            true_pf     = prob_obj.GetOptimum(1000);
            T_pf = array2table(true_pf, 'VariableNames', {'f1', 'f2'});
            writetable(T_pf, pf_csv);
            fprintf('  True PF: %d points → %s\n', size(true_pf, 1), pf_csv);
        catch err
            warning('Could not generate true PF for %s: %s', prob_name, err.message);
        end
    else
        fprintf('  True PF already exists, skipping.\n');
    end

    % ---- Algorithm fronts ----
    for ai = 1:size(algo_config, 1)
        algo    = algo_config{ai, 1};
        adir    = algo_config{ai, 2};
        pattern = algo_config{ai, 3};

        % Build problem-specific pattern:
        %   e.g.  *DTLZ2_M2_D11_40*.mat  or  *DTLZ2_M2_D11*.mat
        if strcmp(pattern, '*.mat')
            prob_pattern = sprintf('*%s_M%d_D%d*.mat', prob_name, M_val, D_val);
        else
            % Extract run-ID suffix from pattern (e.g. '*_40*.mat')
            [tok] = regexp(pattern, '\*(_\d+\*)', 'tokens', 'once');
            if ~isempty(tok)
                suffix = tok{1};  % e.g. '_40*'
                prob_pattern = sprintf('*%s_M%d_D%d%s.mat', prob_name, M_val, D_val, suffix);
            else
                prob_pattern = sprintf('*%s_M%d_D%d*.mat', prob_name, M_val, D_val);
            end
        end

        matfiles = local_list_files(adir, prob_pattern);
        fprintf('  %s: %d files (pattern: %s)\n', algo, numel(matfiles), prob_pattern);

        if isempty(matfiles)
            fprintf('    SKIPPED (no files found in %s)\n', adir);
            continue;
        end

        try
            [med_file, med_igd] = local_find_median_run(matfiles);
            fprintf('    Median run: %s (IGD=%.6g)\n', med_file, med_igd);

            objs = local_extract_objectives(med_file);
            fprintf('    Population: %d solutions, %d objectives\n', size(objs, 1), size(objs, 2));

            if size(objs, 2) ~= M_val
                warning('Expected %d objectives for %s %s, found %d. Skipping.', ...
                    M_val, algo, prob_name, size(objs, 2));
                continue;
            end

            T = array2table(objs, 'VariableNames', {'f1', 'f2'});
            out_name = sprintf('%s_M%d_%s_median.csv', prob_name, M_val, algo);
            writetable(T, fullfile(outdir, out_name));
            fprintf('    Saved: %s\n', out_name);
        catch err
            warning('Failed to extract %s for %s M%d: %s', algo, prob_name, M_val, err.message);
        end
    end
end

fprintf('\n=== Done. CSVs saved to: %s ===\n', outdir);
fprintf('Next step: python src/python/analysis/plot_hosts_fronts.py\n');


%% ===== Local helpers (copied from extract_fronts_for_paper.m) =====

function folder = local_pick_ivf_dir(data_root)
    candidates = {'IVFSPEA2', 'IVFSPEA2V2'};
    best_count = -1;
    folder = '';
    for i = 1:numel(candidates)
        c = fullfile(data_root, candidates{i});
        if ~isfolder(c)
            continue;
        end
        n = numel(dir(fullfile(c, '*_30*.mat')));
        if n > best_count
            best_count = n;
            folder = c;
        end
    end
    if isempty(folder)
        error('Could not locate IVF data folder under %s', data_root);
    end
end

function paths = local_list_files(folder, pattern)
    if ~isfolder(folder)
        paths = {};
        return;
    end
    files = dir(fullfile(folder, pattern));
    if isempty(files)
        paths = {};
        return;
    end
    [~, idx] = sort({files.name});
    files = files(idx);
    paths = arrayfun(@(f) fullfile(f.folder, f.name), files, 'UniformOutput', false);
end

function [median_file, median_igd] = local_find_median_run(matfiles)
    n = numel(matfiles);
    igd_vals = nan(n, 1);
    for i = 1:n
        S = load(matfiles{i}, 'metric');
        if ~isfield(S, 'metric')
            error('File %s does not contain field "metric".', matfiles{i});
        end
        igd_vals(i) = local_final_igd(S.metric);
    end

    if all(isnan(igd_vals))
        error('Unable to extract IGD from provided files.');
    end

    med = median(igd_vals, 'omitnan');
    [~, idx] = min(abs(igd_vals - med));
    median_file = matfiles{idx};
    median_igd = igd_vals(idx);
end

function igd = local_final_igd(metric)
    igd = NaN;
    if isstruct(metric)
        if isfield(metric, 'IGD')
            vals = metric.IGD;
            igd = vals(end);
            return;
        end
    end
    if iscell(metric)
        vals = metric{end};
        if isnumeric(vals)
            igd = vals(end);
            return;
        end
    end
    error('Unsupported metric format for IGD extraction.');
end

function objs = local_extract_objectives(matfile)
    S = load(matfile, 'result');
    if ~isfield(S, 'result')
        error('File %s does not contain field "result".', matfile);
    end

    result = S.result;
    last_idx = size(result, 1);
    solutions = result{last_idx, 2};

    if isa(solutions, 'SOLUTION')
        objs = solutions.objs;
        return;
    end

    if isobject(solutions)
        try
            objs = cat(1, solutions.obj);
            return;
        catch
            objs = solutions.objs;
            return;
        end
    end

    error('Cannot extract objectives from %s', matfile);
end
