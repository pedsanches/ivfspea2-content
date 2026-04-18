% test_CalFitness_V3.m - Unit tests for CalFitness_V3

function tests = test_CalFitness_V3
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('CalFitness_V3'), paths.ivf_v3_path));
    verifyTrue(testCase, contains(which('EnvironmentalSelection_V3'), paths.ivf_v3_path));
end


function testRegressionMatchesReference(testCase)
    rng(42, 'twister');
    N = 80;
    M = 3;
    PopObj = rand(N, M);

    [Fitness, Forca, Distancia, DistMatrix] = CalFitness_V3(PopObj);
    [FitnessRef, ForcaRef, DistanciaRef, DistMatrixRef] = referenceCalFitness(PopObj);

    verifyEqual(testCase, Fitness, FitnessRef, 'AbsTol', 1e-12);
    verifyEqual(testCase, Forca, ForcaRef, 'AbsTol', 1e-12);
    verifyEqual(testCase, Distancia, DistanciaRef, 'AbsTol', 1e-12);
    verifyEqual(testCase, DistMatrix, DistMatrixRef, 'AbsTol', 1e-12);
end


function testDistanceMatrixShapeAndSymmetry(testCase)
    PopObj = [0.1, 0.9; 0.3, 0.7; 0.7, 0.3; 0.9, 0.1];

    [Fitness, Forca, Distancia, DistMatrix] = CalFitness_V3(PopObj);

    verifySize(testCase, Fitness, [1, 4]);
    verifySize(testCase, Forca, [1, 4]);
    verifySize(testCase, Distancia, [4, 1]);
    verifySize(testCase, DistMatrix, [4, 4]);
    verifyEqual(testCase, DistMatrix, DistMatrix.', 'AbsTol', 1e-12);
    verifyTrue(testCase, all(isinf(diag(DistMatrix))));
end


function [Fitness, Forca, Distancia, DistMatrix] = referenceCalFitness(PopObj)
    N = size(PopObj, 1);

    Dominate = false(N);
    for i = 1 : N-1
        for j = i+1 : N
            k = any(PopObj(i, :) < PopObj(j, :)) - any(PopObj(i, :) > PopObj(j, :));
            if k == 1
                Dominate(i, j) = true;
            elseif k == -1
                Dominate(j, i) = true;
            end
        end
    end

    S = sum(Dominate, 2);
    R = zeros(1, N);
    for i = 1 : N
        R(i) = sum(S(Dominate(:, i)));
    end

    DistMatrix = pdist2(PopObj, PopObj);
    DistMatrix(1:N+1:end) = inf;
    SortedDistance = sort(DistMatrix, 2);
    D = 1 ./ (SortedDistance(:, floor(sqrt(N))) + 2);

    Fitness = R + D';
    Forca = R;
    Distancia = D;
end

