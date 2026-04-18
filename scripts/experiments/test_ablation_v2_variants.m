% test_ablation_v2_variants.m
% =========================================================================
% Quick smoke test: 1 run of each V2 ablation variant on ZDT1 (M=2)
% with reduced maxFE to verify execution without errors.
% =========================================================================

PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
PLATEMO_DIR  = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');

addpath(genpath(PLATEMO_DIR));
addpath(fullfile(PROJECT_ROOT, 'src', 'matlab', 'ivf_spea2'));

maxFE = 10000;  % Small budget for quick test
N_pop = 100;

% IVF params (AR mode)
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

fprintf('=== SMOKE TEST: IVF/SPEA2 V2 Ablation Variants ===\n');
fprintf('Problem: ZDT1 (M=2) | maxFE: %d | N: %d\n\n', maxFE, N_pop);

results = {};
all_ok = true;

for v = 1:size(variants, 1)
    name = variants{v, 1};
    algo = variants{v, 2};
    fprintf('[%d/%d] Testing %s ... ', v, size(variants, 1), name);

    try
        tic;
        platemo('algorithm', {algo, C_val, R_val, M_val, V_val, ...
                              Cycles_val, S_val, N_Offspring_val, ...
                              EARN_val, N_Obj_Limit_val}, ...
                'problem', @ZDT1, ...
                'N', N_pop, ...
                'M', 2, ...
                'maxFE', maxFE, ...
                'save', 0, ...
                'run', 1);
        elapsed = toc;
        fprintf('OK (%.1f sec)\n', elapsed);
        results{end+1} = sprintf('  %-30s  OK  (%.1f sec)', name, elapsed);
    catch ME
        elapsed = toc;
        fprintf('FAILED!\n');
        fprintf('  Error: %s\n', ME.message);
        fprintf('  In: %s (line %d)\n', ME.stack(1).name, ME.stack(1).line);
        results{end+1} = sprintf('  %-30s  FAILED: %s', name, ME.message);
        all_ok = false;
    end
end

fprintf('\n=== SUMMARY ===\n');
for i = 1:length(results)
    fprintf('%s\n', results{i});
end

if all_ok
    fprintf('\nAll %d variants passed smoke test!\n', size(variants, 1));
else
    fprintf('\nSome variants FAILED. Check errors above.\n');
end

exit;
