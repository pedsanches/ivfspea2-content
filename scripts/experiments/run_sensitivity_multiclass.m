%% run_sensitivity_multiclass.m
% Robust multi-class sensitivity runner (IVF/SPEA2, AR mode).
%
% Environment controls:
%   SENS_GROUP        = ALL | G1 | G2 | G3      (default: ALL)
%   SENS_WORKERS      = positive integer         (optional)
%   SENS_RUNS         = positive integer         (default: 30)
%   SENS_RUNBASE      = positive integer         (optional)
%   SENS_ONLY_MISSING = 0 | 1                    (default: 1)
%   SENS_MAXFE        = positive integer         (default: 25000)
%   SENS_PROBLEMS     = comma-separated labels   (default: DTLZ2_M2,WFG4_M2,DTLZ7_M3)
%
% Notes:
% - Uses canonical PlatEMO path only.
% - Group mode partitions parameter combinations by index modulo 3.
% - Group-specific default run bases avoid cross-process filename collisions:
%     G1 -> 1, G2 -> 10001, G3 -> 20001

%% Absolute paths
project_root = '/home/pedro/desenvolvimento/ivfspea2';
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
platemo_data = fullfile(platemo_dir, 'Data');

%% Runtime controls
group = upper(strtrim(getenv('SENS_GROUP')));
if isempty(group)
    group = 'ALL';
end

workers = str2double(getenv('SENS_WORKERS'));
if isnan(workers) || workers <= 0
    workers = [];
end

num_runs = str2double(getenv('SENS_RUNS'));
if isnan(num_runs) || num_runs <= 0
    num_runs = 30;
end

only_missing = str2double(getenv('SENS_ONLY_MISSING'));
if isnan(only_missing)
    only_missing = 1;
end
only_missing = only_missing ~= 0;

maxFE = str2double(getenv('SENS_MAXFE'));
if isnan(maxFE) || maxFE <= 0
    maxFE = 25000;
end

run_base = str2double(getenv('SENS_RUNBASE'));
if isnan(run_base) || run_base < 1
    switch group
        case 'G1'
            run_base = 1;
        case 'G2'
            run_base = 10001;
        case 'G3'
            run_base = 20001;
        otherwise
            run_base = 1;
    end
end
run_ids = run_base:(run_base + num_runs - 1);

%% Logging
log_dir = fullfile(project_root, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('sensitivity_%s_%s.log', lower(group), datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== Multi-Class Sensitivity Runner ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Group: %s\n', group);
fprintf('Workers requested: %s\n', local_workers_text(workers));
fprintf('Runs per combo: %d | Run range: %d..%d\n', num_runs, run_ids(1), run_ids(end));
fprintf('Only missing combos: %d\n', only_missing);
fprintf('maxFE: %d\n', maxFE);
fprintf('Log: %s\n\n', log_file);

%% Setup path (canonical only)
addpath(genpath(platemo_dir));

%% Experimental configuration
N_pop = 100;

% IVF parameters (AR mode)
C_param = 0.11;
R_param = 0.10;
M_val = 0;
V_val = 0;
Cycles_val = 3;
S_val = 1;
N_Offspring_val = 1;
EARN_val = 0;
N_Obj_Limit_val = 0;

algorithm_spec = {@IVFSPEA2, C_param, R_param, M_val, V_val, ...
    Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

% Problem set aligned with manuscript sensitivity section
problems = {
    @DTLZ2, 2, 'DTLZ2_M2';
    @WFG4,  2, 'WFG4_M2';
    @DTLZ7, 3, 'DTLZ7_M3';
};

problems_env = upper(strtrim(getenv('SENS_PROBLEMS')));
if ~isempty(problems_env)
    tokens = regexp(problems_env, '[,;\s]+', 'split');
    tokens = tokens(~cellfun(@isempty, tokens));
    labels = string(problems(:,3));
    keep = false(size(labels));
    for i = 1:numel(tokens)
        keep = keep | labels == string(tokens{i});
    end
    problems = problems(keep, :);
    if isempty(problems)
        error('No valid problems selected by SENS_PROBLEMS=%s', problems_env);
    end
end

%% Parameter grid
R_values = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300];
C_values = [0.05, 0.07, 0.11, 0.16, 0.21, 0.27, 0.32, 0.42, 0.53, 0.64];
[R_grid, C_grid] = meshgrid(R_values, C_values);
param_combinations = [R_grid(:), C_grid(:)];
num_combos = size(param_combinations, 1);

switch group
    case 'G1'
        group_idx = 1;
    case 'G2'
        group_idx = 2;
    case 'G3'
        group_idx = 3;
    otherwise
        group_idx = 0;
end

if group_idx > 0
    combo_mask = mod((1:num_combos) - 1, 3) == (group_idx - 1);
    combo_indices = find(combo_mask);
else
    combo_indices = 1:num_combos;
end

fprintf('Problems selected: %s\n', strjoin(string(problems(:,3))', ', '));
fprintf('Parameter combinations (total): %d\n', num_combos);
fprintf('Combinations in this execution: %d\n\n', numel(combo_indices));

%% Output directory
output_base = fullfile(project_root, 'data', 'sensitivity_multiclass');
if ~isfolder(output_base), mkdir(output_base); end

%% Pool
if isempty(gcp('nocreate'))
    if isempty(workers)
        parpool('local');
    else
        parpool('local', workers);
    end
end
pool = gcp;
fprintf('Parallel pool workers: %d\n\n', pool.NumWorkers);

%% Execution
inventory = {};  % {problem, combo_idx, folder, found, expected, status}
total_errors = 0;

for p = 1:size(problems, 1)
    problem_func = problems{p, 1};
    problem_M    = problems{p, 2};
    problem_tag  = problems{p, 3};
    problem_name = func2str(problem_func);
    prefix = sprintf('IVFSPEA2_%s_M%d_', problem_name, problem_M);

    fprintf('--- Problem: %s (%s) ---\n', problem_name, problem_tag);
    t_problem = tic;
    n_skip = 0;
    n_run = 0;

    for ci = 1:numel(combo_indices)
        combo_idx = combo_indices(ci);
        R_val = param_combinations(combo_idx, 1);
        C_val = param_combinations(combo_idx, 2);

        folder_name = sprintf('IVFSPEA2_R%.4f_C%.4f_%s', R_val, C_val, problem_tag);
        result_folder = fullfile(output_base, folder_name);
        if ~isfolder(result_folder), mkdir(result_folder); end

        found_runs = local_list_runs(result_folder, prefix);
        if only_missing && numel(found_runs) >= num_runs
            n_skip = n_skip + 1;
            inventory(end+1,:) = {problem_tag, combo_idx, folder_name, numel(found_runs), num_runs, 'SKIP_OK'}; %#ok<AGROW>
            continue;
        end

        runs_needed = setdiff(run_ids, found_runs);
        if isempty(runs_needed)
            n_skip = n_skip + 1;
            inventory(end+1,:) = {problem_tag, combo_idx, folder_name, numel(found_runs), num_runs, 'SKIP_RUNSET'}; %#ok<AGROW>
            continue;
        end

        fprintf('[RUN] %s | combo %d/%d | R=%.3f C=%.2f | missing %d runs\n', ...
            problem_tag, combo_idx, num_combos, R_val, C_val, numel(runs_needed));

        run_errors = cell(1, numel(runs_needed));
        parfor ri = 1:numel(runs_needed)
            run_idx = runs_needed(ri);
            try
                platemo('algorithm', algorithm_spec, ...
                        'problem', problem_func, ...
                        'N', N_pop, ...
                        'M', problem_M, ...
                        'maxFE', maxFE, ...
                        'save', 1, ...
                        'run', run_idx, ...
                        'metName', {'IGD'});
                run_errors{ri} = '';
            catch ME
                run_errors{ri} = sprintf('run %d: %s', run_idx, ME.message);
            end
        end

        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            total_errors = total_errors + numel(failed_idx);
            fprintf('[WARN] %s | combo %d | %d run failures\n', problem_tag, combo_idx, numel(failed_idx));
            for k = 1:min(3, numel(failed_idx))
                fprintf('  %s\n', run_errors{failed_idx(k)});
            end
        end

        default_folder = fullfile(platemo_data, 'IVFSPEA2');
        local_move_problem_files(default_folder, result_folder, prefix, runs_needed);

        found_runs_after = local_list_runs(result_folder, prefix);
        if numel(found_runs_after) >= num_runs
            status = 'OK';
        elseif numel(found_runs_after) > 0
            status = 'INCOMPLETE';
        else
            status = 'MISSING';
        end

        fprintf('[DONE] %s | combo %d | %d/%d (%s)\n', ...
            problem_tag, combo_idx, numel(found_runs_after), num_runs, status);

        inventory(end+1,:) = {problem_tag, combo_idx, folder_name, numel(found_runs_after), num_runs, status}; %#ok<AGROW>
        n_run = n_run + 1;
    end

    fprintf('--- Completed %s | ran %d combos, skipped %d | %.1f min ---\n\n', ...
        problem_tag, n_run, n_skip, toc(t_problem) / 60);
end

%% Summary
fprintf('\n=== Sensitivity Runner Finished ===\n');
fprintf('End: %s\n', datestr(now));
fprintf('Total run errors: %d\n', total_errors);
fprintf('Output base: %s\n', output_base);

fprintf('\n--- Completeness Check (all combos) ---\n');
for p = 1:size(problems, 1)
    problem_name = func2str(problems{p,1});
    problem_M    = problems{p,2};
    problem_tag  = problems{p,3};
    prefix = sprintf('IVFSPEA2_%s_M%d_', problem_name, problem_M);

    ok = 0; incomplete = 0; missing = 0;
    for combo_idx = 1:num_combos
        R_val = param_combinations(combo_idx, 1);
        C_val = param_combinations(combo_idx, 2);
        folder_name = sprintf('IVFSPEA2_R%.4f_C%.4f_%s', R_val, C_val, problem_tag);
        folder_path = fullfile(output_base, folder_name);
        if ~isfolder(folder_path)
            missing = missing + 1;
            continue;
        end

        n = numel(local_list_runs(folder_path, prefix));
        if n >= num_runs
            ok = ok + 1;
        elseif n > 0
            incomplete = incomplete + 1;
        else
            missing = missing + 1;
        end
    end

    fprintf('  %s: %d/%d OK, %d incomplete, %d missing\n', ...
        problem_tag, ok, num_combos, incomplete, missing);
end

delete(gcp('nocreate'));
diary off;

%% ===== Local helpers =====
function txt = local_workers_text(workers)
if isempty(workers)
    txt = 'default';
else
    txt = sprintf('%d', workers);
end
end

function runs = local_list_runs(folder, prefix)
runs = [];
if ~isfolder(folder)
    return;
end

files = dir(fullfile(folder, [prefix '*.mat']));
if isempty(files)
    return;
end

for i = 1:numel(files)
    tk = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
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

function local_move_problem_files(default_folder, result_folder, prefix, run_ids)
if ~isfolder(default_folder)
    return;
end

files = dir(fullfile(default_folder, [prefix '*.mat']));
if isempty(files)
    return;
end

for i = 1:numel(files)
    name = files(i).name;
    tk = regexp(name, '_(\d+)\.mat$', 'tokens', 'once');
    if isempty(tk)
        continue;
    end
    r = str2double(tk{1});
    if isnan(r)
        continue;
    end

    if ~isempty(run_ids) && ~ismember(r, run_ids)
        continue;
    end

    src = fullfile(files(i).folder, name);
    dst = fullfile(result_folder, name);
    if isfile(dst)
        continue;
    end
    movefile(src, result_folder);
end
end
