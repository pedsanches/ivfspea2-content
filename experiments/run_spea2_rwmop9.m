%% run_spea2_rwmop9.m
% Runs SPEA2 on RWMOP9 (M=2, D=4) for 60 runs to fill the gap in the
% SPEA2 baseline used in the hosts-paper cross-track comparison.
%
% Run IDs mirror the existing SPEA2 submission: 1-60.
%
% Usage:
%   matlab -batch "run('experiments/run_spea2_rwmop9.m')"

NUM_RUNS   = 60;
RUN_BASE   = 1;
MAX_FE     = 100000;
N_SAVE     = 10;
NUM_WORKERS = 6;

project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
log_dir      = fullfile(project_root, 'experiments', 'logs');
if ~isfolder(log_dir), mkdir(log_dir); end

log_file = fullfile(log_dir, sprintf('spea2_rwmop9_%s.log', ...
    datestr(now, 'yyyymmdd_HHMMSS')));
diary(log_file);
fprintf('=== SPEA2 on RWMOP9 (%d runs) ===\n', NUM_RUNS);
fprintf('Start: %s\n\n', datestr(now));

addpath(genpath(platemo_dir));
cd(platemo_dir);
data_dir = fullfile(platemo_dir, 'Data');

if isempty(gcp('nocreate'))
    c = parcluster('Processes');
    parpool(c, min(NUM_WORKERS, c.NumWorkers));
end

target_folder = fullfile(data_dir, 'SPEA2');

runs_needed = [];
for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
    fname = sprintf('SPEA2_RWMOP9_M2_D4_%d.mat', r);
    if ~isfile(fullfile(target_folder, fname))
        runs_needed(end+1) = r; %#ok<AGROW>
    end
end

if isempty(runs_needed)
    fprintf('All %d runs already present.\n', NUM_RUNS);
else
    fprintf('%d runs needed.\n', length(runs_needed));
    parfor ri = 1:length(runs_needed)
        run_idx = runs_needed(ri);
        try
            platemo('algorithm', {@SPEA2}, ...
                    'problem',   @RWMOP9, ...
                    'M',         2, ...
                    'D',         4, ...
                    'maxFE',     MAX_FE, ...
                    'save',      N_SAVE, ...
                    'run',       run_idx, ...
                    'metName',   {'IGD', 'HV'});
        catch ME
            fprintf('  [FAIL] run %d: %s\n', run_idx, ME.message);
        end
    end
end

n_found = 0;
for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
    if isfile(fullfile(target_folder, sprintf('SPEA2_RWMOP9_M2_D4_%d.mat', r)))
        n_found = n_found + 1;
    end
end
fprintf('\nFiles present: %d/%d\n', n_found, NUM_RUNS);
delete(gcp('nocreate'));
diary off;
