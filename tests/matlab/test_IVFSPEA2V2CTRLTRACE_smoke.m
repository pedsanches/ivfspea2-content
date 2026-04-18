function tests = test_IVFSPEA2V2CTRLTRACE_smoke
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    ctrl_trace_path = fullfile(paths.platemo_root, 'Algorithms', ...
        'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
    ctrl_algo_path = fullfile(paths.platemo_root, 'Algorithms', ...
        'Multi-objective optimization', 'IVF-SPEA2-V2-CTRL-TRACE');
    addpath(ctrl_trace_path, '-begin');
    addpath(ctrl_algo_path, '-begin');

    verifyTrue(testCase, contains(which('IVFSPEA2V2CTRLTRACE'), ctrl_algo_path));
    verifyTrue(testCase, contains(which('IVF_V2_CTRL_TRACE'), ctrl_algo_path));
end


function testControllerCompletes(testCase)
    Algorithm = runSmallCase(0.20, 0.232437);

    verifyGreaterThan(testCase, numel(Algorithm.TraceGenerations), 5);
    verifyTrue(testCase, numel(Algorithm.TraceCycles) >= 0);

    g1 = Algorithm.TraceGenerations{1};
    gN = Algorithm.TraceGenerations{end};
    verifyTrue(testCase, isfield(g1, 'igd'));
    verifyTrue(testCase, isfield(g1, 'hv'));
    verifyTrue(testCase, isfield(gN, 'controller_ivf_enabled'));
    verifyTrue(testCase, isfinite(gN.igd));
    verifyTrue(testCase, isfinite(gN.hv));
end


function testControllerCanDisableIVF(testCase)
    Algorithm = runSmallCase(0.20, 2.0);

    final_state = Algorithm.TraceParameters.controller_final;
    verifyTrue(testCase, final_state.decision_made);
    verifyFalse(testCase, final_state.ivf_enabled);
    verifyGreaterThanOrEqual(testCase, final_state.decision_generation, 1);

    states = cellfun(@(g) logical(g.controller_ivf_enabled), Algorithm.TraceGenerations);
    verifyTrue(testCase, any(~states(2:end)));
end


function Algorithm = runSmallCase(warmup_frac, turnover_threshold)
    rng(21, 'twister');
    Problem = ZDT1('M', 2, 'D', 30, 'N', 20, 'maxFE', 400);
    Algorithm = IVFSPEA2V2CTRLTRACE('parameter', ...
        {0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0, warmup_frac, turnover_threshold}, ...
        'save', 0, 'run', 1, 'outputFcn', @(~,~) []);
    Algorithm.Solve(Problem);
end
