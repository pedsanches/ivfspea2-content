%% probe_rwmop_feasibility.m
% Quick feasibility probe across RWMOP1..RWMOP50 for one algorithm.
%
% Environment controls:
%   PROBE_ALGO     = IVFSPEA2V2 | IVFSPEA2 | SPEA2 | SPEA2SDE | MFOSPEA2 | NSGAII | NSGAIII | MOEAD | AGEMOEAII | ARMOEA
%                    (default: IVFSPEA2V2)
%   PROBE_FROM     = first RWMOP id (default: 1)
%   PROBE_TO       = last RWMOP id (default: 50)
%   PROBE_RUNS     = runs per problem (default: 1)
%   PROBE_MAXFE    = max function evaluations (default: 50000)
%   PROBE_WORKERS  = parallel workers (optional)
%   PROBE_PARALLEL = AUTO | PROBLEMS | RUNS | NONE (default: AUTO)
%   PROBE_OUTPUT_SUFFIX = optional output suffix, e.g. shard_a
%   PROBE_M_SET    = optional allowed objectives, e.g. 2,3
%
% Usage:
%   matlab -batch "run('experiments/probe_rwmop_feasibility.m')"

project_root = '/home/pedro/desenvolvimento/ivfspea2';
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
platemo_data = fullfile(platemo_dir, 'Data');
addpath(genpath(platemo_dir));

algo_name = upper(strtrim(getenv('PROBE_ALGO')));
if isempty(algo_name)
    algo_name = 'IVFSPEA2V2';
end

id_from = str2double(getenv('PROBE_FROM'));
if isnan(id_from) || id_from < 1
    id_from = 1;
end

id_to = str2double(getenv('PROBE_TO'));
if isnan(id_to) || id_to < id_from
    id_to = 50;
end

num_runs = str2double(getenv('PROBE_RUNS'));
if isnan(num_runs) || num_runs < 1
    num_runs = 1;
end

maxFE = str2double(getenv('PROBE_MAXFE'));
if isnan(maxFE) || maxFE <= 0
    maxFE = 50000;
end

workers = str2double(getenv('PROBE_WORKERS'));
if isnan(workers) || workers <= 0
    workers = [];
end

parallel_mode = upper(strtrim(getenv('PROBE_PARALLEL')));
if isempty(parallel_mode)
    parallel_mode = 'AUTO';
end

C_val = 0.11;  R_val = 0.10;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

% Canonical IVF/SPEA2-v2 defaults (config C26)
v2_C = 0.12;
v2_R = 0.225;
v2_M = 0.3;
v2_V = 0.1;
v2_Cycles = 2;
v2_Offspring = 1;
v2_EARN = 0;

switch algo_name
    case 'IVFSPEA2V2'
        algo_spec = {@IVFSPEA2V2, v2_C, v2_R, v2_M, v2_V, v2_Cycles, v2_Offspring, v2_EARN};
    case 'IVFSPEA2'
        algo_spec = {@IVFSPEA2, C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};
    case 'SPEA2'
        algo_spec = @SPEA2;
    case 'SPEA2SDE'
        algo_spec = @SPEA2SDE;
    case 'MFOSPEA2'
        algo_spec = @MFOSPEA2;
    case 'NSGAII'
        algo_spec = @NSGAII;
    case 'NSGAIII'
        algo_spec = @NSGAIII;
    case 'MOEAD'
        algo_spec = @MOEAD;
    case 'AGEMOEAII'
        algo_spec = @AGEMOEAII;
    case 'ARMOEA'
        algo_spec = @ARMOEA;
    otherwise
        error('Unsupported PROBE_ALGO=%s', algo_name);
end

probe_data_dir = fullfile(project_root, 'data', 'engineering_probe', algo_name);
if ~isfolder(probe_data_dir)
    mkdir(probe_data_dir);
end

out_dir = fullfile(project_root, 'results', 'engineering_screening');
if ~isfolder(out_dir)
    mkdir(out_dir);
end

output_suffix = lower(strtrim(getenv('PROBE_OUTPUT_SUFFIX')));
output_suffix = regexprep(output_suffix, '[^a-z0-9_-]', '');

allowed_m = local_parse_allowed_m(getenv('PROBE_M_SET'));

problem_ids = id_from:id_to;

if strcmp(parallel_mode, 'AUTO')
    if num_runs <= 1 && numel(problem_ids) > 1
        parallel_mode = 'PROBLEMS';
    elseif num_runs > 1
        parallel_mode = 'RUNS';
    else
        parallel_mode = 'NONE';
    end
end

if ~ismember(parallel_mode, {'PROBLEMS', 'RUNS', 'NONE'})
    error('Invalid PROBE_PARALLEL=%s (use AUTO, PROBLEMS, RUNS, or NONE).', parallel_mode);
end

need_pool = strcmp(parallel_mode, 'PROBLEMS') || (strcmp(parallel_mode, 'RUNS') && num_runs > 1);
if need_pool && isempty(gcp('nocreate'))
    if isempty(workers)
        parpool('local');
    else
        parpool('local', workers);
    end
end

pool_obj = gcp('nocreate');
if ~isempty(pool_obj)
    try
        pctRunOnAll('maxNumCompThreads(1);');
    catch
    end
end

fprintf('=== RWMOP feasibility probe ===\n');
fprintf('Algorithm: %s | IDs: %d..%d | Runs/problem: %d | maxFE: %d\n', algo_name, id_from, id_to, num_runs, maxFE);
fprintf('Parallel mode: %s\n', parallel_mode);
if ~isempty(pool_obj)
    fprintf('Parallel pool workers: %d\n', pool_obj.NumWorkers);
else
    fprintf('Parallel pool workers: 0 (serial)\n');
end

run_ids = 1:num_runs;
N_pop = 100;
N_save = 10;

if strcmp(parallel_mode, 'PROBLEMS')
    rows = cell(numel(problem_ids), 7);
    parfor ii = 1:numel(problem_ids)
        pid = problem_ids(ii);
        problem_name = sprintf('RWMOP%d', pid);
        rows(ii,:) = local_probe_problem(problem_name, probe_data_dir, platemo_data, algo_name, algo_spec, run_ids, N_pop, maxFE, N_save, false, allowed_m);
    end
    rows = rows(~cellfun(@isempty, rows(:,1)), :);
else
    use_run_parallel = strcmp(parallel_mode, 'RUNS') && ~isempty(pool_obj);
    rows = {};
    for pid = problem_ids
        problem_name = sprintf('RWMOP%d', pid);
        row = local_probe_problem(problem_name, probe_data_dir, platemo_data, algo_name, algo_spec, run_ids, N_pop, maxFE, N_save, use_run_parallel, allowed_m);
        if isempty(row{1})
            continue;
        end
        rows(end+1,:) = row; %#ok<AGROW>
    end
end

if isempty(output_suffix)
    out_file = fullfile(out_dir, sprintf('rwmop_feasibility_probe_%s.csv', lower(algo_name)));
else
    out_file = fullfile(out_dir, sprintf('rwmop_feasibility_probe_%s_%s.csv', lower(algo_name), output_suffix));
end
fid = fopen(out_file, 'w');
fprintf(fid, 'Problem,M,D,UsedRuns,FeasibleRuns,MedianFeasiblePoints,FeasibleRunRate\n');
for i = 1:size(rows,1)
    fprintf(fid, '%s,%d,%d,%d,%d,%.6g,%.6g\n', rows{i,1}, rows{i,2}, rows{i,3}, rows{i,4}, rows{i,5}, rows{i,6}, rows{i,7});
end
fclose(fid);

fprintf('\nSaved: %s\n', out_file);
pool_obj = gcp('nocreate');
if ~isempty(pool_obj)
    delete(pool_obj);
end

%% ===== Local helpers =====
function row = local_probe_problem(problem_name, probe_data_dir, platemo_data, algo_name, algo_spec, run_ids, N_pop, maxFE, N_save, use_run_parallel, allowed_m)
row = {'', NaN, NaN, 0, 0, NaN, NaN};

if exist(problem_name, 'file') ~= 2
    return;
end

problem = feval(problem_name);
M_obj = problem.M;
D_var = problem.D;

if ~isempty(allowed_m) && ~ismember(M_obj, allowed_m)
    return;
end

cfg_name = sprintf('%s_%s_M%d', algo_name, problem_name, M_obj);
result_folder = fullfile(probe_data_dir, cfg_name);
if ~isfolder(result_folder)
    mkdir(result_folder);
end

found_runs = local_list_runs(result_folder, algo_name, problem_name, M_obj);
missing_runs = setdiff(run_ids, found_runs);

if ~isempty(missing_runs)
    fprintf('[RUN] %s missing %d runs\n', cfg_name, numel(missing_runs));
    run_errors = cell(1, numel(missing_runs));
    problem_handle = str2func(problem_name);

    if use_run_parallel && numel(missing_runs) > 1
        parfor ri = 1:numel(missing_runs)
            r = missing_runs(ri);
            run_errors{ri} = local_run_once(algo_spec, problem_handle, M_obj, N_pop, maxFE, N_save, r);
        end
    else
        for ri = 1:numel(missing_runs)
            r = missing_runs(ri);
            run_errors{ri} = local_run_once(algo_spec, problem_handle, M_obj, N_pop, maxFE, N_save, r);
        end
    end

    bad = find(~cellfun(@isempty, run_errors));
    if ~isempty(bad)
        fprintf('  [WARN] %d run failures for %s\n', numel(bad), cfg_name);
    end
end

default_folder = fullfile(platemo_data, algo_name);
local_move_problem_files(default_folder, result_folder, algo_name, problem_name, M_obj);

found_runs = local_list_runs(result_folder, algo_name, problem_name, M_obj);
used_runs = intersect(found_runs, run_ids);

feasible_runs = 0;
feasible_points = [];
for r = used_runs
    fpath = local_run_file(result_folder, algo_name, problem_name, M_obj, r);
    if isempty(fpath)
        continue;
    end
    n_feas = local_feasible_points(fpath);
    feasible_points(end+1) = n_feas; %#ok<AGROW>
    if n_feas > 0
        feasible_runs = feasible_runs + 1;
    end
end

if isempty(feasible_points)
    med_feasible_points = NaN;
else
    med_feasible_points = median(feasible_points);
end

row = {problem_name, M_obj, D_var, numel(used_runs), feasible_runs, med_feasible_points, feasible_runs / max(1, numel(used_runs))};

fprintf('[%s] used=%d feasible_runs=%d median_feasible_points=%.1f\n', ...
    problem_name, numel(used_runs), feasible_runs, med_feasible_points);
end

function err = local_run_once(algo_spec, problem_handle, M_obj, N_pop, maxFE, N_save, run_id)
err = '';
try
    platemo('algorithm', algo_spec, ...
            'problem', problem_handle, ...
            'N', N_pop, ...
            'M', M_obj, ...
            'maxFE', maxFE, ...
            'save', N_save, ...
            'run', run_id, ...
            'metName', {'IGD','HV'});
catch ME
    err = sprintf('run %d: %s', run_id, ME.message);
end
end

function runs = local_list_runs(folder, algo_name, problem_name, M_obj)
runs = [];
if ~isfolder(folder)
    return;
end

files = dir(fullfile(folder, '*.mat'));
if isempty(files)
    return;
end

prefix = sprintf('%s_%s_M%d_', algo_name, problem_name, M_obj);
for i = 1:numel(files)
    fname = files(i).name;
    if ~startsWith(fname, prefix)
        continue;
    end
    tk = regexp(fname, '_(\d+)\.mat$', 'tokens', 'once');
    if isempty(tk)
        continue;
    end
    r = str2double(tk{1});
    if ~isnan(r)
        runs(end+1) = r; %#ok<AGROW>
    end
end
runs = unique(runs);
end

function local_move_problem_files(default_folder, result_folder, algo_name, problem_name, M_obj)
if ~isfolder(default_folder)
    return;
end

files = dir(fullfile(default_folder, '*.mat'));
if isempty(files)
    files = dir(fullfile(default_folder, '**', '*.mat'));
end

prefix = sprintf('%s_%s_M%d_', algo_name, problem_name, M_obj);
for i = 1:numel(files)
    if ~startsWith(files(i).name, prefix)
        continue;
    end
    src = fullfile(files(i).folder, files(i).name);
    dst = fullfile(result_folder, files(i).name);
    if isfile(dst)
        continue;
    end
    movefile(src, result_folder);
end
end

function fpath = local_run_file(folder, algo_name, problem_name, M_obj, run_id)
fpath = '';
prefix = sprintf('%s_%s_M%d_', algo_name, problem_name, M_obj);
files = dir(fullfile(folder, '*.mat'));
for i = 1:numel(files)
    fname = files(i).name;
    if ~startsWith(fname, prefix)
        continue;
    end
    tk = regexp(fname, '_(\d+)\.mat$', 'tokens', 'once');
    if isempty(tk)
        continue;
    end
    r = str2double(tk{1});
    if ~isnan(r) && r == run_id
        fpath = fullfile(files(i).folder, files(i).name);
        return;
    end
end
end

function n_feasible = local_feasible_points(file_path)
n_feasible = 0;
try
    d = load(file_path);
    if ~isfield(d, 'result') || ~iscell(d.result) || isempty(d.result)
        return;
    end
    pop = d.result{end};
    if iscell(pop) && ~isempty(pop)
        pop = pop{end};
    end
    if isempty(pop)
        return;
    end
    if ~isobject(pop)
        return;
    end
    cons = pop.cons;
    if isempty(cons)
        n_feasible = numel(pop);
    else
        n_feasible = sum(all(cons <= 0, 2));
    end
catch
    n_feasible = 0;
end
end

function allowed_m = local_parse_allowed_m(raw)
allowed_m = [];
s = strtrim(char(string(raw)));
if isempty(s)
    return;
end

parts = regexp(s, '[,;\s]+', 'split');
vals = [];
for i = 1:numel(parts)
    if isempty(parts{i})
        continue;
    end
    v = str2double(parts{i});
    if isnan(v) || v <= 0 || abs(v - round(v)) > 0
        error('Invalid PROBE_M_SET value: %s', parts{i});
    end
    vals(end+1) = round(v); %#ok<AGROW>
end

allowed_m = unique(vals);
end
