%% run_ppsn_dynamics.m
%  PPSN 2026 — Population Dynamics experiments.
%  Runs IVF-SPEA2 (TRACE) and SPEA2 (TRACE) with identical seeds on 18
%  benchmark instances, 30 runs each.  Per-generation snapshots are saved
%  for every run.
%
%  Environment controls (all optional):
%    PPSN_RUNS        number of independent runs per case (default 30)
%    PPSN_MAXFE       function evaluation budget     (default 100000)
%    PPSN_POP         population size                (default 100)
%    PPSN_CASE_IDS    comma-separated case_id filter
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
selected_ids = local_env_tokens('PPSN_CASE_IDS');
seed_base = 70000;  % distinct from all prior run IDs

manifest_path = fullfile(project_root, 'config', 'ppsn_dynamics_cases.csv');
cases = readtable(manifest_path, 'TextType', 'string');

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

log_file = fullfile(logs_root, sprintf('ppsn_dynamics_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);

fprintf('=== PPSN 2026 Population Dynamics Runner ===\n');
fprintf('Start: %s\n', datestr(now));
fprintf('Cases: %d | Runs/case: %d | maxFE: %d | N: %d\n', height(cases), n_runs, maxFE, N_pop);
fprintf('Seed base: %d\n', seed_base);
fprintf('Log: %s\n\n', log_file);

t_start = tic;

for ci = 1:height(cases)
    case_id = char(cases.case_id(ci));
    problem_name = char(cases.problem(ci));
    M_obj = cases.m(ci);
    D_vars = cases.d(ci);
    role = char(cases.role(ci));

    fprintf('[%d/%d] %s | %s M=%d D=%d | role=%s\n', ci, height(cases), case_id, problem_name, M_obj, D_vars, role);

    problem_handle = str2func(problem_name);

    % Save reference Pareto front
    local_write_reference_pf(problem_handle, problem_name, M_obj, D_vars, ref_root);

    ivf_case_dir = fullfile(ivf_root, case_id);
    spea2_case_dir = fullfile(spea2_root, case_id);
    if ~isfolder(ivf_case_dir), mkdir(ivf_case_dir); end
    if ~isfolder(spea2_case_dir), mkdir(spea2_case_dir); end

    for ri = 1:n_runs
        run_id = seed_base + (ci - 1) * n_runs + ri;
        seed = run_id;

        ivf_file = fullfile(ivf_case_dir, sprintf('IVF_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));
        spea2_file = fullfile(spea2_case_dir, sprintf('SPEA2_%s_M%d_D%d_%d.mat', problem_name, M_obj, D_vars, run_id));

        % Skip if both already exist
        if isfile(ivf_file) && isfile(spea2_file)
            continue;
        end

        % ---- IVF-SPEA2 run ----
        if ~isfile(ivf_file)
            try
                rng(seed, 'twister');
                Problem = feval(problem_handle, 'M', M_obj, 'D', D_vars, 'N', N_pop, 'maxFE', maxFE);
                Algo = IVFSPEA2V2TRACE('parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0}, ...
                    'save', 1, 'run', run_id, 'outputFcn', @(~,~) []);
                Algo.Solve(Problem);

                trace_generations = Algo.TraceGenerations; %#ok<NASGU>
                trace_cycles = Algo.TraceCycles; %#ok<NASGU>
                trace_params = Algo.TraceParameters; %#ok<NASGU>
                meta = struct('case_id', case_id, 'problem', problem_name, ...
                    'm', M_obj, 'd', D_vars, 'run_id', run_id, 'seed', seed, ...
                    'algorithm', 'IVFSPEA2V2', 'role', role, ...
                    'maxFE', maxFE, 'N', N_pop); %#ok<NASGU>
                save(ivf_file, 'trace_generations', 'trace_cycles', 'trace_params', 'meta');
            catch ME
                fprintf('  [FAIL-IVF] run %d: %s\n', run_id, ME.message);
            end
        end

        % ---- SPEA2 baseline run (same seed) ----
        if ~isfile(spea2_file)
            try
                rng(seed, 'twister');
                Problem = feval(problem_handle, 'M', M_obj, 'D', D_vars, 'N', N_pop, 'maxFE', maxFE);
                Algo = SPEA2TRACE('save', 1, 'run', run_id, 'outputFcn', @(~,~) []);
                Algo.Solve(Problem);

                trace_generations = Algo.TraceGenerations; %#ok<NASGU>
                meta = struct('case_id', case_id, 'problem', problem_name, ...
                    'm', M_obj, 'd', D_vars, 'run_id', run_id, 'seed', seed, ...
                    'algorithm', 'SPEA2', 'role', role, ...
                    'maxFE', maxFE, 'N', N_pop); %#ok<NASGU>
                save(spea2_file, 'trace_generations', 'meta');
            catch ME
                fprintf('  [FAIL-SPEA2] run %d: %s\n', run_id, ME.message);
            end
        end
    end
    fprintf('  -> done (%d runs)\n\n', n_runs);
end

elapsed_h = toc(t_start) / 3600;
fprintf('Total elapsed: %.2f hours\n', elapsed_h);
diary off;


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
