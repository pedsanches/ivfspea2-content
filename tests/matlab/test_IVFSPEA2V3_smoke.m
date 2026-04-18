% test_IVFSPEA2V3_smoke.m - Integration smoke tests for IVFSPEA2V3

function tests = test_IVFSPEA2V3_smoke
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('IVFSPEA2V3'), paths.ivf_v3_path));
    verifyTrue(testCase, contains(which('CalFitness_V3'), paths.ivf_v3_path));
end


function testARModeCompletes(testCase)
    [Dec, Obj, Con] = runSmallCase({0.11, 0.10, 0, 0, 3, 1, 0});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyEqual(testCase, size(Obj, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function testEARModeCompletes(testCase)
    [Dec, Obj, Con] = runSmallCase({0.11, 0.10, 0.30, 0.20, 3, 1, 0});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyEqual(testCase, size(Obj, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function testEARNModeCompletes(testCase)
    [Dec, Obj, Con] = runSmallCase({0.11, 0.10, 0.30, 0.20, 3, 1, 1});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyEqual(testCase, size(Obj, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function testMultipleOffspringCompletes(testCase)
    [Dec, Obj, Con] = runSmallCase({0.11, 0.10, 0, 0, 3, 2, 0});

    verifyEqual(testCase, size(Dec, 1), 20);
    verifyEqual(testCase, size(Obj, 1), 20);
    verifyTrue(testCase, all(isfinite(Dec(:))));
    verifyTrue(testCase, all(isfinite(Obj(:))));
    verifyEqual(testCase, size(Con, 1), 20);
end


function [Dec, Obj, Con] = runSmallCase(algo_params)
    rng(17, 'twister');

    [Dec, Obj, Con] = platemo( ...
        'algorithm', [{@IVFSPEA2V3}, algo_params], ...
        'problem', @ZDT1, ...
        'N', 20, ...
        'maxFE', 200, ...
        'M', 2);
end
