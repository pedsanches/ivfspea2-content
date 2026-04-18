%% run_ppsn_dynamics.m
%  PPSN 2026 — Population Dynamics experiments (parallel version).
%  Runs IVF-SPEA2 (TRACE) and SPEA2 (TRACE) with identical seeds on a
%  configurable benchmark manifest.  By default it uses the 18-case PPSN
%  subset; set PPSN_MANIFEST to point at an alternative CSV to scale up to
%  the full 52-instance batch.  Per-generation snapshots are saved for
%  every run.
%
%  Environment controls (all optional):
%    PPSN_RUNS        number of independent runs per case (default 30)
%    PPSN_MAXFE       function evaluation budget     (default 100000)
%    PPSN_POP         population size                (default 100)
%    PPSN_MANIFEST    path to benchmark manifest CSV  (default config/ppsn_dynamics_cases.csv)
%    PPSN_CASE_IDS    comma-separated case_id filter
%    PPSN_WORKERS     parallel workers               (default 6)
%    PPSN_JOB_STORAGE custom JobStorageLocation for the parallel profile
%    PPSN_RUN_TAG     suffix used to disambiguate logs for concurrent runs
%
%  Output:
%    data/raw/ppsn_dynamics/ivf/<case_id>/   — IVF-SPEA2 trace .mat files
%    data/raw/ppsn_dynamics/spea2/<case_id>/ — SPEA2 baseline .mat files

script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);

platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
ivf_trace_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
spea2_trace_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'SPEA2-TRACE');

addpath(genpath(platemo_dir));
addpath(ivf_trace_dir, '-begin');
addpath(spea2_trace_dir, '-begin');

%% ---- Configuration ----
n_runs = local_env_int('PPSN_RUNS', 30);
maxFE  = local_env_int('PPSN_MAXFE', 100000);
N_pop  = local_env_int('PPSN_POP', 100);
n_workers = local_env_int('PPSN_WORKERS', 6);
job_storage = local_env_string('PPSN_JOB_STORAGE', '');
run_tag = local_env_string('PPSN_RUN_TAG', '');
selected_ids = local_env_tokens('PPSN_CASE_IDS');
seed_base = 70000;  % distinct from all prior run IDs

manifest_path = local_resolve_manifest_path(project_root, ...
    getenv('PPSN_MANIFEST'), ...
    fullfile(project_root, 'config', 'ppsn_dynamics_cases.csv'));
if ~isfile(manifest_path)
    error('Manifest file not found: %s', manifest_path);
end
cases = readtable(manifest_path, 'TextType', 'string');
local_require_columns(cases, {'case_id', 'problem', 'm', 'd'});

if ~isempty(selected_ids)
    keep = false(height(cases), 1);
    for i = 1:height(cases)
        keep(i) = any(strcmpi(char(cases.case_id(i)), selected_ids));
    end
    cases = cases(keep, :);
end

ivf_root   = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'ivf');
spea2_root = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'spea2');
ref_root   = fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'reference_pf');
logs_root  = fullfile(project_root, 'logs');

for d = {ivf_root, spea2_root, ref_root, logs_root}
    if ~isfolder(d{1}), mkdir(d{1}); end
end

log_stamp = datestr(now, 'yyyymmdd_HHMMSS');
if isempty(run_tag)
    log_name = sprintf('ppsn_dynamics_%s.log', log_stamp);
else
    safe_tag = regexprep(run_tag, '[^A-Za-z0-9_.-]', '_');
    log_name = sprintf('ppsn_dynamics_%s_%s.log', safe_tag, log_stamp);
end
log_file = fullfile(logs_root, log_name);
diary(log_file);

fprintf('=== PPSN 2026 Population Dynamics Runner (PARALLEL) ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Manifest: %s\n', manifest_path);
fprintf('Cases: %d | Runs/case: %d | maxFE: %d | N: %d | Workers: %d\n', ...
    height(cases), n_runs, maxFE, N_pop, n_workers);
fprintf('Seed base: %d\n', seed_base);
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
% Each job is a struct with all info needed to run one (IVF + SPEA2) pair.
jobs = {};
for ci = 1:height(cases)
    case_id = local_table_string(cases, 'case_id', ci);
    problem_name = local_table_string(cases, 'problem', ci);
    M_obj = local_table_int(cases, 'm', ci);
    D_vars = local_table_int(cases, 'd', ci);
    role = local_table_string(cases, 'role', ci, 'full_suite');

    % Save reference Pareto front (serial, fast)
    problem_handle = str2func(problem_name);
    local_write_reference_pf(problem_handle, problem_name, M_obj, D_vars, ref_root);

    ivf_case_dir = fullfile(ivf_root, case_id);
    spea2_case_dir = fullfile(spea2_root, case_id);
    if ~isfolder(ivf_case_dir), mkdir(ivf_case_dir); end
    if ~isfolder(spea2_case_dir), mkdir(spea2_case_dir); end

    for ri = 1:n_runs
        run_id = seed_base + (ci - 1) * n_runs + ri;

        ivf_file = fullfile(ivf_case_dir, sprintf('IVF_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));
        spea2_file = fullfile(spea2_case_dir, sprintf('SPEA2_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));

        % Skip if both already exist
        if isfile(ivf_file) && isfile(spea2_file)
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
            'N_pop', N_pop, ...
            'maxFE', maxFE, ...
            'ivf_file', ivf_file, ...
            'spea2_file', spea2_file, ...
            'platemo_dir', platemo_dir, ...
            'ivf_trace_dir', ivf_trace_dir, ...
            'spea2_trace_dir', spea2_trace_dir);
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
        local_run_pair(j);
    catch ME
        fprintf('[FAIL] %s run %d: %s\n', j.case_id, j.run_id, ME.message);
        fail_count = fail_count + 1; %#ok<PFBFN>
    end
end

elapsed_h = toc(t_start) / 3600;
fprintf('\n=== Complete ===\n');
fprintf('Jobs: %d | Failures: %d | Elapsed: %.2f hours\n', n_jobs, fail_count, elapsed_h);
diary off;


%% =================== Worker function ===================
function local_run_pair(j)
    % Each worker must add PlatEMO to its own path
    addpath(genpath(j.platemo_dir));
    addpath(j.ivf_trace_dir, '-begin');
    addpath(j.spea2_trace_dir, '-begin');

    problem_handle = str2func(j.problem_name);

    % ---- IVF-SPEA2 run ----
    if ~isfile(j.ivf_file)
        rng(j.seed, 'twister');
        Problem = feval(problem_handle, 'M', j.M_obj, 'D', j.D_vars, 'N', j.N_pop, 'maxFE', j.maxFE);
        Algo = IVFSPEA2V2TRACE('parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0}, ...
            'save', 1, 'run', j.run_id, 'outputFcn', @(~,~) []);
        Algo.Solve(Problem);

        trace_generations = Algo.TraceGenerations; %#ok<NASGU>
        trace_cycles = Algo.TraceCycles; %#ok<NASGU>
        trace_params = Algo.TraceParameters; %#ok<NASGU>
        meta = struct('case_id', j.case_id, 'problem', j.problem_name, ...
            'm', j.M_obj, 'd', j.D_vars, 'run_id', j.run_id, 'seed', j.seed, ...
            'algorithm', 'IVFSPEA2V2', 'role', j.role, ...
            'maxFE', j.maxFE, 'N', j.N_pop); %#ok<NASGU>
        local_save(j.ivf_file, trace_generations, trace_cycles, trace_params, meta);
    end

    % ---- SPEA2 baseline run (same seed) ----
    if ~isfile(j.spea2_file)
        rng(j.seed, 'twister');
        Problem = feval(problem_handle, 'M', j.M_obj, 'D', j.D_vars, 'N', j.N_pop, 'maxFE', j.maxFE);
        Algo = SPEA2TRACE('save', 1, 'run', j.run_id, 'outputFcn', @(~,~) []);
        Algo.Solve(Problem);

        trace_generations = Algo.TraceGenerations; %#ok<NASGU>
        trace_cycles = {}; %#ok<NASGU>
        trace_params = struct(); %#ok<NASGU>
        meta = struct('case_id', j.case_id, 'problem', j.problem_name, ...
            'm', j.M_obj, 'd', j.D_vars, 'run_id', j.run_id, 'seed', j.seed, ...
            'algorithm', 'SPEA2', 'role', j.role, ...
            'maxFE', j.maxFE, 'N', j.N_pop); %#ok<NASGU>
        local_save(j.spea2_file, trace_generations, trace_cycles, trace_params, meta);
    end

    fprintf('  [OK] %s run %d\n', j.case_id, j.run_id);
end


%% =================== Save wrapper (parfor-safe) ===================
function local_save(filepath, trace_generations, trace_cycles, trace_params, meta) %#ok<INUSL>
    save(filepath, 'trace_generations', 'trace_cycles', 'trace_params', 'meta');
end


%% =================== Helper functions ===================
function local_write_reference_pf(problem_handle, problem_name, M_obj, D_vars, ref_root)
    out_path = fullfile(ref_root, sprintf('%s_M%d_D%d_truePF.csv', problem_name, M_obj, D_vars));
    if isfile(out_path), return; end
    prob = feval(problem_handle, 'M', M_obj, 'D', D_vars);
    pf = prob.GetOptimum(2000);
    var_names = arrayfun(@(i) sprintf('f%d', i), 1:size(pf, 2), 'UniformOutput', false);
    T = array2table(pf, 'VariableNames', var_names);
    writetable(T, out_path);
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
