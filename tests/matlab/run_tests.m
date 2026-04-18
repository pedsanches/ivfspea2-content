% run_tests.m - Execute all MATLAB unit tests for IVF-SPEA2
%
% Usage:
%   matlab -batch "run('tests/matlab/run_tests.m')"
%   or from MATLAB: run('tests/matlab/run_tests.m')

test_dir = fileparts(mfilename('fullpath'));
addpath(test_dir);
paths = setupCanonicalTestPaths();

assert(contains(which('CalFitness'), paths.ivf_v2_path), ...
    'run_tests:CanonicalCalFitness', ...
    'CalFitness must resolve to IVF-SPEA2-V2 before running the suite.');
assert(contains(which('EnvironmentalSelection'), paths.ivf_v2_path), ...
    'run_tests:CanonicalEnvironmentalSelection', ...
    'EnvironmentalSelection must resolve to IVF-SPEA2-V2 before running the suite.');
assert(contains(which('CalFitness_V3'), paths.ivf_v3_path), ...
    'run_tests:CanonicalCalFitnessV3', ...
    'CalFitness_V3 must resolve to IVF-SPEA2-V3 before running the suite.');

% Run all tests in the tests/matlab directory
results = runtests(test_dir, 'IncludeSubfolders', true);

% Display results
disp(results);

% Return exit code
if any([results.Failed])
    fprintf('\n❌ TESTS FAILED: %d of %d\n', sum([results.Failed]), numel(results));
    if ~isempty(getenv('CI'))
        exit(1);
    end
else
    fprintf('\n✅ ALL TESTS PASSED: %d of %d\n', sum([results.Passed]), numel(results));
end
