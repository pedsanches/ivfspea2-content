%% extract_fronts_for_paper.m
% Extract final-population objective vectors from PlatEMO .mat runs
% for Pareto-front visualizations in the paper.
%
% Selected cases:
%   1) DTLZ2, M=2  (success pattern)
%   2) WFG2,  M=3  (failure pattern)
%   3) RWMOP9, M=2 (engineering case, multi-algorithm)
%   4) RWMOP8, M=3 (engineering adverse case, multi-algorithm)
%   5) DTLZ4, M=3  (bimodal good/bad runs, V6)
%   6) Additional baselines for DTLZ2 M=2 and WFG2 M=3 (V1 expansion)
%
% Output CSVs:
%   data/processed/fronts/
%
% Usage from project root:
%   matlab -batch "run('experiments/extract_fronts_for_paper.m')"

fprintf('=== Extracting Pareto fronts for paper figures ===\n');

script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);

platemo_root = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
addpath(genpath(platemo_root));

outdir = fullfile(project_root, 'data', 'processed', 'fronts');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

data_root = fullfile(platemo_root, 'Data');
eng_root = fullfile(project_root, 'data', 'engineering_suite');

ivf_dir = local_pick_ivf_dir(data_root);
fprintf('Using IVF data folder: %s\n', ivf_dir);

%% =====================================================================
%% 1) DTLZ2, M=2 (synthetic success case)
%% =====================================================================
fprintf('\n--- DTLZ2 M=2 ---\n');

ivf_paths = local_list_files(ivf_dir, '*DTLZ2_M2_D11_30*.mat');
fprintf('  IVF files found: %d\n', numel(ivf_paths));

if isempty(ivf_paths)
    warning('No IVF files found for DTLZ2 M2 (pattern: *DTLZ2_M2_D11_30*.mat).');
else
    [med_file, med_igd] = local_find_median_run(ivf_paths);
    fprintf('  Median run: %s (IGD=%.6g)\n', med_file, med_igd);

    objs = local_extract_objectives(med_file);
    fprintf('  Population size: %d, objectives: %d\n', size(objs, 1), size(objs, 2));

    T = array2table(objs, 'VariableNames', {'f1', 'f2'});
    writetable(T, fullfile(outdir, 'DTLZ2_M2_IVFSPEA2_median.csv'));

    prob = DTLZ2('M', 2, 'D', 11);
    true_pf = prob.GetOptimum(1000);
    T_pf = array2table(true_pf, 'VariableNames', {'f1', 'f2'});
    writetable(T_pf, fullfile(outdir, 'DTLZ2_M2_truePF.csv'));
    fprintf('  True PF points: %d\n', size(true_pf, 1));
end

%% =====================================================================
%% 2) WFG2, M=3 (synthetic failure case)
%% =====================================================================
fprintf('\n--- WFG2 M=3 ---\n');

ivf_paths = local_list_files(ivf_dir, '*WFG2_M3_D12_30*.mat');
fprintf('  IVF files found: %d\n', numel(ivf_paths));

if isempty(ivf_paths)
    warning('No IVF files found for WFG2 M3 (pattern: *WFG2_M3_D12_30*.mat).');
else
    [med_file, med_igd] = local_find_median_run(ivf_paths);
    fprintf('  Median run: %s (IGD=%.6g)\n', med_file, med_igd);

    objs = local_extract_objectives(med_file);
    fprintf('  Population size: %d, objectives: %d\n', size(objs, 1), size(objs, 2));

    T = array2table(objs, 'VariableNames', {'f1', 'f2', 'f3'});
    writetable(T, fullfile(outdir, 'WFG2_M3_IVFSPEA2_median.csv'));

    prob = WFG2('M', 3, 'D', 12);
    true_pf = prob.GetOptimum(1000);
    T_pf = array2table(true_pf, 'VariableNames', {'f1', 'f2', 'f3'});
    writetable(T_pf, fullfile(outdir, 'WFG2_M3_truePF.csv'));
    fprintf('  True PF points: %d\n', size(true_pf, 1));
end

%% =====================================================================
%% 3) RWMOP9, M=2 (engineering, multi-algorithm)
%% =====================================================================
fprintf('\n--- RWMOP9 M=2 (multi-algorithm) ---\n');

algorithms = {'IVFSPEA2', 'SPEA2', 'NSGAIII', 'ARMOEA'};
for a = 1:numel(algorithms)
    algo = algorithms{a};
    adir = fullfile(eng_root, sprintf('%s_RWMOP9_M2', algo));
    apaths = local_list_files(adir, '*.mat');
    fprintf('  %s: %d files\n', algo, numel(apaths));

    if isempty(apaths)
        fprintf('    SKIPPED (no files)\n');
        continue;
    end

    [med_file, med_igd] = local_find_median_run(apaths);
    fprintf('    Median run: %s (IGD=%.6g)\n', med_file, med_igd);

    objs = local_extract_objectives(med_file);
    fprintf('    Population size: %d, objectives: %d\n', size(objs, 1), size(objs, 2));

    T = array2table(objs, 'VariableNames', {'f1', 'f2'});
    out_name = sprintf('RWMOP9_M2_%s_median.csv', algo);
    writetable(T, fullfile(outdir, out_name));
end

%% =====================================================================
%% 4) RWMOP8, M=3 (engineering, multi-algorithm)
%% =====================================================================
fprintf('\n--- RWMOP8 M=3 (multi-algorithm) ---\n');

algorithms = {'IVFSPEA2', 'SPEA2', 'NSGAIII', 'ARMOEA'};
for a = 1:numel(algorithms)
    algo = algorithms{a};
    adir = fullfile(eng_root, sprintf('%s_RWMOP8_M3', algo));
    apaths = local_list_files(adir, '*.mat');
    fprintf('  %s: %d files\n', algo, numel(apaths));

    if isempty(apaths)
        fprintf('    SKIPPED (no files)\n');
        continue;
    end

    [med_file, med_igd] = local_find_median_run(apaths);
    fprintf('    Median run: %s (IGD=%.6g)\n', med_file, med_igd);

    objs = local_extract_objectives(med_file);
    if size(objs, 2) ~= 3
        warning('Expected 3 objectives for %s RWMOP8 M3, found %d. Skipping.', algo, size(objs, 2));
        continue;
    end
    fprintf('    Population size: %d, objectives: %d\n', size(objs, 1), size(objs, 2));

    T = array2table(objs, 'VariableNames', {'f1', 'f2', 'f3'});
    out_name = sprintf('RWMOP8_M3_%s_median.csv', algo);
    writetable(T, fullfile(outdir, out_name));
end

%% =====================================================================
%% 5) DTLZ4, M=3 (bimodal good/bad runs — V6)
%% =====================================================================
fprintf('\n--- DTLZ4 M=3 (bimodal good/bad) ---\n');

ivf_dtlz4 = local_list_files(ivf_dir, '*DTLZ4_M3_D12_30*.mat');
fprintf('  IVF files found: %d\n', numel(ivf_dtlz4));

if numel(ivf_dtlz4) < 2
    warning('Need at least 2 DTLZ4 M3 runs for good/bad selection.');
else
    n4 = numel(ivf_dtlz4);
    igd4 = nan(n4, 1);
    for i = 1:n4
        S = load(ivf_dtlz4{i}, 'metric');
        igd4(i) = local_final_igd(S.metric);
    end

    q1 = quantile(igd4, 0.25);
    q3 = quantile(igd4, 0.75);
    fprintf('  Q1=%.6g  Q3=%.6g  median=%.6g\n', q1, q3, median(igd4));

    % Good run: IGD <= Q1, selecting the one closest to Q1
    good_mask = igd4 <= q1;
    if any(good_mask)
        good_candidates = find(good_mask);
        [~, rel_idx] = min(abs(igd4(good_candidates) - q1));
        good_idx = good_candidates(rel_idx);
    else
        warning('No runs satisfy IGD <= Q1; falling back to closest-to-Q1 selection.');
        [~, good_idx] = min(abs(igd4 - q1));
    end
    good_file = ivf_dtlz4{good_idx};
    good_igd = igd4(good_idx);
    [~, good_name] = fileparts(good_file);
    fprintf('  Good run: %s (IGD=%.6g)\n', good_name, good_igd);

    objs_good = local_extract_objectives(good_file);
    T = array2table(objs_good, 'VariableNames', {'f1', 'f2', 'f3'});
    writetable(T, fullfile(outdir, 'DTLZ4_M3_IVFSPEA2_good.csv'));

    % Bad run: IGD >= Q3 and IGD > 0.1, selecting the one closest to Q3
    bad_mask = (igd4 >= q3) & (igd4 > 0.1);
    if ~any(bad_mask)
        warning('No runs satisfy IGD >= Q3 and IGD > 0.1; falling back to IGD > 0.1 closest-to-Q3 selection.');
        bad_mask = igd4 > 0.1;
    end

    if ~any(bad_mask)
        warning('No runs with IGD > 0.1 for bad selection.');
    else
        igd4_bad = igd4;
        igd4_bad(~bad_mask) = Inf;
        [~, bad_idx] = min(abs(igd4_bad - q3));
        bad_file = ivf_dtlz4{bad_idx};
        bad_igd = igd4(bad_idx);
        [~, bad_name] = fileparts(bad_file);
        fprintf('  Bad run:  %s (IGD=%.6g)\n', bad_name, bad_igd);

        objs_bad = local_extract_objectives(bad_file);
        T = array2table(objs_bad, 'VariableNames', {'f1', 'f2', 'f3'});
        writetable(T, fullfile(outdir, 'DTLZ4_M3_IVFSPEA2_bad.csv'));
    end

    % True Pareto front
    prob = DTLZ4('M', 3, 'D', 12);
    true_pf = prob.GetOptimum(1000);
    T_pf = array2table(true_pf, 'VariableNames', {'f1', 'f2', 'f3'});
    writetable(T_pf, fullfile(outdir, 'DTLZ4_M3_truePF.csv'));
    fprintf('  True PF points: %d\n', size(true_pf, 1));

    % Summary for caption traceability
    fprintf('\n  === DTLZ4 M3 selection summary ===\n');
    fprintf('  Good: %s  IGD=%.6g  (Q1=%.6g)\n', good_name, good_igd, q1);
    if exist('bad_name', 'var')
        fprintf('  Bad:  %s  IGD=%.6g  (Q3=%.6g)\n', bad_name, bad_igd, q3);
    end
    n_good = sum(igd4 <= 0.1);
    n_bad  = sum(igd4 > 0.1);
    fprintf('  Runs with IGD<=0.1: %d/%d (%.0f%%)\n', n_good, n4, 100*n_good/n4);
    fprintf('  Runs with IGD>0.1:  %d/%d (%.0f%%)\n', n_bad, n4, 100*n_bad/n4);

    % Persist selection metadata for manuscript traceability
    good_run_id = local_extract_run_id(good_name);
    if exist('bad_name', 'var')
        bad_run_id = local_extract_run_id(bad_name);
        selection_type = {'good_q1'; 'bad_q3_gt_0p1'};
        run_id = [good_run_id; bad_run_id];
        run_name = {good_name; bad_name};
        igd_value = [good_igd; bad_igd];
    else
        selection_type = {'good_q1'};
        run_id = good_run_id;
        run_name = {good_name};
        igd_value = good_igd;
    end

    T_meta = table(selection_type, run_id, run_name, igd_value, ...
        repmat(q1, numel(selection_type), 1), ...
        repmat(q3, numel(selection_type), 1), ...
        repmat(n4, numel(selection_type), 1), ...
        repmat(n_good, numel(selection_type), 1), ...
        repmat(n_bad, numel(selection_type), 1), ...
        'VariableNames', {'selection_type','run_id','run_name','igd','q1','q3','n_total','n_igd_le_0p1','n_igd_gt_0p1'});
    writetable(T_meta, fullfile(outdir, 'DTLZ4_M3_selection_metadata.csv'));
end

%% =====================================================================
%% 6) Baselines for DTLZ2 M=2 and WFG2 M=3 (V1 expansion)
%% =====================================================================
fprintf('\n--- Baselines for synthetic panels ---\n');

synthetic_algorithms = {'SPEA2', 'NSGAIII', 'MOEAD'};
for a = 1:numel(synthetic_algorithms)
    algo = synthetic_algorithms{a};
    adir = fullfile(platemo_root, 'Data_original', algo);
    fprintf('  %s data folder: %s\n', algo, adir);

    % DTLZ2 M=2
    pattern_dtlz2 = '*DTLZ2_M2_D11_*.mat';
    files_dtlz2 = local_list_files(adir, pattern_dtlz2);
    fprintf('    DTLZ2 M2 files: %d\n', numel(files_dtlz2));
    if ~isempty(files_dtlz2)
        [med_file, med_igd] = local_find_median_run(files_dtlz2);
        fprintf('      Median run: %s (IGD=%.6g)\n', med_file, med_igd);
        objs = local_extract_objectives(med_file);
        if size(objs, 2) == 2
            T = array2table(objs, 'VariableNames', {'f1', 'f2'});
            out_name = sprintf('DTLZ2_M2_%s_median.csv', algo);
            writetable(T, fullfile(outdir, out_name));
        else
            warning('Expected 2 objectives for %s DTLZ2 M2, found %d. Skipping.', algo, size(objs, 2));
        end
    end

    % WFG2 M=3
    pattern_wfg2 = '*WFG2_M3_D12_*.mat';
    files_wfg2 = local_list_files(adir, pattern_wfg2);
    fprintf('    WFG2 M3 files: %d\n', numel(files_wfg2));
    if ~isempty(files_wfg2)
        [med_file, med_igd] = local_find_median_run(files_wfg2);
        fprintf('      Median run: %s (IGD=%.6g)\n', med_file, med_igd);
        objs = local_extract_objectives(med_file);
        if size(objs, 2) == 3
            T = array2table(objs, 'VariableNames', {'f1', 'f2', 'f3'});
            out_name = sprintf('WFG2_M3_%s_median.csv', algo);
            writetable(T, fullfile(outdir, out_name));
        else
            warning('Expected 3 objectives for %s WFG2 M3, found %d. Skipping.', algo, size(objs, 2));
        end
    end
end

fprintf('\n=== Done. CSVs saved to: %s ===\n', outdir);
fprintf('Next step: python src/python/analysis/generate_paper_figures.py\n');


%% ===== Local helpers =====
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

function run_id = local_extract_run_id(run_name)
    tokens = regexp(run_name, '_(\d+)$', 'tokens', 'once');
    if isempty(tokens)
        run_id = NaN;
    else
        run_id = str2double(tokens{1});
    end
end
