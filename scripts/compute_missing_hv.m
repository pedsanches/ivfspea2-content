%% compute_missing_hv.m
% Inventory all experiment .mat files and compute HV where missing.
%
% Phase 1: Scan data roots, parse filenames, check metric.HV existence
% Phase 2: Compute HV for files where it is missing
% Phase 3: Write comprehensive CSV with all entries
%
% Outputs:
%   results/hv_inventory.csv          — full inventory (every .mat found)
%   results/hv_backfill_computed.csv  — only entries where HV was newly computed
%
% Usage:
%   matlab -nodisplay -r "run('scripts/compute_missing_hv.m')"

clear; clc;

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
OUT_DIR      = fullfile(PROJECT_ROOT, 'results');

addpath(genpath(PLATEMO_DIR));

if ~isfolder(OUT_DIR), mkdir(OUT_DIR); end

%% Data roots to scan
data_roots = {
    fullfile(PLATEMO_DIR, 'Data')
    fullfile(PLATEMO_DIR, 'Data_original')
    fullfile(PROJECT_ROOT, 'data', 'ablation_v2', 'phase1')
    fullfile(PROJECT_ROOT, 'data', 'ablation_v2', 'phase2')
};

PROB_RE = '(ZDT\d|DTLZ\d|WFG\d|MaF\d+|RWMOP\d+)_M(\d+)_D(\d+)_(\d+)\.mat$';

%% ======================================================================
%%  PHASE 1 — Inventory
%% ======================================================================
fprintf('=== Phase 1: Scanning .mat files ===\n');

paths    = {};
sources  = {};
configs  = {};
problems = {};
M_vals   = [];
D_vals   = [];
runs     = [];
has_hv   = logical([]);
hv_vals  = [];
has_igd  = logical([]);
igd_vals = [];

for ri = 1:numel(data_roots)
    root = data_roots{ri};
    if ~isfolder(root)
        fprintf('  [SKIP] Not found: %s\n', root);
        continue;
    end

    mat_list = dir(fullfile(root, '**', '*.mat'));
    fprintf('  Scanning %d files in %s ...\n', numel(mat_list), root);

    for fi = 1:numel(mat_list)
        fpath = fullfile(mat_list(fi).folder, mat_list(fi).name);
        fname = mat_list(fi).name;

        tok = regexp(fname, PROB_RE, 'tokens', 'once');
        if isempty(tok)
            continue;
        end

        prob_name = tok{1};
        M = str2double(tok{2});
        D = str2double(tok{3});
        run_id = str2double(tok{4});

        src = classify_source(mat_list(fi).folder, root);
        cfg = infer_config(mat_list(fi).folder, fname, prob_name, M);

        hHV  = false;
        hIGD = false;
        hvv  = NaN;
        igdv = NaN;

        try
            d = load(fpath, 'metric');
            if isfield(d, 'metric')
                met = d.metric;
                if isfield(met, 'HV') && isnumeric(met.HV) && ~isempty(met.HV)
                    hHV = true;
                    hvv = met.HV(end);
                end
                if isfield(met, 'IGD') && isnumeric(met.IGD) && ~isempty(met.IGD)
                    hIGD = true;
                    igdv = met.IGD(end);
                end
            end
        catch
        end

        n = numel(paths) + 1;
        paths{n,1}    = fpath;
        sources{n,1}  = src;
        configs{n,1}  = cfg;
        problems{n,1} = prob_name;
        M_vals(n,1)   = M;
        D_vals(n,1)   = D;
        runs(n,1)     = run_id;
        has_hv(n,1)   = hHV;
        hv_vals(n,1)  = hvv;
        has_igd(n,1)  = hIGD;
        igd_vals(n,1) = igdv;

        if mod(n, 2000) == 0
            fprintf('    %d files processed ...\n', n);
        end
    end
end

n_total      = numel(paths);
n_with_hv    = sum(has_hv);
n_missing_hv = n_total - n_with_hv;

fprintf('\n--- Phase 1 summary ---\n');
fprintf('Total parseable .mat : %d\n', n_total);
fprintf('  Already have HV    : %d (%.1f%%)\n', n_with_hv, 100*n_with_hv/max(n_total,1));
fprintf('  Missing HV         : %d (%.1f%%)\n', n_missing_hv, 100*n_missing_hv/max(n_total,1));

src_list = unique(sources);
for si = 1:numel(src_list)
    mask = strcmp(sources, src_list{si});
    n_src = sum(mask);
    n_hv  = sum(has_hv(mask));
    fprintf('  %-30s : %5d total, %5d HV, %5d missing\n', src_list{si}, n_src, n_hv, n_src - n_hv);
end

%% ======================================================================
%%  PHASE 2 — Compute HV where missing
%% ======================================================================
fprintf('\n=== Phase 2: Computing HV for %d entries ===\n', n_missing_hv);

optimum_cache = containers.Map('KeyType', 'char', 'ValueType', 'any');
newly_computed = 0;
compute_failed = 0;

missing_idx = find(~has_hv);

for ii = 1:numel(missing_idx)
    idx = missing_idx(ii);

    prob_name = problems{idx};
    M = M_vals(idx);
    D = D_vals(idx);
    fpath = paths{idx};

    cache_key = sprintf('%s_M%d_D%d', prob_name, M, D);

    if ~isKey(optimum_cache, cache_key)
        try
            prob_handle = str2func(prob_name);
            prob_obj = prob_handle('M', M, 'D', D, 'maxFE', 1e4);
            opt = prob_obj.GetOptimum(10000);
            optimum_cache(cache_key) = opt;
        catch
            optimum_cache(cache_key) = [];
        end
    end

    opt = optimum_cache(cache_key);
    if isempty(opt)
        compute_failed = compute_failed + 1;
        continue;
    end

    try
        d = load(fpath, 'result');
        if ~isfield(d, 'result') || isempty(d.result)
            compute_failed = compute_failed + 1;
            continue;
        end

        objs = extract_final_objs(d.result);
        if isempty(objs) || size(objs, 2) ~= M
            compute_failed = compute_failed + 1;
            continue;
        end

        dummy_dec = zeros(size(objs,1), 1);
        cons = zeros(size(objs,1), 1);
        pop = SOLUTION(dummy_dec, objs, cons);
        hv_val = HV(pop, opt);

        has_hv(idx)  = true;
        hv_vals(idx) = hv_val;
        newly_computed = newly_computed + 1;
    catch
        compute_failed = compute_failed + 1;
    end

    if mod(ii, 1000) == 0
        fprintf('  %d / %d processed  (computed=%d, failed=%d)\n', ...
            ii, numel(missing_idx), newly_computed, compute_failed);
    end
end

fprintf('\n--- Phase 2 summary ---\n');
fprintf('Newly computed : %d\n', newly_computed);
fprintf('Failed         : %d\n', compute_failed);
fprintf('Total with HV  : %d / %d\n', sum(has_hv), n_total);

%% ======================================================================
%%  PHASE 3 — Write output CSVs
%% ======================================================================
fprintf('\n=== Phase 3: Writing output CSVs ===\n');

inv_file = fullfile(OUT_DIR, 'hv_inventory.csv');
fid = fopen(inv_file, 'w');
fprintf(fid, 'Source,Config,Problem,M,D,Run,HasHV,HV,HasIGD,IGD,Path\n');
for i = 1:n_total
    fprintf(fid, '%s,%s,%s,%d,%d,%d,%d,%.15g,%d,%.15g,%s\n', ...
        sources{i}, configs{i}, problems{i}, M_vals(i), D_vals(i), runs(i), ...
        has_hv(i), hv_vals(i), has_igd(i), igd_vals(i), paths{i});
end
fclose(fid);
fprintf('  Wrote %s (%d rows)\n', inv_file, n_total);

bf_file = fullfile(OUT_DIR, 'hv_backfill_computed.csv');
fid = fopen(bf_file, 'w');
fprintf(fid, 'Source,Config,Problem,M,D,Run,HV,Path\n');
for i = 1:numel(missing_idx)
    idx = missing_idx(i);
    if has_hv(idx) && ~isnan(hv_vals(idx))
        fprintf(fid, '%s,%s,%s,%d,%d,%d,%.15g,%s\n', ...
            sources{idx}, configs{idx}, problems{idx}, M_vals(idx), D_vals(idx), ...
            runs(idx), hv_vals(idx), paths{idx});
    end
end
fclose(fid);
fprintf('  Wrote %s (%d rows)\n', bf_file, newly_computed);

fprintf('\n=== Done ===\n');

%% ======================================================================
%%  Helper functions
%% ======================================================================
function src = classify_source(folder, root)
    if contains(folder, 'phase1')
        src = 'ablation_v2_phase1';
    elseif contains(folder, 'phase2')
        src = 'ablation_v2_phase2';
    else
        parent = fileparts(folder);
        dirname = folder(length(parent)+2:end);
        if contains(dirname, '_R0.')
            src = 'sensitivity';
        elseif any(strcmp(dirname, {'IVFSPEA2ABL1C','IVFSPEA2ABL4C','IVFSPEA2ABLDOM'}))
            src = 'ablation_v1';
        elseif strcmp(dirname, 'IVFSPEA2_P2')
            src = 'ablation_v2_phase2_live';
        elseif any(strcmp(dirname, {'AGEMOEAII','ARMOEA','MFOSPEA2','MOEAD','NSGAII','NSGAIII','SPEA2','SPEA2SDE'}))
            src = 'baseline';
        else
            src = 'main';
        end
    end
end

function cfg = infer_config(folder, fname, prob_name, M)
    [~, dirname] = fileparts(folder);
    suffix = sprintf('_%s_M%d', prob_name, M);
    if endsWith(dirname, suffix)
        cfg = dirname(1:end-length(suffix));
    else
        prefix_end = strfind(fname, sprintf('_%s_M', prob_name));
        if ~isempty(prefix_end)
            cfg = fname(1:prefix_end(1)-1);
        else
            cfg = dirname;
        end
    end
end

function objs = extract_final_objs(result)
    objs = [];
    if isempty(result), return; end

    for k = numel(result):-1:1
        snapshot = result{k};

        if iscell(snapshot)
            % PlatEMO format: {runtime, Population} or {objs_matrix, ...}
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
