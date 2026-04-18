%% test_trace_pergen.m -- Quick validation of per-generation TRACE instrumentation
project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO')));
trace_dir = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO', 'Algorithms', ...
    'Multi-objective optimization', 'IVF-SPEA2-V2-TRACE');
addpath(trace_dir, '-begin');

rng(42, 'twister');
Problem = ZDT1('M', 2, 'D', 30, 'N', 100, 'maxFE', 10000);
Algorithm = IVFSPEA2V2TRACE('parameter', {0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0}, ...
    'save', 1, 'run', 1, 'outputFcn', @(~,~) []);
Algorithm.Solve(Problem);

nGen = numel(Algorithm.TraceGenerations);
nCyc = numel(Algorithm.TraceCycles);
fprintf('Generations logged: %d\n', nGen);
fprintf('Cycles logged: %d\n', nCyc);

g1 = Algorithm.TraceGenerations{1};
gN = Algorithm.TraceGenerations{end};
fprintf('Gen %d: IGD=%.6f HV=%.6f spread=%.4f spacing=%.4f turnover=%.3f ivf=%d\n', ...
    g1.generation, g1.igd, g1.hv, g1.spread, g1.spacing, g1.turnover, g1.ivf_activated);
fprintf('Gen %d: IGD=%.6f HV=%.6f spread=%.4f spacing=%.4f turnover=%.3f ivf=%d\n', ...
    gN.generation, gN.igd, gN.hv, gN.spread, gN.spacing, gN.turnover, gN.ivf_activated);

mid = round(nGen/2);
gM = Algorithm.TraceGenerations{mid};
fprintf('Gen %d: IGD=%.6f HV=%.6f spread=%.4f spacing=%.4f turnover=%.3f ivf=%d cycles=%d\n', ...
    gM.generation, gM.igd, gM.hv, gM.spread, gM.spacing, gM.turnover, gM.ivf_activated, gM.n_ivf_cycles);

assert(nGen > 5, 'Expected at least 5 generations');
assert(gN.igd < g1.igd, 'Expected IGD to improve');
assert(gN.hv > g1.hv, 'Expected HV to improve');
assert(isfield(g1, 'nd_fraction'), 'Missing nd_fraction field');
assert(isfield(g1, 'ivf_fe'), 'Missing ivf_fe field');

disp('TRACE PER-GEN TEST OK');
