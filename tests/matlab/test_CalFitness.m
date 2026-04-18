% test_CalFitness.m - Unit tests for CalFitness function
%
% Validates fitness calculation for known dominance scenarios.
% Run with: runtests('test_CalFitness') or run('tests/matlab/run_tests.m')

function tests = test_CalFitness
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('CalFitness'), paths.ivf_v2_path));
    verifyTrue(testCase, contains(which('EnvironmentalSelection'), paths.ivf_v2_path));
end

%% Test 1: Non-dominated front (all fitness should be < 1)
function testNonDominatedFront(testCase)
    % 2D Pareto front: no solution dominates another
    PopObj = [0.1, 0.9;
              0.3, 0.7;
              0.5, 0.5;
              0.7, 0.3;
              0.9, 0.1];

    [Fitness, Forca, Distancia] = CalFitness(PopObj);

    % All solutions are non-dominated => R(i) should be 0 for all
    verifyEqual(testCase, Forca, zeros(1, size(PopObj, 1)), ...
        'All non-dominated solutions should have strength R = 0');

    % Fitness = R + D, and R = 0, so Fitness = D (all < 1)
    verifyTrue(testCase, all(Fitness < 1), ...
        'Fitness of non-dominated front should be < 1');
end

%% Test 2: Single dominated solution
function testDominatedSolution(testCase)
    % Solution 3 is dominated by solution 1
    PopObj = [0.1, 0.1;   % dominates solution 3
              0.5, 0.5;
              0.9, 0.9];  % dominated by solution 1

    [Fitness, ~, ~] = CalFitness(PopObj);

    % The dominated solution (3) should have higher fitness
    verifyGreaterThan(testCase, Fitness(3), Fitness(1), ...
        'Dominated solution should have higher fitness than dominator');
end

%% Test 3: Identical solutions
function testIdenticalSolutions(testCase)
    PopObj = [0.5, 0.5;
              0.5, 0.5;
              0.5, 0.5];

    [Fitness, Forca, ~] = CalFitness(PopObj);

    % No dominance => all strengths should be 0
    verifyEqual(testCase, Forca, zeros(1, 3), ...
        'Identical solutions should have zero strength');

    % All fitnesses should be equal
    verifyEqual(testCase, Fitness(1), Fitness(2), 'AbsTol', 1e-10);
    verifyEqual(testCase, Fitness(2), Fitness(3), 'AbsTol', 1e-10);
end

%% Test 4: Output dimensions
function testOutputDimensions(testCase)
    N = 10;
    M = 3;
    PopObj = rand(N, M);

    [Fitness, Forca, Distancia] = CalFitness(PopObj);

    verifySize(testCase, Fitness, [1, N], 'Fitness should be 1xN');
    verifySize(testCase, Forca, [1, N], 'Forca should be 1xN');
    verifySize(testCase, Distancia, [N, 1], 'Distancia should be Nx1');
end

%% Test 5: Two objectives, clear dominance chain
function testDominanceChain(testCase)
    % A dominates B dominates C
    PopObj = [0.1, 0.1;   % A: best
              0.5, 0.5;   % B: middle
              0.9, 0.9];  % C: worst

    [Fitness, ~, ~] = CalFitness(PopObj);

    verifyLessThan(testCase, Fitness(1), Fitness(2), ...
        'A should have lower fitness than B');
    verifyLessThan(testCase, Fitness(2), Fitness(3), ...
        'B should have lower fitness than C');
end

%% Test 6: Regression test — vectorized vs original loop (N=200, M=3)
function testVectorizedRegressionLarge(testCase)
    % Compare vectorized CalFitness against reference scalar loop
    rng(42); % Fixed seed for reproducibility
    N = 200;
    M = 3;
    PopObj = rand(N, M);

    % Get result from current (vectorized) implementation
    [Fitness, Forca, Distancia] = CalFitness(PopObj);

    % Reference: original scalar loop implementation
    Dominate_ref = false(N);
    for i = 1 : N-1
        for j = i+1 : N
            k = any(PopObj(i,:)<PopObj(j,:)) - any(PopObj(i,:)>PopObj(j,:));
            if k == 1
                Dominate_ref(i,j) = true;
            elseif k == -1
                Dominate_ref(j,i) = true;
            end
        end
    end
    S_ref = sum(Dominate_ref,2);
    R_ref = zeros(1,N);
    for i = 1 : N
        R_ref(i) = sum(S_ref(Dominate_ref(:,i)));
    end
    Distance_ref = pdist2(PopObj,PopObj);
    Distance_ref(logical(eye(N))) = inf;
    Distance_ref = sort(Distance_ref,2);
    D_ref = 1./(Distance_ref(:,floor(sqrt(N)))+2);
    Fitness_ref = R_ref + D_ref';

    verifyEqual(testCase, Fitness, Fitness_ref, 'AbsTol', 1e-12, ...
        'Vectorized CalFitness must match original scalar loop');
    verifyEqual(testCase, Forca, R_ref, 'AbsTol', 1e-12, ...
        'Forca (R) must match reference');
    verifyEqual(testCase, Distancia, D_ref, 'AbsTol', 1e-12, ...
        'Distancia (D) must match reference');
end

%% Test 7: Scale test (N=500, M=5)
function testScaleLargePopulation(testCase)
    rng(123);
    N = 500;
    M = 5;
    PopObj = rand(N, M);

    [Fitness, Forca, Distancia] = CalFitness(PopObj);

    % Verify dimensions and basic properties
    verifySize(testCase, Fitness, [1, N]);
    verifySize(testCase, Forca, [1, N]);
    verifySize(testCase, Distancia, [N, 1]);
    verifyTrue(testCase, all(Fitness >= 0), 'Fitness should be non-negative');
    verifyTrue(testCase, all(Forca >= 0), 'Forca should be non-negative');
    verifyTrue(testCase, all(Distancia > 0), 'Distancia should be positive');
end
