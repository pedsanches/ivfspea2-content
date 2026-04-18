% test_IVFNSGAII_smoke.m - Integration smoke tests for IVF/NSGA-II
%
% Validates runtime stability of IVF-NSGA-II (AR variant) on ZDT1.
% Checks: completes without error, population size preserved, all values finite.

function tests = test_IVFNSGAII_smoke
    tests = functiontests(localfunctions);
end


function setupOnce(testCase) %#ok<INUSD>
    setupCanonicalTestPaths();
end


function testDefaultParamsComplete(testCase)
    % Default parameters: R=0.5, C=0.07, Cycles=5
    [Dec, Obj, Con] = runSmallCase({});

    verifyEqual(testCase, size(Dec, 1), 20, 'Population size must remain N=20');
    verifyEqual(testCase, size(Obj, 1), 20);
    verifyEqual(testCase, size(Con, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))), 'Decision variables must be finite');
    verifyTrue(testCase, all(isfinite(Obj(:))), 'Objective values must be finite');
end


function testHighRateComplete(testCase)
    % R=1.0: IVF runs every generation
    [Dec, Obj, Con] = runSmallCase({1.0, 0.07, 5});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function testZeroRateComplete(testCase)
    % R=0.0: IVF never triggers — degenerates to plain NSGA-II
    [Dec, Obj, Con] = runSmallCase({0.0, 0.07, 5});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function testLargeCollectComplete(testCase)
    % C=0.5: collect half the population as donors
    [Dec, Obj, Con] = runSmallCase({0.5, 0.5, 3});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function [Dec, Obj, Con] = runSmallCase(algo_params)
    rng(42, 'twister');
    [Dec, Obj, Con] = platemo( ...
        'algorithm', [{@IVFNSGAII}, algo_params], ...
        'problem',   @ZDT1, ...
        'N',         20, ...
        'maxFE',     200, ...
        'M',         2);
end
