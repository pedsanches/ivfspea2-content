% test_IVF_V3_generation_invariants.m

function tests = test_IVF_V3_generation_invariants
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('IVF_V3'), paths.ivf_v3_path));
    verifyTrue(testCase, contains(which('CalFitness_V3'), paths.ivf_v3_path));
    verifyTrue(testCase, contains(which('EnvironmentalSelection_V3'), paths.ivf_v3_path));
end


function testActivationSkipWhenBudgetExceeded(testCase)
    [Problem, Population, Fitness] = buildInitialState();
    initialDecs = Population.decs;
    feBefore = Problem.FE;

    ivf_rate = 0.10;
    ivf_total_fe_in = 3;

    [PopulationOut, FitnessOut, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V3( ...
        Problem, Population, Fitness, [], [], ivf_rate, ...
        0.11, 0, 0, 3, ivf_total_fe_in, 1, 0, 1);

    verifyEqual(testCase, ivfGenFE, 0);
    verifyEqual(testCase, ivfTotalFEOut, ivf_total_fe_in);
    verifyEqual(testCase, matingN, Problem.N);
    verifyEqual(testCase, Problem.FE, feBefore);
    verifyEqual(testCase, size(PopulationOut, 2), Problem.N);
    verifyEqual(testCase, PopulationOut.decs, initialDecs);
    verifyEqual(testCase, FitnessOut, Fitness, 'AbsTol', 1e-12);
end


function testGenerationInvariantsAR(testCase)
    [Problem, Population, Fitness] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, FitnessOut, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V3( ...
        Problem, Population, Fitness, [], [], 0.10, ...
        0.11, 0, 0, 3, 0, 1, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, FitnessOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsEAR(testCase)
    [Problem, Population, Fitness] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, FitnessOut, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V3( ...
        Problem, Population, Fitness, [], [], 0.10, ...
        0.11, 0.30, 0.20, 3, 0, 1, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, FitnessOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsEARN(testCase)
    [Problem, Population, Fitness] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, FitnessOut, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V3( ...
        Problem, Population, Fitness, [], [], 0.10, ...
        0.11, 0.30, 0.20, 3, 0, 1, 1, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, FitnessOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsMultipleOffspring(testCase)
    [Problem, Population, Fitness] = buildInitialState();
    feBefore = Problem.FE;
    nOffspring = 3;

    [PopulationOut, FitnessOut, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V3( ...
        Problem, Population, Fitness, [], [], 0.10, ...
        0.11, 0, 0, 3, 0, nOffspring, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, FitnessOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, nOffspring);
    verifyEqual(testCase, mod(ivfGenFE, nOffspring), 0);
end


function assertCommonGenerationInvariants(testCase, Problem, PopulationOut, FitnessOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, nOffspring)

    verifyEqual(testCase, size(PopulationOut, 2), Problem.N);
    verifySize(testCase, FitnessOut, [1, Problem.N]);
    verifyGreaterThanOrEqual(testCase, ivfGenFE, 0);
    verifyLessThanOrEqual(testCase, ivfGenFE, Problem.N);
    verifyEqual(testCase, Problem.FE - feBefore, ivfGenFE);
    verifyEqual(testCase, ivfTotalFEOut, ivfGenFE);
    verifyEqual(testCase, matingN, Problem.N - ivfGenFE);

    if ivfGenFE > 0
        verifyEqual(testCase, mod(ivfGenFE, nOffspring), 0);
    end
end


function [Problem, Population, Fitness] = buildInitialState()
    rng(31, 'twister');
    Problem = ZDT1('N', 20, 'maxFE', 200);
    Population = Problem.Initialization();
    Fitness = CalFitness_V3(Population.objs);
end

