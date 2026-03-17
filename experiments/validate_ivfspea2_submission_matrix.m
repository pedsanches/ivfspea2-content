%% validate_ivfspea2_submission_matrix.m
% Validates IVFSPEA2 completion matrix for submission rerun protocol.
%
% Usage:
%   matlab -batch "run('experiments/validate_ivfspea2_submission_matrix.m')"

%% Configuration
NUM_RUNS = 100;
RUN_BASE = 2001; % Dedicated range for submission rerun (2001..2100)
SUBMISSION_TAG = 'SUB20260218';
algo_name = 'IVFSPEA2';

problems_M2 = {
    @ZDT1, 2, 30;   @ZDT2, 2, 30;   @ZDT3, 2, 30;   @ZDT4, 2, 10;   @ZDT6, 2, 10;
    @DTLZ1, 2, 6;   @DTLZ2, 2, 11;  @DTLZ3, 2, 11;  @DTLZ4, 2, 11;
    @DTLZ5, 2, 11;  @DTLZ6, 2, 11;  @DTLZ7, 2, 21;
    @WFG1, 2, 11;   @WFG2, 2, 11;   @WFG3, 2, 11;   @WFG4, 2, 11;
    @WFG5, 2, 11;   @WFG6, 2, 11;   @WFG7, 2, 11;   @WFG8, 2, 11;   @WFG9, 2, 11;
    @MaF1, 2, 11;   @MaF2, 2, 11;   @MaF3, 2, 11;   @MaF4, 2, 11;
    @MaF5, 2, 11;   @MaF6, 2, 11;   @MaF7, 2, 21;
};

problems_M3 = {
    @DTLZ1, 3, 7;   @DTLZ2, 3, 12;  @DTLZ3, 3, 12;  @DTLZ4, 3, 12;
    @DTLZ5, 3, 12;  @DTLZ6, 3, 12;  @DTLZ7, 3, 22;
    @WFG1, 3, 12;   @WFG2, 3, 12;   @WFG3, 3, 12;   @WFG4, 3, 12;
    @WFG5, 3, 12;   @WFG6, 3, 12;   @WFG7, 3, 12;   @WFG8, 3, 12;   @WFG9, 3, 12;
    @MaF1, 3, 12;   @MaF2, 3, 12;   @MaF3, 3, 12;   @MaF4, 3, 12;
    @MaF5, 3, 12;   @MaF6, 3, 12;   @MaF7, 3, 22;
};

problem_rwmop9 = {@RWMOP9, 2, 4};
all_problems = [problems_M2; problems_M3; problem_rwmop9];

%% Setup
project_root = fullfile(fileparts(mfilename('fullpath')), '..');
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
data_dir     = fullfile(platemo_dir, 'Data', algo_name);
results_dir  = fullfile(project_root, 'results');
if ~isfolder(results_dir), mkdir(results_dir); end

fprintf('=== Validate IVFSPEA2 Submission Matrix ===\n');
fprintf('Data dir: %s\n\n', data_dir);
fprintf('Submission tag: %s\n', SUBMISSION_TAG);
fprintf('Run range considered: %d..%d\n\n', RUN_BASE, RUN_BASE + NUM_RUNS - 1);

out_csv = fullfile(results_dir, sprintf('ivfspea2_submission_matrix_status_%s.csv', SUBMISSION_TAG));
fid = fopen(out_csv, 'w');
fprintf(fid, 'Tag,Problem,M,D,RunBase,ExpectedStart,ExpectedEnd,Found,Expected,FoundRuns,MissingRuns,Status\n');

issues = 0;
for p = 1:size(all_problems,1)
    prob_name = func2str(all_problems{p,1});
    M_obj     = all_problems{p,2};
    D_vars    = all_problems{p,3};

    found_runs = [];
    for r = RUN_BASE:(RUN_BASE + NUM_RUNS - 1)
        fname = sprintf('%s_%s_M%d_D%d_%d.mat', algo_name, prob_name, M_obj, D_vars, r);
        if isfile(fullfile(data_dir, fname))
            found_runs(end+1) = r; %#ok<AGROW>
        end
    end
    found = numel(found_runs);

    all_expected_runs = RUN_BASE:(RUN_BASE + NUM_RUNS - 1);
    missing_runs = setdiff(all_expected_runs, found_runs);

    if isempty(found_runs)
        found_runs_str = '';
    else
        found_runs_str = char(strjoin(string(found_runs), ';'));
    end

    if isempty(missing_runs)
        missing_runs_str = '';
    else
        missing_runs_str = char(strjoin(string(missing_runs), ';'));
    end

    if found >= NUM_RUNS
        status = 'OK';
    elseif found > 0
        status = 'INCOMPLETE';
        issues = issues + 1;
    else
        status = 'MISSING';
        issues = issues + 1;
    end

    fprintf('%-8s M=%d D=%d -> %3d/%3d (%s)\n', prob_name, M_obj, D_vars, found, NUM_RUNS, status);
    fprintf(fid, '%s,%s,%d,%d,%d,%d,%d,%d,%d,"%s","%s",%s\n', ...
        SUBMISSION_TAG, prob_name, M_obj, D_vars, RUN_BASE, RUN_BASE, RUN_BASE + NUM_RUNS - 1, ...
        found, NUM_RUNS, found_runs_str, missing_runs_str, status);
end
fclose(fid);

legacy_csv = fullfile(results_dir, 'ivfspea2_submission_matrix_status.csv');
copyfile(out_csv, legacy_csv);

fprintf('\nStatus CSV: %s\n', out_csv);
fprintf('Legacy alias: %s\n', legacy_csv);
if issues == 0
    fprintf('ALL CONFIGS COMPLETE.\n');
else
    fprintf('%d configs are incomplete/missing.\n', issues);
end
