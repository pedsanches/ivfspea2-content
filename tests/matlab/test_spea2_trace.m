%% test_spea2_trace.m -- Quick validation of SPEA2-TRACE baseline
project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO')));
spea2_trace_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO', 'Algorithms', ...
    'Multi-objective optimization', 'SPEA2-TRACE');
addpath(spea2_trace_dir, '-begin');

rng(42, 'twister');
Problem = ZDT1('M', 2, 'D', 30, 'N', 100, 'maxFE', 10000);
Algorithm = SPEA2TRACE('save', 1, 'run', 1, 'outputFcn', @(~,~) []);
Algorithm.Solve(Problem);

nGen = numel(Algorithm.TraceGenerations);
fprintf('SPEA2 Generations logged: %d\n', nGen);

g1 = Algorithm.TraceGenerations{1};
gN = Algorithm.TraceGenerations{end};
fprintf('Gen %d: IGD=%.6f HV=%.6f spread=%.4f spacing=%.4f ivf=%d\n', ...
    g1.generation, g1.igd, g1.hv, g1.spread, g1.spacing, g1.ivf_activated);
fprintf('Gen %d: IGD=%.6f HV=%.6f spread=%.4f spacing=%.4f ivf=%d\n', ...
    gN.generation, gN.igd, gN.hv, gN.spread, gN.spacing, gN.ivf_activated);

assert(nGen > 5, 'Expected at least 5 generations');
assert(gN.igd < g1.igd, 'Expected IGD to improve');
assert(gN.hv > g1.hv, 'Expected HV to improve');
assert(~g1.ivf_activated, 'SPEA2 should never activate IVF');
assert(~gN.ivf_activated, 'SPEA2 should never activate IVF');
assert(gN.n_ivf_cycles == 0, 'SPEA2 should have 0 IVF cycles');

disp('SPEA2-TRACE TEST OK');
