%% run_ablation_batch3.m — Ablation Batch 3 of 3
%  Covers: IVFSPEA2ABL4C (remaining 3) + IVFSPEA2ABLDOM (all 10 problems)
%  6 parallel runners.
%
%  Usage (6 terminals):
%    RUNNER_ID=1 matlab -batch "run('experiments/run_ablation_batch3.m')"
%    ...
%    RUNNER_ID=6 matlab -batch "run('experiments/run_ablation_batch3.m')"

%% Configuration
NUM_RUNS = 60;
MAX_FE   = 100000;
N_SAVE   = 10;

C_val = 0.11;  R_val = 0.1;  M_val = 0;  V_val = 0;
Cycles_val = 3;  S_val = 1;  N_Offspring_val = 1;
EARN_val = 0;  N_Obj_Limit_val = 0;

ivf_params = {C_val, R_val, M_val, V_val, Cycles_val, S_val, N_Offspring_val, EARN_val, N_Obj_Limit_val};

%% All combos for this batch
combos = {
    'IVFSPEA2ABL4C',  @IVFSPEA2ABL4C,  @WFG2,  3;   % 1
    'IVFSPEA2ABL4C',  @IVFSPEA2ABL4C,  @MaF1,  3;   % 2
    'IVFSPEA2ABL4C',  @IVFSPEA2ABL4C,  @MaF5,  3;   % 3
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @ZDT1,  2;   % 4
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @ZDT6,  2;   % 5
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @WFG4,  2;   % 6
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @WFG9,  2;   % 7
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @DTLZ1, 3;   % 8
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @DTLZ4, 3;   % 9
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @DTLZ7, 3;   % 10
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @WFG2,  3;   % 11
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @MaF1,  3;   % 12
    'IVFSPEA2ABLDOM', @IVFSPEA2ABLDOM, @MaF5,  3;   % 13
};

%% Get runner ID (1-6)
runner_id = str2double(getenv('RUNNER_ID'));
if isnan(runner_id) || runner_id < 1 || runner_id > 6
    error('Set RUNNER_ID=1..6 environment variable before running.');
end

%% Assign combos to runners (round-robin)
my_combos = runner_id:6:size(combos, 1);
fprintf('=== Batch 3, Runner %d: handling %d combos ===\n', runner_id, length(my_combos));

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

%% Data output directory
data_dir = fullfile(platemo_dir, 'Data');

%% Main loop
t_start = tic;

for ci = 1:length(my_combos)
    idx = my_combos(ci);
    algo_name   = combos{idx, 1};
    algo_handle = combos{idx, 2};
    prob_handle = combos{idx, 3};
    M_obj       = combos{idx, 4};
    prob_name   = func2str(prob_handle);

    algo_spec = [{algo_handle}, ivf_params];

    fprintf('\n--- [%d/%d] %s on %s (M=%d) ---\n', ci, length(my_combos), algo_name, prob_name, M_obj);

    target_folder = fullfile(data_dir, algo_name);
    runs_needed = [];
    for r = 1:NUM_RUNS
        pattern = sprintf('%s_%s_M%d_*_%d.mat', algo_name, prob_name, M_obj, r);
        if isempty(dir(fullfile(target_folder, pattern)))
            runs_needed(end+1) = r; %#ok<AGROW>
        end
    end

    if isempty(runs_needed)
        fprintf('  Already complete (%d runs). Skipping.\n', NUM_RUNS);
        continue;
    end

    fprintf('  Running %d missing runs: [%d..%d]\n', length(runs_needed), runs_needed(1), runs_needed(end));

    for ri = 1:length(runs_needed)
        run_idx = runs_needed(ri);
        try
            platemo('algorithm', algo_spec, ...
                    'problem', prob_handle, ...
                    'M', M_obj, ...
                    'maxFE', MAX_FE, ...
                    'save', N_SAVE, ...
                    'run', run_idx, ...
                    'metName', {'IGD', 'HV'});
            fprintf('  ok %s/%s run %d\n', algo_name, prob_name, run_idx);
        catch ME
            fprintf('  FAIL %s/%s run %d: %s\n', algo_name, prob_name, run_idx, ME.message);
        end
    end
end

elapsed = toc(t_start);
fprintf('\n=== Batch 3 Runner %d complete in %.1f min ===\n', runner_id, elapsed/60);
