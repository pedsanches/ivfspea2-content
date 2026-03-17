% test_ablation_v2_dtlz4.m
% Quick test on DTLZ4 (M=3) - one of the failure cases - to ensure
% all variants handle tri-objective correctly.

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');

addpath(genpath(PLATEMO_DIR));
addpath(fullfile(PROJECT_ROOT, 'src', 'matlab', 'ivf_spea2'));

maxFE = 10000;
N_pop = 100;

C_val = 0.11; R_val = 0.1; M_val = 0; V_val = 0;
Cycles_val = 3; S_val = 1; N_Offspring_val = 1;
EARN_val = 0; N_Obj_Limit_val = 0;

variants = {
    'IVFSPEA2 (baseline)',    @IVFSPEA2;
    'V1 (dissimilar father)', @IVFSPEA2_V1_DISSIM;
    'V2 (collective crit.)',  @IVFSPEA2_V2_COLLECTIVE;
    'V3 (eta_c = 10)',        @IVFSPEA2_V3_ETA10;
    'V4 (adaptive trigger)',  @IVFSPEA2_V4_ADAPTIVE;
    'V5 (post-SBX mutation)', @IVFSPEA2_V5_MUTATION;
};

fprintf('=== SMOKE TEST: DTLZ4 (M=3) ===\n\n');

all_ok = true;
for v = 1:size(variants, 1)
    name = variants{v, 1};
    algo = variants{v, 2};
    fprintf('[%d/%d] %s on DTLZ4(M=3) ... ', v, size(variants, 1), name);
    try
        tic;
        platemo('algorithm', {algo, C_val, R_val, M_val, V_val, ...
                              Cycles_val, S_val, N_Offspring_val, ...
                              EARN_val, N_Obj_Limit_val}, ...
                'problem', @DTLZ4, 'N', N_pop, 'M', 3, ...
                'maxFE', maxFE, 'save', 0, 'run', 1);
        fprintf('OK (%.1f sec)\n', toc);
    catch ME
        fprintf('FAILED: %s (line %d in %s)\n', ME.message, ME.stack(1).line, ME.stack(1).name);
        all_ok = false;
    end
end

fprintf('\n');
if all_ok
    fprintf('All variants OK on DTLZ4 (M=3)!\n');
else
    fprintf('Some variants FAILED on DTLZ4.\n');
end

% Also test WFG2 (M=3) - disconnected front
fprintf('\n=== SMOKE TEST: WFG2 (M=3) ===\n\n');
for v = 1:size(variants, 1)
    name = variants{v, 1};
    algo = variants{v, 2};
    fprintf('[%d/%d] %s on WFG2(M=3) ... ', v, size(variants, 1), name);
    try
        tic;
        platemo('algorithm', {algo, C_val, R_val, M_val, V_val, ...
                              Cycles_val, S_val, N_Offspring_val, ...
                              EARN_val, N_Obj_Limit_val}, ...
                'problem', @WFG2, 'N', N_pop, 'M', 3, ...
                'maxFE', maxFE, 'save', 0, 'run', 1);
        fprintf('OK (%.1f sec)\n', toc);
    catch ME
        fprintf('FAILED: %s (line %d in %s)\n', ME.message, ME.stack(1).line, ME.stack(1).name);
        all_ok = false;
    end
end

fprintf('\n');
if all_ok
    fprintf('All variants OK!\n');
else
    fprintf('Some variants FAILED. Fix before running ablation.\n');
end

exit;
