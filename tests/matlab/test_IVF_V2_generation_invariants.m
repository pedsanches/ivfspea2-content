% test_IVF_V2_generation_invariants.m
%
% Validates one-generation invariants of IVF_V2 for all currently
% implemented IVF modes in this repository:
%   - AR   : M=0, EARN=0
%   - EAR  : M>0, EARN=0
%   - EARN : M>0, EARN=1

function tests = test_IVF_V2_generation_invariants
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('IVF_V2'), paths.ivf_v2_path));
    verifyTrue(testCase, contains(which('CalFitness'), paths.ivf_v2_path));
    verifyTrue(testCase, contains(which('EnvironmentalSelection'), paths.ivf_v2_path));
end


function testActivationSkipWhenBudgetExceeded(testCase)
    [Problem, Population, Fitness, Forca, Distancia] = buildInitialState();
    initialDecs = Population.decs;
    feBefore = Problem.FE;

    ivf_rate = 0.10;
    ivf_total_fe_in = 3; % With N=20 and FE=20, threshold is 2; this must skip

    [PopulationOut, ~, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, ...
        0.11, 0, 0, 3, ivf_total_fe_in, 1, 0, 1);

    verifyEqual(testCase, ivfGenFE, 0, 'IVF must not consume FE when trigger is off');
    verifyEqual(testCase, ivfTotalFEOut, ivf_total_fe_in, ...
        'Total IVF FE must remain unchanged when skipped');
    verifyEqual(testCase, matingN, Problem.N, ...
        'Host mating size must remain full when IVF is skipped');
    verifyEqual(testCase, Problem.FE, feBefore, ...
        'Problem FE must not change when IVF is skipped');
    verifyEqual(testCase, size(PopulationOut, 2), Problem.N, ...
        'Population size must remain N when IVF is skipped');
    verifyEqual(testCase, PopulationOut.decs, initialDecs, ...
        'Population decisions must remain unchanged when IVF is skipped');
end


function testGenerationInvariantsAR(testCase)
    [Problem, Population, Fitness, Forca, Distancia] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, ~, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, 0.10, ...
        0.11, 0, 0, 3, 0, 1, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsEAR(testCase)
    [Problem, Population, Fitness, Forca, Distancia] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, ~, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, 0.10, ...
        0.11, 0.30, 0.20, 3, 0, 1, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsEARN(testCase)
    [Problem, Population, Fitness, Forca, Distancia] = buildInitialState();
    feBefore = Problem.FE;

    [PopulationOut, ~, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, 0.10, ...
        0.11, 0.30, 0.20, 3, 0, 1, 1, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, 1);
end


function testGenerationInvariantsMultipleOffspring(testCase)
    [Problem, Population, Fitness, Forca, Distancia] = buildInitialState();
    feBefore = Problem.FE;
    nOffspring = 3;

    [PopulationOut, ~, ivfGenFE, ivfTotalFEOut, matingN] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, 0.10, ...
        0.11, 0, 0, 3, 0, nOffspring, 0, 1);

    assertCommonGenerationInvariants(testCase, Problem, PopulationOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, nOffspring);
    verifyEqual(testCase, mod(ivfGenFE, nOffspring), 0, ...
        'IVF FE should be a multiple of N_Offspring');
end


function assertCommonGenerationInvariants(testCase, Problem, PopulationOut, ...
        feBefore, ivfGenFE, ivfTotalFEOut, matingN, nOffspring)

    verifyEqual(testCase, size(PopulationOut, 2), Problem.N, ...
        'Population size after IVF must be exactly N');
    verifyGreaterThanOrEqual(testCase, ivfGenFE, 0, 'IVF generation FE must be non-negative');
    verifyLessThanOrEqual(testCase, ivfGenFE, Problem.N, ...
        'IVF generation FE must respect per-generation budget N');
    verifyEqual(testCase, Problem.FE - feBefore, ivfGenFE, ...
        'Reported IVF FE must match actual FE consumption');
    verifyEqual(testCase, ivfTotalFEOut, ivfGenFE, ...
        'With IVF_Total_FE input=0, output must equal this generation FE');
    verifyEqual(testCase, matingN, Problem.N - ivfGenFE, ...
        'Host mating size must be N - IVF_Gen_FE');

    if ivfGenFE > 0
        verifyEqual(testCase, mod(ivfGenFE, nOffspring), 0, ...
            'IVF FE should be consistent with requested offspring multiplicity');
    end
end


function [Problem, Population, Fitness, Forca, Distancia] = buildInitialState()
    rng(31, 'twister');
    Problem = ZDT1('N', 20, 'maxFE', 200);
    Population = Problem.Initialization();
    [Fitness, Forca, Distancia] = CalFitness(Population.objs);
end

