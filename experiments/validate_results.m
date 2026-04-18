%% validate_results.m — Data Integrity Checker
%  Validates experiment output completeness and integrity.
%  Reports missing runs and file count mismatches.
%
%  Usage:
%    matlab -batch "run('experiments/validate_results.m')"

%% Setup
platemo_dir = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'matlab', 'lib', 'PlatEMO');
data_dir    = fullfile(platemo_dir, 'Data');

fprintf('=== IVF-SPEA2 Experiment Validation ===\n');
fprintf('Data directory: %s\n\n', data_dir);

total_issues = 0;

%% Phase 1.1: Ablation Study
fprintf('--- Phase 1.1: Ablation Study (4 × 5 × 60 = 1200 expected) ---\n');
abl_algos = {'IVFSPEA2', 'IVFSPEA2ABL1C', 'IVFSPEA2ABL4C', 'IVFSPEA2ABLDOM'};
abl_probs = {'ZDT1', 'DTLZ1', 'WFG4', 'MaF1', 'MaF4'};
abl_M     = [2, 3, 2, 3, 3];
EXPECTED_ABL = 60;

for ai = 1:length(abl_algos)
    algo = abl_algos{ai};
    folder = fullfile(data_dir, algo);
    for pi = 1:length(abl_probs)
        prob = abl_probs{pi};
        M = abl_M(pi);
        pattern = sprintf('%s_%s_M%d_*_*.mat', algo, prob, M);
        if isfolder(folder)
            count = length(dir(fullfile(folder, pattern)));
        else
            count = 0;
        end
        if count < EXPECTED_ABL
            fprintf('  ✗ %s/%s (M=%d): %d/%d\n', algo, prob, M, count, EXPECTED_ABL);
            total_issues = total_issues + 1;
        else
            fprintf('  ✓ %s/%s (M=%d): %d/%d\n', algo, prob, M, count, EXPECTED_ABL);
        end
    end
end

%% Phase 1.4: RWMOP9
fprintf('\n--- Phase 1.4: RWMOP9 (9 × 60 = 540 expected) ---\n');
rwmop_algos = {'SPEA2','NSGAII','NSGAIII','MOEAD','MFOSPEA2','SPEA2SDE','AGEMOEAII','ARMOEA','IVFSPEA2'};
EXPECTED_RW = 60;

for ai = 1:length(rwmop_algos)
    algo = rwmop_algos{ai};
    folder = fullfile(data_dir, algo);
    pattern = sprintf('%s_RWMOP9_M2_*.mat', algo);
    if isfolder(folder)
        count = length(dir(fullfile(folder, pattern)));
    else
        count = 0;
    end
    if count < EXPECTED_RW
        fprintf('  ✗ %s: %d/%d\n', algo, count, EXPECTED_RW);
        total_issues = total_issues + 1;
    else
        fprintf('  ✓ %s: %d/%d\n', algo, count, EXPECTED_RW);
    end
end

%% Phase 1.2: Modern Baselines
fprintf('\n--- Phase 1.2: Modern Baselines (2 × 51 × 60 = 6120 expected) ---\n');
bl_algos = {'AGEMOEAII', 'ARMOEA'};
EXPECTED_BL = 60;
bl_count = 0;  bl_missing = 0;

for ai = 1:length(bl_algos)
    algo = bl_algos{ai};
    folder = fullfile(data_dir, algo);
    if isfolder(folder)
        files = dir(fullfile(folder, '*.mat'));
        count = length(files);
    else
        count = 0;
    end
    expected_total = 51 * EXPECTED_BL;
    bl_count = bl_count + count;
    if count < expected_total
        fprintf('  ✗ %s: %d/%d files\n', algo, count, expected_total);
        bl_missing = bl_missing + (expected_total - count);
        total_issues = total_issues + 1;
    else
        fprintf('  ✓ %s: %d/%d files\n', algo, count, expected_total);
    end
end

%% Phase 1.3: Sensitivity
fprintf('\n--- Phase 1.3: Sensitivity Grid (90 × 4 × 30 = 10800 expected) ---\n');
sens_dirs = dir(fullfile(data_dir, 'IVFSPEA2_R*_C*_*'));
sens_dirs = sens_dirs([sens_dirs.isdir]);
sens_count = 0;  sens_complete = 0;  sens_incomplete = 0;
EXPECTED_SENS = 30;

for si = 1:length(sens_dirs)
    files = dir(fullfile(sens_dirs(si).folder, sens_dirs(si).name, '*.mat'));
    count = length(files);
    sens_count = sens_count + count;
    if count >= EXPECTED_SENS
        sens_complete = sens_complete + 1;
    else
        sens_incomplete = sens_incomplete + 1;
    end
end

expected_combos = 90 * 4;  % 9R × 10C × 4 problems
fprintf('  Combos found: %d/%d\n', length(sens_dirs), expected_combos);
fprintf('  Complete: %d | Incomplete: %d\n', sens_complete, sens_incomplete);
fprintf('  Total files: %d/%d\n', sens_count, expected_combos * EXPECTED_SENS);
if sens_incomplete > 0 || length(sens_dirs) < expected_combos
    total_issues = total_issues + 1;
end

%% Summary
fprintf('\n============================================\n');
if total_issues == 0
    fprintf('✓ ALL PHASES COMPLETE — no issues found.\n');
else
    fprintf('✗ %d issue(s) found. Review above for details.\n', total_issues);
end
fprintf('============================================\n');
