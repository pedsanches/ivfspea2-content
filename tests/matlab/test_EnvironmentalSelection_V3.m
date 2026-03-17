% test_EnvironmentalSelection_V3.m - Unit tests for EnvironmentalSelection_V3

function tests = test_EnvironmentalSelection_V3
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('EnvironmentalSelection_V3'), paths.ivf_v3_path));
    verifyTrue(testCase, contains(which('CalFitness_V3'), paths.ivf_v3_path));
end


function testPopulationSizeReduction(testCase)
    [Problem, Combined] = buildCombinedPopulation();

    [Selected, Fitness] = EnvironmentalSelection_V3(Combined, Problem.N);

    verifyEqual(testCase, size(Selected, 2), Problem.N);
    verifySize(testCase, Fitness, [1, Problem.N]);
end


function testPrecomputedFitnessMatchesImplicitPath(testCase)
    [Problem, Combined] = buildCombinedPopulation();

    [SelectedA, FitnessA] = EnvironmentalSelection_V3(Combined, Problem.N);
    [FullFitness, ~, ~, DistMatrix] = CalFitness_V3(Combined.objs);
    [SelectedB, FitnessB] = EnvironmentalSelection_V3(Combined, Problem.N, FullFitness, DistMatrix);

    verifyEqual(testCase, SelectedA.decs, SelectedB.decs, 'AbsTol', 1e-12);
    verifyEqual(testCase, SelectedA.objs, SelectedB.objs, 'AbsTol', 1e-12);
    verifyEqual(testCase, FitnessA, FitnessB, 'AbsTol', 1e-12);
end


function [Problem, Combined] = buildCombinedPopulation()
    rng(13, 'twister');
    Problem = ZDT1('N', 20, 'maxFE', 200);
    Population = Problem.Initialization();

    extraN = 6;
    lower = repmat(Problem.lower, extraN, 1);
    span = repmat(Problem.upper - Problem.lower, extraN, 1);
    Extra = Problem.Evaluation(lower + rand(extraN, Problem.D) .* span);

    Combined = [Population, Extra];
end

