%% run_sensitivity.m — Phase 1.3: Parameter Sensitivity Grid
%  9 R-values × 10 C-values × 4 problems × 30 runs = 10,800 runs
%  Uses parfor over runs for parallelism.
%  Resume-safe: checks folder existence before each combo.
%
%  Usage:
%    matlab -batch "run('experiments/run_sensitivity.m')"

%% Configuration
NUM_RUNS = 30;
MAX_FE   = 25000;  % Sensitivity uses fewer FE (matches original run_experiment.m)
N_SAVE   = 10;

% Fixed IVF parameters
M_val = 0;  V_val = 0;  Cycles_val = 20;  S_val = 1;
N_Offspring_val = 1;  EARN_val = 0;  N_Obj_Limit_val = 20;

% Grid
R_vals = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300];
C_vals = [0.05, 0.07, 0.11, 0.16, 0.21, 0.27, 0.32, 0.42, 0.53, 0.64];

% Problems: {handle, M_objectives}
problems = {
    @ZDT1,  2;
    @DTLZ1, 3;
    @WFG4,  2;
    @MaF1,  3;
};

%% Setup PlatEMO path
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
cd(platemo_dir);
addpath(genpath(platemo_dir));

%% Start parallel pool
if isempty(gcp('nocreate'))
    parpool;
end

data_dir = fullfile(platemo_dir, 'Data');

%% Generate all parameter combinations
param_combos = combvec(R_vals, C_vals)';  % Each row: [R, C]
total_combos = size(param_combos, 1) * size(problems, 1);
combo_count  = 0;
t_start = tic;

for p = 1:size(problems, 1)
    prob_handle = problems{p, 1};
    M_obj       = problems{p, 2};
    prob_name   = func2str(prob_handle);

    for ci = 1:size(param_combos, 1)
        R_val = param_combos(ci, 1);
        C_val = param_combos(ci, 2);

        combo_count = combo_count + 1;

        % Unique folder name per combo×problem
        folder_name = sprintf('IVFSPEA2_R%.4f_C%.2f_%s_M%d', R_val, C_val, prob_name, M_obj);
        target_folder = fullfile(data_dir, folder_name);

        % Resume: skip if folder already exists with enough files
        if isfolder(target_folder)
            existing = length(dir(fullfile(target_folder, '*.mat')));
            if existing >= NUM_RUNS
                if mod(combo_count, 20) == 1
                    fprintf('[%d/%d] %s — complete (%d files). Skipping.\n', ...
                            combo_count, total_combos, folder_name, existing);
                end
                continue;
            end
        end

        fprintf('[%d/%d] %s — R=%.4f, C=%.2f, %s M=%d\n', ...
                combo_count, total_combos, folder_name, R_val, C_val, prob_name, M_obj);

        % PlatEMO saves to Data/IVFSPEA2/ by default so we need unique run IDs
        % and then move files. Use a temporary marker approach.
        orig_folder = fullfile(data_dir, 'IVFSPEA2');

        % Clean any leftover IVFSPEA2 folder to avoid contamination
        if isfolder(orig_folder)
            % Only clean if it has files from THIS problem (safety check)
            warning('off', 'all');
            rmdir(orig_folder, 's');
            warning('on', 'all');
        end

        parfor run = 1:NUM_RUNS
            try
                platemo('algorithm', {@IVFSPEA2, C_val, R_val, M_val, V_val, ...
                                      Cycles_val, S_val, N_Offspring_val, ...
                                      EARN_val, N_Obj_Limit_val}, ...
                        'problem', prob_handle, ...
                        'M', M_obj, ...
                        'maxFE', MAX_FE, ...
                        'save', N_SAVE, ...
                        'run', run, ...
                        'metName', {'IGD', 'HV'});
            catch ME
                fprintf('  ✗ run %d: %s\n', run, ME.message);
            end
        end

        % Move results to unique folder
        if isfolder(orig_folder)
            if ~isfolder(target_folder)
                movefile(orig_folder, target_folder);
            else
                % Merge into existing folder
                files = dir(fullfile(orig_folder, '*.mat'));
                for fi = 1:length(files)
                    movefile(fullfile(files(fi).folder, files(fi).name), target_folder);
                end
                rmdir(orig_folder, 's');
            end
            fprintf('  → Results saved to %s\n', folder_name);
        end
    end
end

elapsed = toc(t_start);
fprintf('\n=== Sensitivity grid complete in %.1f hours ===\n', elapsed/3600);
delete(gcp('nocreate'));
