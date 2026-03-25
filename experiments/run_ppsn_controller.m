%% run_ppsn_controller.m
%  PPSN 2026 — minimal controller experiments (parallel version).
%  Runs IVFSPEA2V2CTRLTRACE on a configurable benchmark manifest using the
%  same seed schedule as the paired dynamics batch so results stay directly
%  comparable to existing IVF/SPEA2 traces.
%
%  Environment controls (all optional):
%    PPSN_RUNS        number of independent runs per case (default 30)
%    PPSN_MAXFE       function evaluation budget     (default 100000)
%    PPSN_POP         population size                (default 100)
%    PPSN_MANIFEST    path to benchmark manifest CSV (default config/ppsn_dynamics_cases_full.csv)
%    PPSN_CASE_IDS    comma-separated case_id filter
%    PPSN_WORKERS     parallel workers               (default 6)
%    PPSN_JOB_STORAGE custom JobStorageLocation for the parallel profile
%    PPSN_RUN_TAG     suffix used to disambiguate logs for concurrent runs
%    PPSN_SEED_RUNS   runs/case used by the fallback seed schedule (default 30)
%    CTRL_WARMUP_FRAC controller warmup fraction     (default 0.20)
%    CTRL_TURNOVER_THRESHOLD controller threshold    (default 0.232437)
%    CTRL_CAPTURE_POP 0|1 store pre/post-IVF pops    (default 0)
%
%  Output:
%    data/raw/ppsn_dynamics/controller/<case_id>/ — controller trace .mat files

script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);

platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
trace_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
ctrl_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2-CTRL-TRACE');

addpath(genpath(platemo_dir));
addpath(trace_dir, '-begin');
addpath(ctrl_dir, '-begin');

%% ---- Configuration ----
n_runs = local_env_int('PPSN_RUNS', 30);
seed_runs = local_env_int('PPSN_SEED_RUNS', 30);
maxFE  = local_env_int('PPSN_MAXFE', 100000);
N_pop  = local_env_int('PPSN_POP', 100);
n_workers = local_env_int('PPSN_WORKERS', 6);
job_storage = local_env_string('PPSN_JOB_STORAGE', '');
run_tag = local_env_string('PPSN_RUN_TAG', '');
selected_ids = local_env_tokens('PPSN_CASE_IDS');
warmup_frac = local_env_float('CTRL_WARMUP_FRAC', 0.20);
turnover_threshold = local_env_float('CTRL_TURNOVER_THRESHOLD', 0.232437);
capture_population = local_env_bool('CTRL_CAPTURE_POP', false);
seed_base = 70000;

manifest_path = local_resolve_manifest_path(project_root, ...
    getenv('PPSN_MANIFEST'), ...
    fullfile(project_root, 'config', 'ppsn_dynamics_cases_full.csv'));
if ~isfile(manifest_path)
    error('Manifest file not found: %s', manifest_path);
end
cases = readtable(manifest_path, 'TextType', 'string');
local_require_columns(cases, {'case_id', 'problem', 'm', 'd'});
cases.manifest_idx = transpose(1:height(cases));

if ~isempty(selected_ids)
    keep = false(height(cases), 1);
    for i = 1:height(cases)
        keep(i) = any(strcmpi(char(cases.case_id(i)), selected_ids));
    end
    cases = cases(keep, :);
end

ctrl_root = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'controller');
ivf_root = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'ivf');
spea2_root = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'spea2');
logs_root = fullfile(project_root, 'logs');
for d = {ctrl_root, logs_root}
    if ~isfolder(d{1}), mkdir(d{1}); end
end

log_stamp = datestr(now, 'yyyymmdd_HHMMSS');
if isempty(run_tag)
    log_name = sprintf('ppsn_controller_%s.log', log_stamp);
else
    safe_tag = regexprep(run_tag, '[^A-Za-z0-9_.-]', '_');
    log_name = sprintf('ppsn_controller_%s_%s.log', safe_tag, log_stamp);
end
log_file = fullfile(logs_root, log_name);
diary(log_file);

fprintf('=== PPSN 2026 Controller Runner (PARALLEL) ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Manifest: %s\n', manifest_path);
fprintf('Cases: %d | Runs/case: %d | maxFE: %d | N: %d | Workers: %d\n', ...
    height(cases), n_runs, maxFE, N_pop, n_workers);
fprintf('Seed base: %d | seed_runs: %d | warmup_frac: %.4f | turnover_threshold: %.6f | capture_population: %d\n', ...
    seed_base, seed_runs, warmup_frac, turnover_threshold, capture_population);
if ~isempty(job_storage)
    fprintf('Job storage: %s\n', job_storage);
end
if ~isempty(run_tag)
    fprintf('Run tag: %s\n', run_tag);
end
fprintf('Log: %s\n\n', log_file);

%% ---- Start parallel pool ----
pool = gcp('nocreate');
if isempty(pool) || pool.NumWorkers ~= n_workers
    delete(gcp('nocreate'));
    cluster = parcluster('Processes');
    if ~isempty(job_storage)
        if ~isfolder(job_storage)
            mkdir(job_storage);
        end
        cluster.JobStorageLocation = job_storage;
    end
    pool = parpool(cluster, n_workers);
end
fprintf('Parallel pool: %d workers\n\n', pool.NumWorkers);

t_start = tic;

%% ---- Build job list ----
jobs = {};
for ci = 1:height(cases)
    case_id = local_table_string(cases, 'case_id', ci);
    problem_name = local_table_string(cases, 'problem', ci);
    M_obj = local_table_int(cases, 'm', ci);
    D_vars = local_table_int(cases, 'd', ci);
    role = local_table_string(cases, 'role', ci, 'full_suite');
    manifest_idx = local_table_int(cases, 'manifest_idx', ci);

    ctrl_case_dir = fullfile(ctrl_root, case_id);
    ivf_case_dir = fullfile(ivf_root, case_id);
    spea2_case_dir = fullfile(spea2_root, case_id);
    if ~isfolder(ctrl_case_dir), mkdir(ctrl_case_dir); end
    [planned_run_ids, seed_source] = local_planned_run_ids( ...
        ivf_case_dir, spea2_case_dir, seed_base, manifest_idx, seed_runs, n_runs);

    for ri = 1:numel(planned_run_ids)
        run_id = planned_run_ids(ri);
        ctrl_file = fullfile(ctrl_case_dir, sprintf('CTRL_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));

        if isfile(ctrl_file)
            continue;
        end

        job = struct( ...
            'case_id', case_id, ...
            'problem_name', problem_name, ...
            'M_obj', M_obj, ...
            'D_vars', D_vars, ...
            'role', role, ...
            'run_id', run_id, ...
            'seed', run_id, ...
            'seed_source', seed_source, ...
            'N_pop', N_pop, ...
            'maxFE', maxFE, ...
            'ctrl_file', ctrl_file, ...
            'manifest_idx', manifest_idx, ...
            'platemo_dir', platemo_dir, ...
            'trace_dir', trace_dir, ...
            'ctrl_dir', ctrl_dir, ...
            'capture_population', capture_population, ...
            'warmup_frac', warmup_frac, ...
            'turnover_threshold', turnover_threshold);
        jobs{end+1} = job; %#ok<SAGROW>
    end
end

n_jobs = numel(jobs);
fprintf('Total jobs: %d (skipped %d already completed)\n\n', n_jobs, ...
    height(cases) * n_runs - n_jobs);

%% ---- Execute jobs in parallel ----
fail_count = 0;
parfor ji = 1:n_jobs
    j = jobs{ji};
    try
        local_run_controller(j);
    catch ME
        fprintf('[FAIL] %s run %d: %s\n', j.case_id, j.run_id, ME.message);
        fail_count = fail_count + 1; %#ok<PFBFN>
    end
end

elapsed_h = toc(t_start) / 3600;
fprintf('\n=== Complete ===\n');
fprintf('Jobs: %d | Failures: %d | Elapsed: %.2f hours\n', n_jobs, fail_count, elapsed_h);
diary off;


function local_run_controller(j)
    addpath(genpath(j.platemo_dir));
    addpath(j.trace_dir, '-begin');
    addpath(j.ctrl_dir, '-begin');

    problem_handle = str2func(j.problem_name);

    if ~isfile(j.ctrl_file)
        rng(j.seed, 'twister');
        Problem = feval(problem_handle, 'M', j.M_obj, 'D', j.D_vars, 'N', j.N_pop, 'maxFE', j.maxFE);
        Algo = IVFSPEA2V2CTRLTRACE('parameter', ...
            {0.12, 0.225, 0.3, 0.1, 2, 1, 0, double(j.capture_population), j.warmup_frac, j.turnover_threshold}, ...
            'save', 1, 'run', j.run_id, 'outputFcn', @(~,~) []);
        Algo.Solve(Problem);

        trace_generations = Algo.TraceGenerations; %#ok<NASGU>
        trace_cycles = Algo.TraceCycles; %#ok<NASGU>
        trace_params = Algo.TraceParameters; %#ok<NASGU>
        meta = struct('case_id', j.case_id, 'problem', j.problem_name, ...
            'm', j.M_obj, 'd', j.D_vars, 'run_id', j.run_id, 'seed', j.seed, ...
            'manifest_idx', j.manifest_idx, ...
            'seed_source', j.seed_source, ...
            'algorithm', 'IVFSPEA2V2CTRLTRACE', 'role', j.role, ...
            'maxFE', j.maxFE, 'N', j.N_pop, ...
            'controller_warmup_frac', j.warmup_frac, ...
            'controller_turnover_threshold', j.turnover_threshold); %#ok<NASGU>
        save(j.ctrl_file, 'trace_generations', 'trace_cycles', 'trace_params', 'meta');
    end

    fprintf('  [OK] %s run %d\n', j.case_id, j.run_id);
end


function value = local_env_int(name, default_value)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = default_value;
        return;
    end
    value = str2double(raw);
    if isnan(value) || value ~= round(value) || value < 1
        error('%s must be a positive integer. Got: %s', name, raw);
    end
end

function value = local_env_float(name, default_value)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = default_value;
        return;
    end
    value = str2double(raw);
    if isnan(value) || ~isfinite(value)
        error('%s must be a finite number. Got: %s', name, raw);
    end
end

function value = local_env_bool(name, default_value)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = logical(default_value);
        return;
    end
    switch lower(raw)
        case {'1', 'true', 'yes', 'on'}
            value = true;
        case {'0', 'false', 'no', 'off'}
            value = false;
        otherwise
            error('%s must be 0/1 or true/false. Got: %s', name, raw);
    end
end

function tokens = local_env_tokens(name)
    raw = strtrim(getenv(name));
    if isempty(raw)
        tokens = {};
        return;
    end
    pieces = split(string(raw), ',');
    pieces = strtrim(pieces);
    pieces = pieces(pieces ~= "");
    tokens = cellstr(pieces);
end

function value = local_env_string(name, default_value)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = default_value;
        return;
    end
    value = raw;
end

function manifest_path = local_resolve_manifest_path(project_root, raw_path, default_path)
    if nargin < 2 || isempty(strtrim(raw_path))
        manifest_path = default_path;
        return;
    end

    candidate = strtrim(raw_path);
    if isfile(candidate)
        manifest_path = candidate;
        return;
    end

    if isfile(fullfile(project_root, candidate))
        manifest_path = fullfile(project_root, candidate);
        return;
    end

    manifest_path = candidate;
end

function local_require_columns(tbl, required_cols)
    names = string(tbl.Properties.VariableNames);
    for i = 1:numel(required_cols)
        if ~any(strcmpi(names, required_cols{i}))
            error('Manifest is missing required column: %s', required_cols{i});
        end
    end
end

function value = local_table_string(tbl, colname, row_idx, default_value)
    if nargin < 4
        default_value = '';
    end

    names = string(tbl.Properties.VariableNames);
    idx = find(strcmpi(names, colname), 1);
    if isempty(idx)
        value = default_value;
        return;
    end

    raw = tbl.(tbl.Properties.VariableNames{idx})(row_idx);
    value = char(strtrim(string(raw)));
    if isempty(value)
        value = default_value;
    end
end

function value = local_table_int(tbl, colname, row_idx)
    names = string(tbl.Properties.VariableNames);
    idx = find(strcmpi(names, colname), 1);
    if isempty(idx)
        error('Manifest is missing required column: %s', colname);
    end

    raw = tbl.(tbl.Properties.VariableNames{idx})(row_idx);
    value = str2double(string(raw));
    if isnan(value) || value ~= round(value) || value < 1
        error('Manifest column %s must contain positive integers.', colname);
    end
    value = round(value);
end

function [run_ids, seed_source] = local_planned_run_ids(ivf_case_dir, spea2_case_dir, ...
        seed_base, manifest_idx, seed_runs, n_runs)
    paired_ids = local_existing_paired_run_ids(ivf_case_dir, spea2_case_dir);
    paired_ids = local_select_recent_run_ids(paired_ids, n_runs);

    if numel(paired_ids) >= n_runs
        run_ids = paired_ids;
        seed_source = 'baseline_paired';
        return;
    end

    if n_runs > seed_runs
        error('PPSN_RUNS=%d exceeds PPSN_SEED_RUNS=%d; increase PPSN_SEED_RUNS to preserve unique fallback seeds.', ...
            n_runs, seed_runs);
    end

    run_ids = paired_ids;
    fallback_ids = seed_base + (manifest_idx - 1) * seed_runs + (1:seed_runs);
    fallback_ids = fallback_ids(~ismember(fallback_ids, run_ids));
    needed = n_runs - numel(run_ids);
    if needed > numel(fallback_ids)
        error('Unable to allocate %d fallback seeds for manifest_idx=%d.', needed, manifest_idx);
    end
    run_ids = [run_ids, fallback_ids(1:needed)];
    run_ids = sort(run_ids);

    if isempty(paired_ids)
        seed_source = 'schedule_fallback';
    else
        seed_source = 'baseline_paired_plus_fallback';
    end
end

function run_ids = local_existing_paired_run_ids(ivf_case_dir, spea2_case_dir)
    ivf_ids = local_existing_run_ids(ivf_case_dir, 'IVF_*.mat');
    spea2_ids = local_existing_run_ids(spea2_case_dir, 'SPEA2_*.mat');
    run_ids = intersect(ivf_ids, spea2_ids);
end

function run_ids = local_existing_run_ids(case_dir, pattern)
    run_ids = [];
    if ~isfolder(case_dir)
        return;
    end

    files = dir(fullfile(case_dir, pattern));
    for i = 1:numel(files)
        match = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
        if isempty(match)
            continue;
        end
        run_ids(end+1) = str2double(match{1}); %#ok<AGROW>
    end
    run_ids = unique(run_ids);
end

function run_ids = local_select_recent_run_ids(run_ids, n_runs)
    run_ids = sort(unique(run_ids));
    if numel(run_ids) > n_runs
        run_ids = run_ids(end - n_runs + 1:end);
    end
end
