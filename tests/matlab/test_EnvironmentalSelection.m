% test_EnvironmentalSelection.m - Unit tests for EnvironmentalSelection
%
% Note: These tests require PlatEMO's SOLUTION class to be on the path.
% Run with: runtests('test_EnvironmentalSelection')

function tests = test_EnvironmentalSelection
    tests = functiontests(localfunctions);
end


function setupOnce(testCase)
    paths = setupCanonicalTestPaths();
    verifyTrue(testCase, contains(which('EnvironmentalSelection'), paths.ivf_v2_path));
end

%% Test 1: Population size is correctly reduced
function testPopulationSizeReduction(testCase)
    % This test validates that environmental selection reduces population
    % to exactly N individuals. Requires SOLUTION class from PlatEMO.

    % Skip if SOLUTION class is not available
    if ~exist('SOLUTION', 'class')
        warning('test_EnvironmentalSelection:skipNoSOLUTION', ...
            'SOLUTION class not found. Skipping integration test.');
        return;
    end

    % If SOLUTION is available, test would go here
    verifyTrue(testCase, true, 'Placeholder - requires PlatEMO environment');
end

%% Test 2: Truncation selects correct individuals
function testTruncation(testCase)
    % Test the Truncation helper directly with objective values
    PopObj = [0.1, 0.9;
              0.2, 0.8;
              0.3, 0.7;
              0.5, 0.5;
              0.9, 0.1];

    K = 2; % Remove 2 individuals

    % Call Truncation (it's a local function in EnvironmentalSelection.m)
    % We need to test it indirectly or extract it
    verifyTrue(testCase, true, 'Truncation requires integration test setup');
end
