%% compute_hv_modern_baselines.m
% Compute HV for modern baseline MAT files (AGEMOEAII, ARMOEA) in
% data/modern_baselines/ and save metric.HV back into each file.
%
% This is needed because those runs were executed with only IGD + runtime
% recorded. The approach mirrors compute_missing_hv.m: load the final
% population from result{end}, build SOLUTION objects, call PlatEMO's HV
% metric with the true Pareto front.
%
% Usage:
%   matlab -nodisplay -r "run('scripts/compute_hv_modern_baselines.m')"
%
% Outputs:
%   - Each MAT file gets metric.HV written in-place
%   - results/hv_modern_baselines_log.csv  — log of all computed values

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
MODERN_DIR   = fullfile(PROJECT_ROOT, 'data', 'modern_baselines');
OUT_DIR      = fullfile(PROJECT_ROOT, 'results');

addpath(genpath(PLATEMO_DIR));

if ~isfolder(OUT_DIR), mkdir(OUT_DIR); end

%% Scan all MAT files
fprintf('=== Scanning modern baseline MAT files ===\n');
all_files = dir(fullfile(MODERN_DIR, '**', '*.mat'));
fprintf('Found %d MAT files\n', numel(all_files));

PROB_RE = '^(AGEMOEAII|ARMOEA)_(ZDT\d|DTLZ\d|WFG\d|MaF\d+|RWMOP\d+)_M(\d+)_D(\d+)_(\d+)\.mat$';

%% Classify files
fpaths    = {};
algos     = {};
problems  = {};
M_vals    = [];
D_vals    = [];
runs      = [];
has_hv    = logical([]);
existing_hv = [];

n_parsed  = 0;
n_skipped = 0;

for i = 1:numel(all_files)
    fname = all_files(i).name;
    fpath = fullfile(all_files(i).folder, fname);

    tok = regexp(fname, PROB_RE, 'tokens', 'once');
    if isempty(tok)
        n_skipped = n_skipped + 1;
        continue;
    end

    n_parsed = n_parsed + 1;
    fpaths{n_parsed,1}    = fpath;
    algos{n_parsed,1}     = tok{1};
    problems{n_parsed,1}  = tok{2};
    M_vals(n_parsed,1)    = str2double(tok{3});
    D_vals(n_parsed,1)    = str2double(tok{4});
    runs(n_parsed,1)      = str2double(tok{5});

    % Check existing HV
    hHV = false;
    hvv = NaN;
    try
        d = load(fpath, 'metric');
        if isfield(d, 'metric') && isfield(d.metric, 'HV') && ...
                isnumeric(d.metric.HV) && ~isempty(d.metric.HV)
            hHV = true;
            hvv = d.metric.HV(end);
        end
    catch
    end
    has_hv(n_parsed,1) = hHV;
    existing_hv(n_parsed,1) = hvv;

    if mod(n_parsed, 2000) == 0
        fprintf('  Scanned %d files ...\n', n_parsed);
    end
end

n_total = n_parsed;
n_already = sum(has_hv);
n_missing = n_total - n_already;

fprintf('\n--- Scan summary ---\n');
fprintf('Parsed     : %d\n', n_total);
fprintf('Skipped    : %d\n', n_skipped);
fprintf('Already HV : %d\n', n_already);
fprintf('Missing HV : %d\n', n_missing);

% Per-algorithm breakdown
unique_algos = unique(algos);
for ai = 1:numel(unique_algos)
    a = unique_algos{ai};
    mask = strcmp(algos, a);
    for m_val = [2, 3]
        mm = mask & (M_vals == m_val);
        if any(mm)
            fprintf('  %-12s M%d : %5d total, %5d HV, %5d missing\n', ...
                a, m_val, sum(mm), sum(has_hv(mm)), sum(mm) - sum(has_hv(mm)));
        end
    end
end

%% Compute HV for missing entries
fprintf('\n=== Computing HV for %d entries ===\n', n_missing);

optimum_cache = containers.Map('KeyType', 'char', 'ValueType', 'any');
newly_computed = 0;
compute_failed = 0;
failed_reasons = {};

missing_idx = find(~has_hv);

for ii = 1:numel(missing_idx)
    idx = missing_idx(ii);

    prob_name = problems{idx};
    Mv = M_vals(idx);
    Dv = D_vals(idx);
    fpath = fpaths{idx};

    cache_key = sprintf('%s_M%d_D%d', prob_name, Mv, Dv);

    % Get or compute the true Pareto front
    if ~isKey(optimum_cache, cache_key)
        try
            prob_handle = str2func(prob_name);
            prob_obj = prob_handle('M', Mv, 'D', Dv, 'maxFE', 1e4);
            opt = prob_obj.GetOptimum(10000);
            optimum_cache(cache_key) = opt;
        catch me
            fprintf('  [WARN] Cannot instantiate %s: %s\n', cache_key, me.message);
            optimum_cache(cache_key) = [];
        end
    end

    opt = optimum_cache(cache_key);
    if isempty(opt)
        compute_failed = compute_failed + 1;
        failed_reasons{end+1} = sprintf('no_optimum:%s', cache_key); %#ok<SAGROW>
        continue;
    end

    try
        d = load(fpath, 'result');
        if ~isfield(d, 'result') || isempty(d.result)
            compute_failed = compute_failed + 1;
            failed_reasons{end+1} = sprintf('no_result:%s', fpath); %#ok<SAGROW>
            continue;
        end

        objs = extract_final_objs(d.result);
        if isempty(objs) || size(objs, 2) ~= Mv
            compute_failed = compute_failed + 1;
            failed_reasons{end+1} = sprintf('bad_objs:%s (cols=%d, M=%d)', ...
                fpath, size(objs,2), Mv); %#ok<SAGROW>
            continue;
        end

        dummy_dec = zeros(size(objs,1), 1);
        cons = zeros(size(objs,1), 1);
        pop = SOLUTION(dummy_dec, objs, cons);
        hv_val = HV(pop, opt);

        % Save HV back into the MAT file
        s = load(fpath, 'metric');
        metric = s.metric;
        metric.HV = hv_val;
        save(fpath, 'metric', '-append');

        has_hv(idx) = true;
        existing_hv(idx) = hv_val;
        newly_computed = newly_computed + 1;

    catch me
        compute_failed = compute_failed + 1;
        failed_reasons{end+1} = sprintf('error:%s:%s', fpath, me.message); %#ok<SAGROW>
    end

    if mod(ii, 500) == 0
        fprintf('  %d / %d processed  (computed=%d, failed=%d)\n', ...
            ii, numel(missing_idx), newly_computed, compute_failed);
    end
end

fprintf('\n--- Computation summary ---\n');
fprintf('Newly computed : %d\n', newly_computed);
fprintf('Failed         : %d\n', compute_failed);
fprintf('Total with HV  : %d / %d\n', sum(has_hv), n_total);

if compute_failed > 0
    fprintf('\nFirst %d failure reasons:\n', min(10, numel(failed_reasons)));
    for i = 1:min(10, numel(failed_reasons))
        fprintf('  %s\n', failed_reasons{i});
    end
end

%% Write log CSV
log_file = fullfile(OUT_DIR, 'hv_modern_baselines_log.csv');
fid = fopen(log_file, 'w');
fprintf(fid, 'Algorithm,Problem,M,D,Run,HasHV,HV,Path\n');
for i = 1:n_total
    fprintf(fid, '%s,%s,%d,%d,%d,%d,%.15g,%s\n', ...
        algos{i}, problems{i}, M_vals(i), D_vals(i), runs(i), ...
        has_hv(i), existing_hv(i), fpaths{i});
end
fclose(fid);
fprintf('Wrote log: %s (%d rows)\n', log_file, n_total);

fprintf('\n=== Done ===\n');

%% ======================================================================
%%  Helper: extract final-generation objectives from result cell array
%% ======================================================================
function objs = extract_final_objs(result)
    objs = [];
    if isempty(result), return; end

    % result can be a cell array or struct array; iterate from end (last gen)
    for k = numel(result):-1:1
        if iscell(result)
            snapshot = result{k};
        else
            snapshot = result(k);
        end

        if iscell(snapshot)
            for j = 1:numel(snapshot)
                elem = snapshot{j};
                if isobject(elem)
                    try objs = elem.objs; return; catch, end
                elseif isnumeric(elem) && size(elem, 2) > 1 && size(elem, 1) > 1
                    objs = elem; return;
                end
            end
        elseif isobject(snapshot)
            try objs = snapshot.objs; return; catch, end
        elseif isnumeric(snapshot) && size(snapshot, 2) > 1
            objs = snapshot; return;
        end
    end
end
