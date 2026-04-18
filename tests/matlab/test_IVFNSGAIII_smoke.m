% test_IVFNSGAIII_smoke.m - Integration smoke tests for IVF/NSGA-III
%
% Validates runtime stability of IVF-NSGA-III (AR variant, DE operator) on DTLZ2.
% Note: UniformPoint adjusts N to the nearest valid simplex lattice size —
% assertions check size consistency and finiteness, not a specific N value.

function tests = test_IVFNSGAIII_smoke
    tests = functiontests(localfunctions);
end


function setupOnce(testCase) %#ok<INUSD>
    setupCanonicalTestPaths();
end


function testDefaultParamsComplete(testCase)
    % Default parameters: ivf_rate=0.10, C=0.10, Cycles=5
    [Dec, Obj, Con] = runSmallCase({});

    N_actual = size(Dec, 1);
    verifyGreaterThan(testCase, N_actual, 0, 'Population must be non-empty');
    verifyEqual(testCase, size(Obj, 1), N_actual, 'Obj rows must match population size');
    verifyEqual(testCase, size(Con, 1), N_actual, 'Con rows must match population size');
    verifyTrue(testCase, all(isfinite(Dec(:))), 'Decision variables must be finite');
    verifyTrue(testCase, all(isfinite(Obj(:))), 'Objective values must be finite');
end


function testHighBudgetComplete(testCase)
    % ivf_rate=0.5: IVF consumes up to 50% of evaluations
    [Dec, Obj, Con] = runSmallCase({0.5, 0.10, 5});

    N_actual = size(Dec, 1);
    verifyGreaterThan(testCase, N_actual, 0);
    verifyEqual(testCase, size(Obj, 1), N_actual);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), N_actual);
end


function testZeroBudgetComplete(testCase)
    % ivf_rate=0.0: IVF budget exhausted immediately — degenerates to plain NSGA-III
    [Dec, Obj, Con] = runSmallCase({0.0, 0.10, 5});

    N_actual = size(Dec, 1);
    verifyGreaterThan(testCase, N_actual, 0);
    verifyEqual(testCase, size(Obj, 1), N_actual);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), N_actual);
end


function testLargeCollectComplete(testCase)
    % C=0.5: collect half the population as mothers
    [Dec, Obj, Con] = runSmallCase({0.10, 0.5, 3});

    N_actual = size(Dec, 1);
    verifyGreaterThan(testCase, N_actual, 0);
    verifyEqual(testCase, size(Obj, 1), N_actual);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), N_actual);
end


function [Dec, Obj, Con] = runSmallCase(algo_params)
    rng(42, 'twister');
    % Request N=15, M=3: UniformPoint will snap to nearest valid lattice size
    [Dec, Obj, Con] = platemo( ...
        'algorithm', [{@IVFNSGAIII}, algo_params], ...
        'problem',   @DTLZ2, ...
        'N',         15, ...
        'maxFE',     300, ...
        'M',         3);
end
