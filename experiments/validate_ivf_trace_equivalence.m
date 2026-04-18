%% validate_ivf_trace_equivalence.m
% Checks that IVFSPEA2V2TRACE reproduces IVFSPEA2V2 under fixed seeds.

script_dir = fileparts(mfilename('fullpath'));
project_root = fileparts(script_dir);
platemo_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
trace_algo_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
canonical_algo_dir = fullfile(platemo_dir, 'Algorithms', 'Multi-objective optimization', 'IVF-SPEA2-V2');

addpath(genpath(platemo_dir));
addpath(trace_algo_dir, '-begin');
addpath(canonical_algo_dir, '-begin');

cases = {
    @DTLZ2, 2, 11, 1101;
    @WFG2,  3, 12, 2201;
    @DTLZ4, 3, 12, 3301;
};

fprintf('=== IVF TRACE EQUIVALENCE CHECK ===\n');
for ci = 1:size(cases, 1)
    problem_handle = cases{ci, 1};
    M_obj = cases{ci, 2};
    D_vars = cases{ci, 3};
    seed = cases{ci, 4};
    problem_name = func2str(problem_handle);

    fprintf('Case %d/%d: %s M=%d D=%d seed=%d\n', ci, size(cases, 1), problem_name, M_obj, D_vars, seed);

    rng(seed, 'twister');
    canonical_problem = feval(problem_handle, 'M', M_obj, 'D', D_vars, 'N', 100, 'maxFE', 10000);
    canonical_algo = IVFSPEA2V2( ...
        'parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0}, ...
        'save', 1, ...
        'metName', {'IGD', 'HV'}, ...
        'outputFcn', @(~, ~) []);
    canonical_algo.Solve(canonical_problem);
    canonical_algo.CalMetric('IGD');
    canonical_algo.CalMetric('HV');

    rng(seed, 'twister');
    trace_problem = feval(problem_handle, 'M', M_obj, 'D', D_vars, 'N', 100, 'maxFE', 10000);
    trace_algo = IVFSPEA2V2TRACE( ...
        'parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0, 1}, ...
        'save', 1, ...
        'metName', {'IGD', 'HV'}, ...
        'outputFcn', @(~, ~) []);
    trace_algo.Solve(trace_problem);
    trace_algo.CalMetric('IGD');
    trace_algo.CalMetric('HV');

    canonical_objs = sortrows(canonical_algo.result{end, 2}.objs);
    trace_objs = sortrows(trace_algo.result{end, 2}.objs);
    if size(canonical_objs, 1) ~= size(trace_objs, 1) || size(canonical_objs, 2) ~= size(trace_objs, 2)
        error('Population shape mismatch for %s.', problem_name);
    end
    max_obj_diff = max(abs(canonical_objs(:) - trace_objs(:)));
    max_igd_diff = max(abs(canonical_algo.metric.IGD(:) - trace_algo.metric.IGD(:)));
    max_hv_diff = max(abs(canonical_algo.metric.HV(:) - trace_algo.metric.HV(:)));
    fprintf('  max |obj diff| = %.3e\n', max_obj_diff);
    fprintf('  max |IGD diff| = %.3e\n', max_igd_diff);
    fprintf('  max |HV diff|  = %.3e\n', max_hv_diff);

    tol = 1e-12;
    assert(max_obj_diff <= tol, 'Objective mismatch exceeds tolerance.');
    assert(max_igd_diff <= tol, 'IGD mismatch exceeds tolerance.');
    assert(max_hv_diff <= tol, 'HV mismatch exceeds tolerance.');
    assert(~isempty(trace_algo.TraceCycles), 'Trace variant did not record any IVF cycles.');
end

fprintf('All equivalence checks passed.\n');
