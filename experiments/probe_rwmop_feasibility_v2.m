%% probe_rwmop_feasibility_v2.m
% Canonical feasibility probe wrapper for IVF/SPEA2-v2 on RWMOP1..50.
%
% This wrapper pins the probe to IVFSPEA2V2 defaults and delegates execution
% to probe_rwmop_feasibility.m.
%
% Optional overrides (environment variables):
%   PROBE_FROM, PROBE_TO, PROBE_RUNS, PROBE_MAXFE, PROBE_WORKERS,
%   PROBE_PARALLEL, PROBE_OUTPUT_SUFFIX, PROBE_M_SET
%
% Usage:
%   matlab -batch "run('experiments/probe_rwmop_feasibility_v2.m')"

project_root = '/home/pedro/desenvolvimento/ivfspea2';

if isempty(strtrim(getenv('PROBE_ALGO')))
    setenv('PROBE_ALGO', 'IVFSPEA2V2');
end
if isempty(strtrim(getenv('PROBE_FROM')))
    setenv('PROBE_FROM', '1');
end
if isempty(strtrim(getenv('PROBE_TO')))
    setenv('PROBE_TO', '50');
end
if isempty(strtrim(getenv('PROBE_RUNS')))
    setenv('PROBE_RUNS', '1');
end

run(fullfile(project_root, 'experiments', 'probe_rwmop_feasibility.m'));
