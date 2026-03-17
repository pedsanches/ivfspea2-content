%% run_ivf_trace_cases.m
% Reproducible trace runner for mechanistic IVF/SPEA2 case studies.
%
% Environment controls:
%   IVF_TRACE_CASE_IDS        comma-separated case_id filter (optional)
%   IVF_TRACE_RUNS            positive integer, default 30
%   IVF_TRACE_RUNBASE         positive integer, default 9001
%   IVF_TRACE_MAXFE           positive integer, default 100000
%   IVF_TRACE_POP             positive integer, default 100
%   IVF_TRACE_SAVE            positive integer, default 1
%   IVF_TRACE_WORKERS         positive integer, optional
%   IVF_TRACE_ONLY_MISSING    0|1, default 1
%   IVF_TRACE_CAPTURE_POP     0|1, default 0
%   IVF_TRACE_RUN_IDS         comma-separated run ids (optional)
%
% Usage examples:
%   matlab -batch "run('experiments/run_ivf_trace_cases.m')"
%   IVF_TRACE_CAPTURE_POP=1 IVF_TRACE_RUN_IDS=9009,9017 matlab -batch "run('experiments/run_ivf_trace_cases.m')"

script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);
platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
trace_algo_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
manifest_path = fullfile(project_root, 'config', 'ivf_trace_cases.csv');
logs_root = fullfile(project_root, 'logs');

if ~isfolder(logs_root)
    mkdir(logs_root);
end

runs_per_case = local_env_int('IVF_TRACE_RUNS', 30, true);
run_base = local_env_int('IVF_TRACE_RUNBASE', 9001, true);
maxFE = local_env_int('IVF_TRACE_MAXFE', 100000, true);
N_pop = local_env_int('IVF_TRACE_POP', 100, true);
n_save = local_env_int('IVF_TRACE_SAVE', 1, true);
only_missing = local_env_bool('IVF_TRACE_ONLY_MISSING', true);
capture_population = local_env_bool('IVF_TRACE_CAPTURE_POP', false);
workers = local_env_int('IVF_TRACE_WORKERS', 0, false);
selected_case_ids = local_env_tokens('IVF_TRACE_CASE_IDS');
selected_run_ids = local_env_int_list('IVF_TRACE_RUN_IDS');

mode_label = 'summary';
if capture_population
    mode_label = 'detailed';
end

raw_root = fullfile(project_root, 'data', 'raw', 'ivf_trace_cases', mode_label);
ref_root = fullfile(project_root, 'data', 'raw', 'ivf_trace_cases', 'reference_pf');
manifest_root = fullfile(project_root, 'data', 'raw', 'ivf_trace_cases', 'manifests');

if ~isfolder(raw_root), mkdir(raw_root); end
if ~isfolder(ref_root), mkdir(ref_root); end
if ~isfolder(manifest_root), mkdir(manifest_root); end

log_file = fullfile(logs_root, sprintf('ivf_trace_%s_%s.log', mode_label, datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVF TRACE CASE RUNNER ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Mode: %s\n', mode_label);
fprintf('Runs/case: %d | run base: %d\n', runs_per_case, run_base);
fprintf('maxFE: %d | N: %d | save: %d\n', maxFE, N_pop, n_save);
fprintf('Only missing: %d | capture populations: %d\n', only_missing, capture_population);
fprintf('Workers requested: %s\n', local_workers_text(workers));
fprintf('Log: %s\n\n', log_file);

addpath(genpath(platemo_dir));
addpath(trace_algo_dir, '-begin');

resolved_algo = which('IVFSPEA2V2TRACE');
if isempty(resolved_algo)
    error('IVFSPEA2V2TRACE not found on MATLAB path.');
end
fprintf('Trace algorithm: %s\n\n', resolved_algo);

if ~isfile(manifest_path)
    error('Trace manifest not found: %s', manifest_path);
end
cases = readtable(manifest_path, 'TextType', 'string');
cases = local_filter_cases(cases, selected_case_ids);
if isempty(cases)
    error('No trace cases selected after IVF_TRACE_CASE_IDS filtering.');
end

local_write_case_manifest(cases, runs_per_case, run_base, maxFE, N_pop, capture_population, manifest_root, mode_label);

parallel_available = license('test', 'Distrib_Computing_Toolbox');
use_parallel = parallel_available;
pool_started_here = false;
if use_parallel
    cluster = parcluster('local');
    job_storage_root = fullfile(logs_root, 'parjobs_ivf_trace');
    if ~isfolder(job_storage_root)
        mkdir(job_storage_root);
    end
    cluster.JobStorageLocation = fullfile(job_storage_root, sprintf('%s_%s', mode_label, datestr(now, 'yyyymmdd_HHMMSS')));
    if ~isfolder(cluster.JobStorageLocation)
        mkdir(cluster.JobStorageLocation);
    end

    if isempty(gcp('nocreate'))
        if isempty(workers) || workers <= 0
            parpool(cluster);
        else
            parpool(cluster, min(workers, cluster.NumWorkers));
        end
        pool_started_here = true;
    end
else
    fprintf('Parallel Computing Toolbox unavailable; using serial execution.\n\n');
end

t_start = tic;
for ci = 1:height(cases)
    case_row = cases(ci, :);
    case_id = char(case_row.case_id);
    problem_name = char(case_row.problem);
    M_obj = case_row.m;
    D_vars = case_row.d;
    role = char(case_row.role);
    display_label = char(case_row.display_label);
    seed_base = case_row.seed_base;

    fprintf('[%d/%d] %s | %s | M=%d D=%d\n', ci, height(cases), case_id, problem_name, M_obj, D_vars);

    case_dir = fullfile(raw_root, case_id);
    if ~isfolder(case_dir)
        mkdir(case_dir);
    end

    problem_handle = str2func(problem_name);
    local_write_reference_pf(problem_handle, problem_name, M_obj, D_vars, ref_root);

    planned_runs = run_base:(run_base + runs_per_case - 1);
    if ~isempty(selected_run_ids)
        planned_runs = intersect(planned_runs, selected_run_ids);
    end
    if isempty(planned_runs)
        fprintf('  -> no runs left after IVF_TRACE_RUN_IDS filtering\n');
        continue;
    end

    run_records = table('Size', [numel(planned_runs), 5], ...
        'VariableTypes', {'double', 'double', 'string', 'string', 'logical'}, ...
        'VariableNames', {'run_id', 'seed', 'file_path', 'status', 'capture_population'});

    for i = 1:numel(planned_runs)
        run_id = planned_runs(i);
        seed = seed_base + (run_id - run_base);
        file_path = fullfile(case_dir, sprintf('IVFSPEA2V2TRACE_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));
        run_records.run_id(i) = run_id;
        run_records.seed(i) = seed;
        run_records.file_path(i) = string(file_path);
        run_records.status(i) = "planned";
        run_records.capture_population(i) = capture_population;
        if only_missing && isfile(file_path)
            run_records.status(i) = "existing";
        end
    end

    writetable(run_records, fullfile(manifest_root, sprintf('%s_%s_runs.csv', case_id, mode_label)));

    todo_runs = run_records(run_records.status ~= "existing", :);
    if isempty(todo_runs)
        fprintf('  -> all requested runs already present\n\n');
        continue;
    end

    fprintf('  -> executing %d runs (%s)\n', height(todo_runs), local_exec_mode(use_parallel));
    if use_parallel
        parfor ri = 1:height(todo_runs)
            row = todo_runs(ri, :);
            local_execute_trace_run(row, problem_handle, case_row, case_id, display_label, role, ...
                problem_name, M_obj, D_vars, N_pop, maxFE, n_save, capture_population, mode_label);
        end
    else
        for ri = 1:height(todo_runs)
            row = todo_runs(ri, :);
            local_execute_trace_run(row, problem_handle, case_row, case_id, display_label, role, ...
                problem_name, M_obj, D_vars, N_pop, maxFE, n_save, capture_population, mode_label);
        end
    end

    missing_after = 0;
    for ri = 1:height(todo_runs)
        if ~isfile(char(todo_runs.file_path(ri)))
            missing_after = missing_after + 1;
        end
    end
    if missing_after > 0
        error('Trace run(s) failed for %s: %d output file(s) missing after execution.', case_id, missing_after);
    end

    fprintf('  -> done\n\n');
end

fprintf('Elapsed hours: %.3f\n', toc(t_start) / 3600);

if pool_started_here
    delete(gcp('nocreate'));
end
diary off;


function cases = local_filter_cases(cases, selected_case_ids)
    if isempty(selected_case_ids)
        return;
    end
    keep = false(height(cases), 1);
    for i = 1:height(cases)
        keep(i) = any(strcmpi(char(cases.case_id(i)), selected_case_ids));
    end
    cases = cases(keep, :);
end

function local_write_reference_pf(problem_handle, problem_name, M_obj, D_vars, ref_root)
    out_path = fullfile(ref_root, sprintf('%s_M%d_D%d_truePF.csv', problem_name, M_obj, D_vars));
    if isfile(out_path)
        return;
    end
    prob = feval(problem_handle, 'M', M_obj, 'D', D_vars);
    pf = prob.GetOptimum(2000);
    var_names = arrayfun(@(i) sprintf('f%d', i), 1:size(pf, 2), 'UniformOutput', false);
    T = array2table(pf, 'VariableNames', var_names);
    writetable(T, out_path);
end

function local_write_case_manifest(cases, runs_per_case, run_base, maxFE, N_pop, capture_population, manifest_root, mode_label)
    out = cases;
    out.runs_per_case = repmat(runs_per_case, height(out), 1);
    out.run_base = repmat(run_base, height(out), 1);
    out.maxFE = repmat(maxFE, height(out), 1);
    out.population_size = repmat(N_pop, height(out), 1);
    out.capture_population = repmat(capture_population, height(out), 1);
    writetable(out, fullfile(manifest_root, sprintf('ivf_trace_cases_%s.csv', mode_label)));
end

function value = local_env_int(name, default_value, required_positive)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = default_value;
        return;
    end
    value = str2double(raw);
    if isnan(value) || ~isfinite(value) || value ~= round(value)
        error('%s must be an integer. Got: %s', name, raw);
    end
    if required_positive && value < 1
        error('%s must be >= 1. Got: %d', name, value);
    end
end

function value = local_env_bool(name, default_value)
    raw = strtrim(getenv(name));
    if isempty(raw)
        value = default_value;
        return;
    end
    if any(strcmpi(raw, {'1', 'true', 'yes'}))
        value = true;
    elseif any(strcmpi(raw, {'0', 'false', 'no'}))
        value = false;
    else
        error('%s must be 0/1/true/false. Got: %s', name, raw);
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

function values = local_env_int_list(name)
    tokens = local_env_tokens(name);
    if isempty(tokens)
        values = [];
        return;
    end
    values = zeros(1, numel(tokens));
    for i = 1:numel(tokens)
        v = str2double(tokens{i});
        if isnan(v) || v ~= round(v)
            error('%s contains non-integer token: %s', name, tokens{i});
        end
        values(i) = v;
    end
end

function txt = local_workers_text(workers)
    if isempty(workers) || workers <= 0
        txt = 'cluster default';
    else
        txt = sprintf('%d', workers);
    end
end

function txt = local_exec_mode(use_parallel)
    if use_parallel
        txt = 'parallel';
    else
        txt = 'serial';
    end
end

function value = local_nan_if_missing(x)
    if ismissing(x)
        value = NaN;
    else
        value = x;
    end
end

function local_execute_trace_run(row, problem_handle, case_row, case_id, display_label, role, ...
        problem_name, M_obj, D_vars, N_pop, maxFE, n_save, capture_population, mode_label)
    run_id = row.run_id;
    seed = row.seed;
    out_file = char(row.file_path);
    try
        rng(seed, 'twister');
        Problem = feval(problem_handle, 'M', M_obj, 'D', D_vars, 'N', N_pop, 'maxFE', maxFE);
        Algorithm = IVFSPEA2V2TRACE( ...
            'parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0, double(capture_population)}, ...
            'save', n_save, ...
            'run', run_id, ...
            'metName', {'IGD', 'HV'}, ...
            'outputFcn', @(~, ~) []);
        Algorithm.Solve(Problem);
        Algorithm.CalMetric('IGD');
        Algorithm.CalMetric('HV');

        result = Algorithm.result; %#ok<NASGU>
        metric = Algorithm.metric; %#ok<NASGU>
        trace_run = struct( ...
            'trace_version', 'ivf_v2_trace_v1', ...
            'case_id', case_id, ...
            'display_label', display_label, ...
            'role', role, ...
            'problem', problem_name, ...
            'm', M_obj, ...
            'd', D_vars, ...
            'run_id', run_id, ...
            'seed', seed, ...
            'mode', mode_label, ...
            'capture_population', capture_population, ...
            'maxFE', maxFE, ...
            'population_size', N_pop, ...
            'selection_run_rule', char(case_row.run_selection), ...
            'selection_cycle_rule', char(case_row.cycle_selection), ...
            'bad_run_min_igd', local_nan_if_missing(case_row.bad_run_min_igd), ...
            'notes', char(case_row.notes), ...
            'parameters', Algorithm.TraceParameters, ...
            'n_cycles', numel(Algorithm.TraceCycles), ...
            'cycles', {Algorithm.TraceCycles}); %#ok<NASGU>
        save(out_file, 'result', 'metric', 'trace_run');
    catch ME
        fprintf('[FAIL] %s run %d: %s\n', case_id, run_id, ME.message);
    end
end
