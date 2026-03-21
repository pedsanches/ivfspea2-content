%% test_dynamics_output.m -- Validate PPSN dynamics .mat file contents
project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));

d = load(fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'ivf', ...
    'strong_pos_zdt6_m2', 'IVF_ZDT6_M2_D10_70001.mat'));
fprintf('IVF fields: %s\n', strjoin(fieldnames(d), ', '));
fprintf('IVF generations: %d\n', numel(d.trace_generations));
g1 = d.trace_generations{1}; gN = d.trace_generations{end};
fprintf('Gen %d: IGD=%.6f HV=%.4f spread=%.4f\n', g1.generation, g1.igd, g1.hv, g1.spread);
fprintf('Gen %d: IGD=%.6f HV=%.4f spread=%.4f\n', gN.generation, gN.igd, gN.hv, gN.spread);
fprintf('IVF cycles: %d\n', numel(d.trace_cycles));

fprintf('---\n');
d2 = load(fullfile(project_root, 'data', 'raw', 'ppsn_dynamics', 'spea2', ...
    'strong_pos_zdt6_m2', 'SPEA2_ZDT6_M2_D10_70001.mat'));
fprintf('SPEA2 fields: %s\n', strjoin(fieldnames(d2), ', '));
fprintf('SPEA2 generations: %d\n', numel(d2.trace_generations));
g1s = d2.trace_generations{1}; gNs = d2.trace_generations{end};
fprintf('Gen %d: IGD=%.6f HV=%.4f spread=%.4f\n', g1s.generation, g1s.igd, g1s.hv, g1s.spread);
fprintf('Gen %d: IGD=%.6f HV=%.4f spread=%.4f\n', gNs.generation, gNs.igd, gNs.hv, gNs.spread);

fprintf('\nDelta IGD final: %.6f (positive = IVF better)\n', gNs.igd - gN.igd);
fprintf('Delta HV final: %.4f (positive = IVF better)\n', gN.hv - gNs.hv);

% Validate same initial population (same seed)
assert(abs(g1.igd - g1s.igd) < 1e-10, 'Initial IGD should match (same seed)');
fprintf('\nSame-seed validation: PASSED (initial IGD matches)\n');
disp('DYNAMICS OUTPUT TEST OK');
