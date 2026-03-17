%% run_ivfspea2v2_tuning.m
% Phased tuning pipeline for IVFSPEA2V2 with integrity safeguards.
%
% Environment controls:
%   V2_TUNE_PHASE        = A | B | C            (default: A)
%   V2_TUNE_GROUP        = ALL | G1..Gk         (default: ALL)
%   V2_TUNE_NUM_GROUPS   = positive integer     (default: 4)
%   V2_TUNE_PROBLEM_SET  = SENTINEL | FULL12    (default: SENTINEL)
%   V2_TUNE_PROBLEMS     = comma-separated tags (optional)
%   V2_TUNE_RUNS         = positive integer     (default: 30)
%   V2_TUNE_RUNBASE      = positive integer     (phase default if unset)
%   V2_TUNE_MAXFE        = positive integer     (default: 50000)
%   V2_TUNE_POP          = positive integer     (default: 100)
%   V2_TUNE_SAVE         = positive integer     (default: 1)
%   V2_TUNE_ONLY_MISSING = 0 | 1                (default: 1)
%   V2_TUNE_WORKERS      = positive integer     (optional)
%
% Phase B fixed center controls (optional):
%   V2_TUNE_FIXED_R      = [0,1]
%   V2_TUNE_FIXED_C      = [0,1]
%   V2_TUNE_FIXED_CYCLES = integer >= 1
%
% Phase C local-refinement center controls (optional):
%   V2_TUNE_CENTER_R      = [0,1]
%   V2_TUNE_CENTER_C      = [0,1]
%   V2_TUNE_CENTER_CYCLES = integer >= 1
%
% Usage examples:
%   matlab -batch "run('scripts/experiments/run_ivfspea2v2_tuning.m')"
%   V2_TUNE_PHASE=B V2_TUNE_GROUP=G2 matlab -batch "run('scripts/experiments/run_ivfspea2v2_tuning.m')"

%% Absolute paths
project_root = '/home/pedro/desenvolvimento/ivfspea2';
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
platemo_data = fullfile(platemo_dir, 'Data');

output_root  = fullfile(project_root, 'data', 'tuning_ivfspea2v2');
results_root = fullfile(project_root, 'results', 'tuning_ivfspea2v2');
logs_root    = fullfile(project_root, 'logs');

if ~isfolder(output_root),  mkdir(output_root); end
if ~isfolder(results_root), mkdir(results_root); end
if ~isfolder(logs_root),    mkdir(logs_root); end

%% Runtime controls
phase = upper(strtrim(getenv('V2_TUNE_PHASE')));
if isempty(phase)
    phase = 'A';
end
if ~ismember(phase, {'A', 'B', 'C'})
    error('V2_TUNE_PHASE must be one of: A, B, C. Got: %s', phase);
end

group_label = upper(strtrim(getenv('V2_TUNE_GROUP')));
if isempty(group_label)
    group_label = 'ALL';
end

num_groups = local_env_int('V2_TUNE_NUM_GROUPS', 4, true);
runs_per_case = local_env_int('V2_TUNE_RUNS', 30, true);
maxFE = local_env_int('V2_TUNE_MAXFE', 50000, true);
N_pop = local_env_int('V2_TUNE_POP', 100, true);
n_save = local_env_int('V2_TUNE_SAVE', 1, true);
only_missing = local_env_bool('V2_TUNE_ONLY_MISSING', true);

workers = local_env_int('V2_TUNE_WORKERS', 0, false);
if workers <= 0
    workers = [];
end

run_base_default = local_default_run_base(phase);
run_base = local_env_int('V2_TUNE_RUNBASE', run_base_default, true);

problem_set = upper(strtrim(getenv('V2_TUNE_PROBLEM_SET')));
if isempty(problem_set)
    problem_set = 'SENTINEL';
end

%% Logging
log_file = fullfile(logs_root, sprintf('ivfspea2v2_tuning_phase%s_%s_%s.log', ...
    phase, lower(group_label), datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== IVFSPEA2V2 Tuning Runner ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Phase: %s\n', phase);
fprintf('Group: %s / total groups: %d\n', group_label, num_groups);
fprintf('Problem set: %s\n', problem_set);
fprintf('Runs per case: %d\n', runs_per_case);
fprintf('Run base: %d\n', run_base);
fprintf('maxFE: %d | N: %d | save: %d\n', maxFE, N_pop, n_save);
fprintf('Only missing: %d\n', only_missing);
fprintf('Workers requested: %s\n', local_workers_text(workers));
fprintf('Log: %s\n\n', log_file);

%% Canonical path setup and preflight
addpath(genpath(platemo_dir));
ivf_v2_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2');
addpath(ivf_v2_dir, '-begin');

resolved_algo = which('IVFSPEA2V2');
if isempty(resolved_algo)
    error('IVFSPEA2V2 not found on MATLAB path.');
end
if ~contains(resolved_algo, 'IVF-SPEA2-V2')
    error('IVFSPEA2V2 resolves to non-canonical path: %s', resolved_algo);
end

resolved_calfitness = which('CalFitness');
resolved_envsel = which('EnvironmentalSelection');
if ~contains(resolved_calfitness, 'IVF-SPEA2-V2') || ~contains(resolved_envsel, 'IVF-SPEA2-V2')
    error(['CalFitness/EnvironmentalSelection are not resolving to IVF-SPEA2-V2. ', ...
           'CalFitness=%s | EnvironmentalSelection=%s'], resolved_calfitness, resolved_envsel);
end

fprintf('Path preflight OK\n');
fprintf('  IVFSPEA2V2: %s\n', resolved_algo);
fprintf('  CalFitness: %s\n', resolved_calfitness);
fprintf('  EnvSelect : %s\n\n', resolved_envsel);

%% Load problems and configurations
problems = local_select_problems(problem_set);
problems = local_filter_problems_by_env(problems);
if isempty(problems)
    error('No problems selected. Check V2_TUNE_PROBLEMS and V2_TUNE_PROBLEM_SET.');
end

configs = local_build_phase_configs(phase);
if isempty(configs)
    error('No configurations generated for phase %s.', phase);
end

selected_cfg_indices = local_select_group_indices(numel(configs), group_label, num_groups);
if isempty(selected_cfg_indices)
    error('No configuration assigned to %s with %d groups.', group_label, num_groups);
end

fprintf('Problems selected: %d\n', numel(problems));
fprintf('Configs (total): %d | in this run: %d\n\n', numel(configs), numel(selected_cfg_indices));

%% Persist manifests for integrity verification
phase_dir = fullfile(output_root, sprintf('phase%s', phase));
if ~isfolder(phase_dir), mkdir(phase_dir); end

manifest_cfg = fullfile(results_root, sprintf('manifest_phase%s_configs.csv', phase));
manifest_prob = fullfile(results_root, sprintf('manifest_phase%s_problems.csv', phase));
manifest_case = fullfile(results_root, sprintf('manifest_phase%s_cases.csv', phase));

local_write_config_manifest(configs, phase, manifest_cfg);
local_write_problem_manifest(problems, phase, manifest_prob);
local_write_case_manifest(configs, problems, phase, run_base, runs_per_case, manifest_case);

%% Pool setup
cluster = parcluster('local');
job_storage_root = fullfile(logs_root, 'parjobs_ivfspea2v2');
if ~isfolder(job_storage_root), mkdir(job_storage_root); end
cluster.JobStorageLocation = fullfile(job_storage_root, sprintf('phase%s_%s', phase, lower(group_label)));
if ~isfolder(cluster.JobStorageLocation), mkdir(cluster.JobStorageLocation); end

pool_started_here = false;
if isempty(gcp('nocreate'))
    if isempty(workers)
        parpool(cluster);
    else
        parpool(cluster, workers);
    end
    pool_started_here = true;
end
pool = gcp('nocreate');
fprintf('Parallel pool workers: %d\n\n', pool.NumWorkers);

%% Main execution
t_all = tic;
inventory = {}; % phase, cfg_id, problem_tag, expected, found, missing, extra, status
total_run_failures = 0;

for ci = 1:numel(selected_cfg_indices)
    cfg_index = selected_cfg_indices(ci);
    cfg = configs(cfg_index);

    fprintf('=== Config %s (%d/%d in this run) ===\n', cfg.id, ci, numel(selected_cfg_indices));
    fprintf('    %s\n', cfg.description);
    fprintf('    Params: C=%.4f R=%.4f Cycles=%d M=%.3f V=%.3f EARN=%d\n', ...
        cfg.C, cfg.R, cfg.Cycles, cfg.M, cfg.V, cfg.EARN);

    for pi = 1:numel(problems)
        problem = problems(pi);
        case_index = (cfg_index - 1) * numel(problems) + pi;
        run_start = run_base + (case_index - 1) * runs_per_case;
        run_end = run_start + runs_per_case - 1;
        expected_runs = run_start:run_end;

        folder_name = sprintf('IVFSPEA2V2_%s_%s', cfg.id, problem.tag);
        result_folder = fullfile(phase_dir, folder_name);
        if ~isfolder(result_folder), mkdir(result_folder); end

        file_prefix = sprintf('IVFSPEA2V2_%s_M%d_', problem.name, problem.M);
        found_runs = local_list_runs(result_folder, file_prefix);

        if only_missing
            runs_to_execute = setdiff(expected_runs, found_runs);
        else
            runs_to_execute = expected_runs;
        end

        if isempty(runs_to_execute)
            status = local_case_status(found_runs, expected_runs);
            fprintf('[SKIP] %s | %s | already complete (%s)\n', cfg.id, problem.tag, status);
            [missing, extra] = local_missing_extra(found_runs, expected_runs);
            inventory(end+1, :) = {phase, cfg.id, problem.tag, numel(expected_runs), numel(found_runs), numel(missing), numel(extra), status}; %#ok<AGROW>
            continue;
        end

        fprintf('[RUN]  %s | %s | executing %d runs (%d..%d)\n', ...
            cfg.id, problem.tag, numel(runs_to_execute), runs_to_execute(1), runs_to_execute(end));

        t_case = tic;
        run_errors = cell(1, numel(runs_to_execute));

        algo_spec = {@IVFSPEA2V2, cfg.C, cfg.R, cfg.M, cfg.V, cfg.Cycles, cfg.N_Offspring, cfg.EARN};

        parfor ri = 1:numel(runs_to_execute)
            run_id = runs_to_execute(ri);
            try
                platemo('algorithm', algo_spec, ...
                        'problem', problem.func, ...
                        'N', N_pop, ...
                        'M', problem.M, ...
                        'maxFE', maxFE, ...
                        'save', n_save, ...
                        'run', run_id, ...
                        'metName', {'IGD', 'HV'});
                run_errors{ri} = '';
            catch ME
                run_errors{ri} = sprintf('run %d: %s', run_id, ME.message);
            end
        end

        failed_idx = find(~cellfun(@isempty, run_errors));
        if ~isempty(failed_idx)
            total_run_failures = total_run_failures + numel(failed_idx);
            fprintf('[WARN] %s | %s | %d run failures\n', cfg.id, problem.tag, numel(failed_idx));
            for fi = 1:min(5, numel(failed_idx))
                fprintf('       %s\n', run_errors{failed_idx(fi)});
            end
        end

        default_folder = fullfile(platemo_data, 'IVFSPEA2V2');
        local_move_problem_files(default_folder, result_folder, file_prefix, expected_runs);

        found_after = local_list_runs(result_folder, file_prefix);
        [missing, extra] = local_missing_extra(found_after, expected_runs);
        status = local_case_status(found_after, expected_runs);

        fprintf('[DONE] %s | %s | found=%d expected=%d status=%s | %.1fs\n', ...
            cfg.id, problem.tag, numel(found_after), numel(expected_runs), status, toc(t_case));

        inventory(end+1, :) = {phase, cfg.id, problem.tag, numel(expected_runs), numel(found_after), numel(missing), numel(extra), status}; %#ok<AGROW>
    end
end

%% Persist case manifest and inventory
timestamp = datestr(now, 'yyyymmdd_HHMMSS');
inventory_file = fullfile(results_root, sprintf('inventory_phase%s_%s_%s.csv', phase, lower(group_label), timestamp));

inv_tbl = cell2table(inventory, 'VariableNames', ...
    {'Phase', 'ConfigID', 'ProblemTag', 'ExpectedRuns', 'FoundRuns', 'MissingRuns', 'ExtraRuns', 'Status'});
writetable(inv_tbl, inventory_file);

%% Summary
elapsed_min = toc(t_all) / 60;
fprintf('\n=== IVFSPEA2V2 Tuning Finished ===\n');
fprintf('End: %s\n', datestr(now));
fprintf('Elapsed: %.1f min\n', elapsed_min);
fprintf('Total run failures: %d\n', total_run_failures);
fprintf('Phase output: %s\n', phase_dir);
fprintf('Config manifest: %s\n', manifest_cfg);
fprintf('Problem manifest: %s\n', manifest_prob);
fprintf('Case manifest: %s\n', manifest_case);
fprintf('Inventory: %s\n', inventory_file);

if ~isempty(inv_tbl)
    statuses = categories(categorical(inv_tbl.Status));
    for si = 1:numel(statuses)
        s = statuses{si};
        fprintf('  Status %-12s : %d\n', s, sum(strcmp(inv_tbl.Status, s)));
    end
end

if pool_started_here
    delete(gcp('nocreate'));
end
diary off;

%% ===== Local helpers =====
function out = local_env_int(name, default_value, must_be_positive)
raw = str2double(getenv(name));
if isnan(raw)
    out = default_value;
    return;
end
out = round(raw);
if must_be_positive && out <= 0
    error('%s must be a positive integer.', name);
end
end

function out = local_env_bool(name, default_value)
raw = strtrim(getenv(name));
if isempty(raw)
    out = logical(default_value);
    return;
end
num = str2double(raw);
if isnan(num)
    error('%s must be 0 or 1.', name);
end
out = num ~= 0;
end

function txt = local_workers_text(workers)
if isempty(workers)
    txt = 'default';
else
    txt = sprintf('%d', workers);
end
end

function base = local_default_run_base(phase)
switch phase
    case 'A'
        base = 100001;
    case 'B'
        base = 300001;
    case 'C'
        base = 500001;
    otherwise
        base = 900001;
end
end

function problems = local_select_problems(problem_set)
full12 = struct( ...
    'tag',  {'ZDT1_M2','ZDT6_M2','WFG4_M2','WFG9_M2','DTLZ1_M3','DTLZ2_M3','DTLZ4_M3','DTLZ7_M3','WFG2_M3','WFG5_M3','MaF1_M3','MaF5_M3'}, ...
    'func', {@ZDT1,    @ZDT6,    @WFG4,    @WFG9,    @DTLZ1,     @DTLZ2,     @DTLZ4,     @DTLZ7,     @WFG2,    @WFG5,    @MaF1,    @MaF5}, ...
    'M',    {2,         2,         2,        2,        3,          3,          3,          3,          3,        3,        3,        3}, ...
    'name', {'ZDT1',   'ZDT6',    'WFG4',   'WFG9',   'DTLZ1',    'DTLZ2',    'DTLZ4',    'DTLZ7',    'WFG2',   'WFG5',   'MaF1',   'MaF5'} ...
);

sentinel_tags = {'ZDT1_M2', 'WFG4_M2', 'DTLZ7_M3', 'WFG2_M3', 'MaF5_M3'};

switch upper(problem_set)
    case 'FULL12'
        problems = full12;
    case 'SENTINEL'
        keep = arrayfun(@(p) ismember(p.tag, sentinel_tags), full12);
        problems = full12(keep);
    otherwise
        error('V2_TUNE_PROBLEM_SET must be SENTINEL or FULL12. Got: %s', problem_set);
end
end

function filtered = local_filter_problems_by_env(problems)
raw = upper(strtrim(getenv('V2_TUNE_PROBLEMS')));
if isempty(raw)
    filtered = problems;
    return;
end

tokens = regexp(raw, '[,;\s]+', 'split');
tokens = tokens(~cellfun(@isempty, tokens));
if isempty(tokens)
    filtered = problems;
    return;
end

keep = false(1, numel(problems));
for i = 1:numel(problems)
    keep(i) = any(strcmp(upper(problems(i).tag), tokens));
end
filtered = problems(keep);
end

function configs = local_build_phase_configs(phase)
base_Noff = 1;

switch phase
    case 'A'
        R_values = [0.05, 0.10, 0.15, 0.20];
        C_values = [0.07, 0.11, 0.16, 0.21];
        Cycles_values = [2, 3, 4];

        idx = 0;
        configs = struct('id', {}, 'description', {}, 'R', {}, 'C', {}, 'Cycles', {}, ...
            'M', {}, 'V', {}, 'EARN', {}, 'N_Offspring', {});
        for ri = 1:numel(R_values)
            for ci = 1:numel(C_values)
                for yi = 1:numel(Cycles_values)
                    idx = idx + 1;
                    configs(idx).id = sprintf('A%02d', idx);
                    configs(idx).description = 'AR baseline grid (R,C,Cycles)';
                    configs(idx).R = R_values(ri);
                    configs(idx).C = C_values(ci);
                    configs(idx).Cycles = Cycles_values(yi);
                    configs(idx).M = 0;
                    configs(idx).V = 0;
                    configs(idx).EARN = 0;
                    configs(idx).N_Offspring = base_Noff;
                end
            end
        end

    case 'B'
        R_fixed = local_env_num('V2_TUNE_FIXED_R', 0.10);
        C_fixed = local_env_num('V2_TUNE_FIXED_C', 0.11);
        Cycles_fixed = local_env_int('V2_TUNE_FIXED_CYCLES', 3, true);

        profiles = {
            'B01', 'AR control',                0.0, 0.0, 0;
            'B02', 'EAR light polynomial',      0.3, 0.1, 0;
            'B03', 'EAR medium polynomial',     0.5, 0.2, 0;
            'B04', 'EAR strong polynomial',     0.7, 0.3, 0;
            'B05', 'EARN random neogenesis',    0.5, 0.2, 1;
        };

        configs = struct('id', {}, 'description', {}, 'R', {}, 'C', {}, 'Cycles', {}, ...
            'M', {}, 'V', {}, 'EARN', {}, 'N_Offspring', {});
        for i = 1:size(profiles, 1)
            configs(i).id = profiles{i, 1};
            configs(i).description = profiles{i, 2};
            configs(i).R = R_fixed;
            configs(i).C = C_fixed;
            configs(i).Cycles = Cycles_fixed;
            configs(i).M = profiles{i, 3};
            configs(i).V = profiles{i, 4};
            configs(i).EARN = profiles{i, 5};
            configs(i).N_Offspring = base_Noff;
        end

    case 'C'
        R_center = local_env_num('V2_TUNE_CENTER_R', 0.10);
        C_center = local_env_num('V2_TUNE_CENTER_C', 0.11);
        Cycles_center = local_env_int('V2_TUNE_CENTER_CYCLES', 3, true);

        R_values = unique(local_clip([R_center - 0.025, R_center, R_center + 0.025], 0.01, 0.30));
        C_values = unique(local_clip([C_center - 0.04, C_center, C_center + 0.05], 0.05, 0.40));

        profiles = {
            'AR',    0.0, 0.0, 0;
            'EARL',  0.3, 0.1, 0;
            'EARM',  0.5, 0.2, 0;
            'EARN',  0.5, 0.2, 1;
        };

        idx = 0;
        configs = struct('id', {}, 'description', {}, 'R', {}, 'C', {}, 'Cycles', {}, ...
            'M', {}, 'V', {}, 'EARN', {}, 'N_Offspring', {});
        for ri = 1:numel(R_values)
            for ci = 1:numel(C_values)
                for pi = 1:size(profiles, 1)
                    idx = idx + 1;
                    configs(idx).id = sprintf('C%02d', idx);
                    configs(idx).description = sprintf('Local refine %s around center', profiles{pi, 1});
                    configs(idx).R = R_values(ri);
                    configs(idx).C = C_values(ci);
                    configs(idx).Cycles = Cycles_center;
                    configs(idx).M = profiles{pi, 2};
                    configs(idx).V = profiles{pi, 3};
                    configs(idx).EARN = profiles{pi, 4};
                    configs(idx).N_Offspring = base_Noff;
                end
            end
        end

    otherwise
        error('Unsupported phase: %s', phase);
end
end

function val = local_env_num(name, default_value)
raw = str2double(getenv(name));
if isnan(raw)
    val = default_value;
else
    val = raw;
end
end

function arr = local_clip(arr, lo, hi)
arr = max(min(arr, hi), lo);
end

function indices = local_select_group_indices(total_count, group_label, num_groups)
if strcmpi(group_label, 'ALL')
    indices = 1:total_count;
    return;
end

tk = regexp(group_label, '^G(\d+)$', 'tokens', 'once');
if isempty(tk)
    error('V2_TUNE_GROUP must be ALL or G<k>. Got: %s', group_label);
end

group_idx = str2double(tk{1});
if isnan(group_idx) || group_idx < 1 || group_idx > num_groups
    error('Invalid group index %d for V2_TUNE_NUM_GROUPS=%d.', group_idx, num_groups);
end

mask = mod((1:total_count) - 1, num_groups) == (group_idx - 1);
indices = find(mask);
end

function local_write_config_manifest(configs, phase, out_csv)
N = numel(configs);
Phase = repmat({phase}, N, 1);
ConfigIndex = (1:N)';
ConfigID = cell(N, 1);
Description = cell(N, 1);
R = zeros(N, 1);
C = zeros(N, 1);
Cycles = zeros(N, 1);
M = zeros(N, 1);
V = zeros(N, 1);
EARN = zeros(N, 1);
N_Offspring = zeros(N, 1);

for i = 1:N
    ConfigID{i} = configs(i).id;
    Description{i} = configs(i).description;
    R(i) = configs(i).R;
    C(i) = configs(i).C;
    Cycles(i) = configs(i).Cycles;
    M(i) = configs(i).M;
    V(i) = configs(i).V;
    EARN(i) = configs(i).EARN;
    N_Offspring(i) = configs(i).N_Offspring;
end

tbl = table(Phase, ConfigIndex, ConfigID, Description, R, C, Cycles, M, V, EARN, N_Offspring);
writetable(tbl, out_csv);
end

function local_write_problem_manifest(problems, phase, out_csv)
N = numel(problems);
Phase = repmat({phase}, N, 1);
ProblemTag = cell(N, 1);
ProblemName = cell(N, 1);
M = zeros(N, 1);
for i = 1:N
    ProblemTag{i} = problems(i).tag;
    ProblemName{i} = problems(i).name;
    M(i) = problems(i).M;
end
tbl = table(Phase, ProblemTag, ProblemName, M);
writetable(tbl, out_csv);
end

function local_write_case_manifest(configs, problems, phase, run_base, runs_per_case, out_csv)
rows = {};
for cfg_index = 1:numel(configs)
    cfg = configs(cfg_index);
    for pi = 1:numel(problems)
        problem = problems(pi);
        case_index = (cfg_index - 1) * numel(problems) + pi;
        run_start = run_base + (case_index - 1) * runs_per_case;
        run_end = run_start + runs_per_case - 1;
        rows(end+1, :) = {phase, cfg_index, cfg.id, problem.tag, run_start, run_end, runs_per_case}; %#ok<AGROW>
    end
end

tbl = cell2table(rows, 'VariableNames', ...
    {'Phase', 'ConfigIndex', 'ConfigID', 'ProblemTag', 'RunStart', 'RunEnd', 'RunsPerCase'});
writetable(tbl, out_csv);
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
    val = str2double(tk{1});
    if ~isnan(val)
        runs(end+1) = val; %#ok<AGROW>
    end
end
runs = unique(runs);
end

function local_move_problem_files(default_folder, result_folder, prefix, allowed_run_ids)
if ~isfolder(default_folder)
    return;
end

files = dir(fullfile(default_folder, [prefix '*.mat']));
if isempty(files)
    return;
end

for i = 1:numel(files)
    fname = files(i).name;
    tk = regexp(fname, '_(\d+)\.mat$', 'tokens', 'once');
    if isempty(tk)
        continue;
    end
    run_id = str2double(tk{1});
    if isnan(run_id) || ~ismember(run_id, allowed_run_ids)
        continue;
    end

    src = fullfile(files(i).folder, fname);
    dst = fullfile(result_folder, fname);
    if isfile(dst)
        continue;
    end
    movefile(src, result_folder);
end
end

function [missing, extra] = local_missing_extra(found_runs, expected_runs)
missing = setdiff(expected_runs, found_runs);
extra = setdiff(found_runs, expected_runs);
end

function status = local_case_status(found_runs, expected_runs)
[missing, extra] = local_missing_extra(found_runs, expected_runs);
if isempty(missing) && isempty(extra)
    status = 'OK';
elseif ~isempty(found_runs)
    status = 'INCOMPLETE';
else
    status = 'MISSING';
end
end
