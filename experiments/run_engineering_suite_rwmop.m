%% run_engineering_suite_rwmop.m
% Robust engineering-suite runner for additional real-world validation.
%
% Stages:
%   - SCREEN: quick candidate screening (default 10 runs)
%   - MAIN:   final suite execution (default 60 runs)
%
% Environment controls:
%   ENG_SUITE_STAGE   = SCREEN | MAIN         (default: MAIN)
%   ENG_SUITE_GROUP   = ALL | G1 | G2 | G3    (default: ALL)
%   ENG_SUITE_RUNS    = positive integer       (optional override)
%   ENG_SUITE_RUNBASE = positive integer       (default: 1)
%   ENG_SUITE_WORKERS = positive integer       (optional)
%   ENG_SUITE_PROBLEMS_FILE = CSV path with columns Problem,M (optional)
%                             If provided, overrides built-in problem lists.
%
% Usage example:
%   ENG_SUITE_STAGE=SCREEN matlab -batch "run('experiments/run_engineering_suite_rwmop.m')"
%   ENG_SUITE_STAGE=SCREEN ENG_SUITE_PROBLEMS_FILE=config/engineering_candidates_rwmop_m23.csv \
%     matlab -batch "run('experiments/run_engineering_suite_rwmop.m')"

%% Absolute paths
project_root = '/home/pedro/desenvolvimento/ivfspea2';
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
platemo_data = fullfile(platemo_dir, 'Data');

%% Runtime controls
stage = upper(strtrim(getenv('ENG_SUITE_STAGE')));
if isempty(stage)
    stage = 'MAIN';
end

group = upper(strtrim(getenv('ENG_SUITE_GROUP')));
if isempty(group)
    group = 'ALL';
end

run_base = str2double(getenv('ENG_SUITE_RUNBASE'));
if isnan(run_base) || run_base < 1
    run_base = 1;
end

workers = str2double(getenv('ENG_SUITE_WORKERS'));
if isnan(workers) || workers <= 0
    workers = [];
end

%% Stage configuration
switch stage
    case 'SCREEN'
        num_runs_default = 10;
        output_subdir = 'engineering_screening';
        % Candidate set for fast discriminative screening
        % Columns: {problem_name, M}
        problems = {
            'RWMOP20', 2;
            'RWMOP13', 3;
            'RWMOP8',  3;
            'RWMOP24', 3;
            'RWMOP21', 2;
            'RWMOP29', 2;
        };
    case 'MAIN'
        num_runs_default = 60;
        output_subdir = 'engineering_suite';
        % Final high-quality suite
        % Selected via SCREEN phase (feasibility + discriminative behavior)
        problems = {
            'RWMOP9',  2;
            'RWMOP21', 2;
            'RWMOP8',  3;
        };
    otherwise
        error('Invalid ENG_SUITE_STAGE=%s (use SCREEN or MAIN).', stage);
end

problems_file = strtrim(getenv('ENG_SUITE_PROBLEMS_FILE'));
if ~isempty(problems_file)
    problems = local_load_problem_list(problems_file, project_root);
end

num_runs = str2double(getenv('ENG_SUITE_RUNS'));
if isnan(num_runs) || num_runs <= 0
    num_runs = num_runs_default;
end

run_ids = run_base:(run_base + num_runs - 1);

%% Logging
log_dir = fullfile(project_root, 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end
log_file = fullfile(log_dir, sprintf('engineering_suite_%s_%s_%s.log', lower(stage), lower(group), datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== Engineering Suite Runner ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Stage: %s | Group: %s\n', stage, group);
fprintf('Runs: %d | Run range: %d..%d\n', num_runs, run_ids(1), run_ids(end));
fprintf('Problems: %d\n', size(problems,1));
if ~isempty(problems_file)
    fprintf('Problem list source: %s\n', problems_file);
end
fprintf('Log: %s\n\n', log_file);

%% Setup path (canonical only)
addpath(genpath(platemo_dir));

%% Algorithms
% IVF default production profile (canonical label remains IVFSPEA2)
ivf_cfg = struct( ...
    'collection_rate', 0.12, ...
    'ivf_activation_ratio', 0.225, ...
    'mother_mutation_fraction', 0.3, ...
    'variable_mutation_fraction', 0.1, ...
    'max_ivf_cycles', 2, ...
    'offspring_per_mother', 1, ...
    'exploration_mode', 0); % 0: EAR, 1: EARN

algorithms = {
    % Columns: {canonical_name, algorithm_spec, source_name_in_platemo_data}
    'IVFSPEA2',  {@IVFSPEA2V2, ivf_cfg.collection_rate, ivf_cfg.ivf_activation_ratio, ...
                               ivf_cfg.mother_mutation_fraction, ivf_cfg.variable_mutation_fraction, ...
                               ivf_cfg.max_ivf_cycles, ivf_cfg.offspring_per_mother, ivf_cfg.exploration_mode}, 'IVFSPEA2V2';
    'SPEA2',     @SPEA2,     'SPEA2';
    'SPEA2SDE',  @SPEA2SDE,  'SPEA2SDE';
    'MFOSPEA2',  @MFOSPEA2,  'MFOSPEA2';
    'NSGAII',    @NSGAII,    'NSGAII';
    'NSGAIII',   @NSGAIII,   'NSGAIII';
    'MOEAD',     @MOEAD,     'MOEAD';
    'AGEMOEAII', @AGEMOEAII, 'AGEMOEAII';
    'ARMOEA',    @ARMOEA,    'ARMOEA';
};

switch group
    case 'G1'
        selected = {'IVFSPEA2', 'SPEA2', 'SPEA2SDE'};
    case 'G2'
        selected = {'MFOSPEA2', 'NSGAII', 'NSGAIII'};
    case 'G3'
        selected = {'MOEAD', 'AGEMOEAII', 'ARMOEA'};
    otherwise
        selected = algorithms(:,1);
end

mask = ismember(algorithms(:,1), selected);
algorithms = algorithms(mask,:);

if isempty(algorithms)
    error('No algorithms selected for group %s.', group);
end

if isempty(problems)
    error('No problems configured for stage %s.', stage);
end

%% Output
output_base = fullfile(project_root, 'data', output_subdir);
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
try
    pctRunOnAll('maxNumCompThreads(1);');
catch
end
fprintf('Parallel pool workers: %d\n\n', pool.NumWorkers);

%% Main execution
N_pop = 100;
maxFE = 100000;
N_save = 10;

inventory = {};  % {config, found, expected, status}
total_errors = 0;

for pi = 1:size(problems,1)
    problem_name = problems{pi,1};
    M_obj = problems{pi,2};
    problem_handle = str2func(problem_name);

    fprintf('\n=== Problem %s (M=%d) ===\n', problem_name, M_obj);

    for ai = 1:size(algorithms,1)
        algo_name = algorithms{ai,1};
        algo_spec = algorithms{ai,2};
        source_algo_name = algorithms{ai,3};

        config_name = sprintf('%s_%s_M%d', algo_name, problem_name, M_obj);
        result_folder = fullfile(output_base, config_name);
        if ~isfolder(result_folder), mkdir(result_folder); end

        local_alias_result_files(result_folder, source_algo_name, algo_name, problem_name, M_obj);

        found_runs = local_list_runs(result_folder, algo_name, problem_name, M_obj);
        runs_needed = setdiff(run_ids, found_runs);

        if isempty(runs_needed)
            fprintf('[SKIP] %s - complete (%d/%d)\n', config_name, numel(found_runs), num_runs);
            inventory(end+1,:) = {config_name, numel(found_runs), num_runs, 'OK'}; %#ok<AGROW>
            continue;
        end

        fprintf('[START] %s - missing %d runs\n', config_name, numel(runs_needed));
        t_cfg = tic;

        run_errors = cell(1, numel(runs_needed));
        parfor ri = 1:numel(runs_needed)
            run_idx = runs_needed(ri);
            try
                platemo('algorithm', algo_spec, ...
                        'problem', problem_handle, ...
                        'N', N_pop, ...
                        'M', M_obj, ...
                        'maxFE', maxFE, ...
                        'save', N_save, ...
                        'run', run_idx, ...
                        'metName', {'IGD','HV'});
                run_errors{ri} = '';
            catch ME
                run_errors{ri} = sprintf('run %d: %s', run_idx, ME.message);
            end
        end

        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            total_errors = total_errors + numel(failed_idx);
            fprintf('[WARN] %s - %d run failures\n', config_name, numel(failed_idx));
            for k = 1:min(5, numel(failed_idx))
                fprintf('  %s\n', run_errors{failed_idx(k)});
            end
        end

        default_folder = fullfile(platemo_data, source_algo_name);
        local_move_problem_files(default_folder, result_folder, source_algo_name, algo_name, problem_name, M_obj);

        found_runs = local_list_runs(result_folder, algo_name, problem_name, M_obj);
        n_found = numel(intersect(found_runs, run_ids));
        if n_found >= num_runs
            status = 'OK';
        elseif n_found > 0
            status = 'INCOMPLETE';
        else
            status = 'MISSING';
        end

        fprintf('[DONE]  %s - %d/%d (%s) in %.1f s\n', config_name, n_found, num_runs, status, toc(t_cfg));
        inventory(end+1,:) = {config_name, n_found, num_runs, status}; %#ok<AGROW>
    end
end

%% Summary
fprintf('\n=== Engineering Suite Finished ===\n');
fprintf('End: %s\n', datestr(now));
fprintf('Output: %s\n', output_base);
fprintf('Total run errors: %d\n', total_errors);

fprintf('\n--- Inventory ---\n');
fprintf('%-36s %-8s %-8s %s\n', 'Config', 'Found', 'Expect', 'Status');
fprintf('%s\n', repmat('-',1,68));
for i = 1:size(inventory,1)
    fprintf('%-36s %-8d %-8d %s\n', inventory{i,1}, inventory{i,2}, inventory{i,3}, inventory{i,4});
end

delete(gcp('nocreate'));
diary off;

%% ===== Local helpers =====
function problems = local_load_problem_list(input_path, project_root)
problems = {};

path_try = input_path;
if ~isfile(path_try)
    path_try = fullfile(project_root, input_path);
end
if ~isfile(path_try)
    error('ENG_SUITE_PROBLEMS_FILE not found: %s', input_path);
end

tbl = readtable(path_try, 'TextType', 'string');
required = {'Problem', 'M'};
for i = 1:numel(required)
    if ~ismember(required{i}, tbl.Properties.VariableNames)
        error('Problems CSV must contain columns: Problem,M');
    end
end

has_include = ismember('Include', tbl.Properties.VariableNames);
for i = 1:height(tbl)
    if has_include && ~local_truthy(tbl.Include(i))
        continue;
    end

    p = strtrim(char(tbl.Problem(i)));
    if isempty(p)
        continue;
    end

    m = str2double(string(tbl.M(i)));
    if isnan(m) || m <= 0 || abs(m - round(m)) > 0
        error('Invalid M at row %d in %s', i, path_try);
    end

    problems(end+1,:) = {upper(p), round(m)}; %#ok<AGROW>
end

if isempty(problems)
    error('No valid rows found in %s', path_try);
end
end

function tf = local_truthy(v)
if islogical(v)
    tf = all(v);
    return;
end
if isnumeric(v)
    tf = all(v ~= 0);
    return;
end
s = lower(strtrim(char(string(v))));
tf = ismember(s, {'1','true','yes','y'});
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
    if ~isempty(tk)
        r = str2double(tk{1});
        if ~isnan(r)
            runs(end+1) = r; %#ok<AGROW>
        end
    end
end
runs = unique(runs);
end

function local_move_problem_files(default_folder, result_folder, source_algo_name, target_algo_name, problem_name, M_obj)
if ~isfolder(default_folder)
    return;
end

files = dir(fullfile(default_folder, '*.mat'));
if isempty(files)
    files = dir(fullfile(default_folder, '**', '*.mat'));
end

source_prefix = sprintf('%s_%s_M%d_', source_algo_name, problem_name, M_obj);
target_prefix = sprintf('%s_%s_M%d_', target_algo_name, problem_name, M_obj);

for i = 1:numel(files)
    if ~startsWith(files(i).name, source_prefix)
        continue;
    end

    src = fullfile(files(i).folder, files(i).name);
    suffix = files(i).name((numel(source_prefix) + 1):end);
    dst_name = [target_prefix, suffix];
    dst = fullfile(result_folder, dst_name);

    if isfile(dst)
        if isfile(src)
            delete(src);
        end
        continue;
    end
    movefile(src, dst);
end
end

function local_alias_result_files(result_folder, source_algo_name, target_algo_name, problem_name, M_obj)
if strcmp(source_algo_name, target_algo_name)
    return;
end

if ~isfolder(result_folder)
    return;
end

files = dir(fullfile(result_folder, '*.mat'));
if isempty(files)
    return;
end

source_prefix = sprintf('%s_%s_M%d_', source_algo_name, problem_name, M_obj);
target_prefix = sprintf('%s_%s_M%d_', target_algo_name, problem_name, M_obj);

for i = 1:numel(files)
    if ~startsWith(files(i).name, source_prefix)
        continue;
    end

    src = fullfile(files(i).folder, files(i).name);
    suffix = files(i).name((numel(source_prefix) + 1):end);
    dst_name = [target_prefix, suffix];
    dst = fullfile(files(i).folder, dst_name);

    if isfile(dst)
        if isfile(src)
            delete(src);
        end
        continue;
    end
    movefile(src, dst);
end
end
