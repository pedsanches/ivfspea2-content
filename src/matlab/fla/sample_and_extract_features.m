%% sample_and_extract_features.m
%  Fitness Landscape Analysis — Sampling + Feature Extraction (v2)
%  PPSN 2026 paper: landscape-aware prediction of IVF operator effectiveness
%
%  Changes from v1:
%    - M-agnostic: all features aggregate across ALL objectives (not just f1/f2)
%    - Multi-seed: runs N_SEEDS independent samples, exports mean and CV
%    - Added n_nondominated to contextualize Group C reliability
%    - Feature names reflect aggregation (e.g., skewness_mean, autocorr_mean)
%
%  Exports:
%    data/processed/landscape_features.csv      — mean features across seeds
%    data/processed/landscape_features_cv.csv   — CV of features across seeds
%
%  Usage:
%    addpath(genpath('src/matlab/lib/PlatEMO'));
%    run('src/matlab/fla/sample_and_extract_features.m');

%% ---- Configuration ----
N_LHS       = 2000;   % Latin Hypercube sample size (increased per Mersmann et al. 2011)
N_WALK      = 1000;   % Random walk steps (increased per Munoz et al. 2015)
STEP_SIZE   = 0.01;   % Random walk step size (fraction of range per dimension)
SEEDS       = [42, 123, 456, 789, 1024];  % 5 independent seeds
N_SEEDS     = length(SEEDS);
DBSCAN_K    = 5;      % k for DBSCAN minPts and k-NN graph
PROJECT_ROOT = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
OUTPUT_MEAN = fullfile(PROJECT_ROOT, 'data', 'processed', 'landscape_features.csv');
OUTPUT_CV   = fullfile(PROJECT_ROOT, 'data', 'processed', 'landscape_features_cv.csv');

%% ---- Instance Registry ----
% Exactly the 51 synthetic instances from the Memetic Computing study
% Format: {ProblemClass, M, D, InstanceName}
instances = { ...
    @ZDT1, 2, 30, 'ZDT1_M2'; ...
    @ZDT2, 2, 30, 'ZDT2_M2'; ...
    @ZDT3, 2, 30, 'ZDT3_M2'; ...
    @ZDT4, 2, 10, 'ZDT4_M2'; ...
    @ZDT6, 2, 10, 'ZDT6_M2'; ...
    @DTLZ1, 2,  6, 'DTLZ1_M2'; ...
    @DTLZ1, 3,  7, 'DTLZ1_M3'; ...
    @DTLZ2, 2, 11, 'DTLZ2_M2'; ...
    @DTLZ2, 3, 12, 'DTLZ2_M3'; ...
    @DTLZ3, 2, 11, 'DTLZ3_M2'; ...
    @DTLZ3, 3, 12, 'DTLZ3_M3'; ...
    @DTLZ4, 2, 11, 'DTLZ4_M2'; ...
    @DTLZ4, 3, 12, 'DTLZ4_M3'; ...
    @DTLZ5, 2, 11, 'DTLZ5_M2'; ...
    @DTLZ5, 3, 12, 'DTLZ5_M3'; ...
    @DTLZ6, 2, 11, 'DTLZ6_M2'; ...
    @DTLZ6, 3, 12, 'DTLZ6_M3'; ...
    @DTLZ7, 2, 21, 'DTLZ7_M2'; ...
    @DTLZ7, 3, 22, 'DTLZ7_M3'; ...
    @WFG1, 2, 11, 'WFG1_M2'; ...
    @WFG1, 3, 12, 'WFG1_M3'; ...
    @WFG2, 2, 11, 'WFG2_M2'; ...
    @WFG2, 3, 12, 'WFG2_M3'; ...
    @WFG3, 2, 11, 'WFG3_M2'; ...
    @WFG3, 3, 12, 'WFG3_M3'; ...
    @WFG4, 2, 11, 'WFG4_M2'; ...
    @WFG4, 3, 12, 'WFG4_M3'; ...
    @WFG5, 2, 11, 'WFG5_M2'; ...
    @WFG5, 3, 12, 'WFG5_M3'; ...
    @WFG6, 2, 11, 'WFG6_M2'; ...
    @WFG6, 3, 12, 'WFG6_M3'; ...
    @WFG7, 2, 11, 'WFG7_M2'; ...
    @WFG7, 3, 12, 'WFG7_M3'; ...
    @WFG8, 2, 11, 'WFG8_M2'; ...
    @WFG8, 3, 12, 'WFG8_M3'; ...
    @WFG9, 2, 11, 'WFG9_M2'; ...
    @WFG9, 3, 12, 'WFG9_M3'; ...
    @MaF1, 2, 11, 'MaF1_M2'; ...
    @MaF1, 3, 12, 'MaF1_M3'; ...
    @MaF2, 2, 11, 'MaF2_M2'; ...
    @MaF2, 3, 12, 'MaF2_M3'; ...
    @MaF3, 2, 11, 'MaF3_M2'; ...
    @MaF3, 3, 12, 'MaF3_M3'; ...
    @MaF4, 2, 11, 'MaF4_M2'; ...
    @MaF4, 3, 12, 'MaF4_M3'; ...
    @MaF5, 2, 11, 'MaF5_M2'; ...
    @MaF5, 3, 12, 'MaF5_M3'; ...
    @MaF6, 2, 11, 'MaF6_M2'; ...
    @MaF6, 3, 12, 'MaF6_M3'; ...
    @MaF7, 2, 21, 'MaF7_M2'; ...
    @MaF7, 3, 22, 'MaF7_M3'; ...
};

n_instances = size(instances, 1);

%% ---- Feature Names (M-agnostic) ----
% Group A: Objective distribution (6 features)
%   - corr_obj_mean:  mean of all pairwise Spearman correlations
%   - conflict_degree: proportion of conflicting pairs (already M-agnostic)
%   - skewness_mean:  mean skewness across all M objectives
%   - kurtosis_mean:  mean kurtosis across all M objectives
%   - cv_mean:        mean coefficient of variation across objectives
%   - cv_max:         max coefficient of variation across objectives
%
% Group B: Dominance (3 features)
%   - prop_nondominated, dom_depth_mean, dom_depth_std
%
% Group C: Front connectivity (6 features)
%   - n_nondominated:     count of non-dominated points (reliability context)
%   - front_n_clusters:   DBSCAN cluster count on ND front
%   - front_connectivity: fraction of ND front in largest k-NN component
%   - front_diameter:     longest shortest path in k-NN graph
%   - front_gap_ratio:    largest gap / span in ND front
%   - front_curvature_var: curvature variance (2D) or local PCA var (M>2)
%
% Group D: Local landscape (5 features)
%   - autocorr_mean: mean lag-1 autocorrelation across objectives
%   - autocorr_min:  min lag-1 autocorrelation (most rugged direction)
%   - info_content:  Tchebycheff-based information content (Munoz 2015)
%   - neutrality_ratio: fraction of walk steps with negligible change
%   - fdc_mean:      mean fitness-distance correlation across objectives
%
% Group E: Structural (2 features)
%   - n_obj, n_var

feature_names = { ...
    'corr_obj_mean', 'conflict_degree', ...
    'skewness_mean', 'kurtosis_mean', 'cv_mean', 'cv_max', ...
    'prop_nondominated', 'dom_depth_mean', 'dom_depth_std', ...
    'n_nondominated', 'front_n_clusters', 'front_connectivity', ...
    'front_diameter', 'front_gap_ratio', 'front_curvature_var', ...
    'autocorr_mean', 'autocorr_min', 'info_content', ...
    'neutrality_ratio', 'fdc_mean', ...
    'n_obj', 'n_var' ...
};
n_features = length(feature_names);

fprintf('=== FLA Feature Extraction v2: %d instances x %d seeds x %d features ===\n', ...
    n_instances, N_SEEDS, n_features);

%% ---- Main Loop: multi-seed ----
% 3D array: instances x features x seeds
all_results = zeros(n_instances, n_features, N_SEEDS);
instance_names = cell(n_instances, 1);

total_timer = tic;

for seed_idx = 1:N_SEEDS
    seed = SEEDS(seed_idx);
    rng(seed);
    fprintf('\n--- Seed %d/%d (rng=%d) ---\n', seed_idx, N_SEEDS, seed);

    for idx = 1:n_instances
        prob_class = instances{idx, 1};
        M = instances{idx, 2};
        D = instances{idx, 3};
        name = instances{idx, 4};
        instance_names{idx} = name;

        if seed_idx == 1
            fprintf('[%2d/%d] %s (M=%d, D=%d) ... ', idx, n_instances, name, M, D);
        else
            fprintf('[%2d/%d] %s ... ', idx, n_instances, name);
        end
        inst_timer = tic;

        % Instantiate problem
        Problem = prob_class('M', M, 'D', D);
        xl = Problem.lower;
        xu = Problem.upper;

        % ---- Step 1: Latin Hypercube Sampling ----
        X_lhs = lhs_sample(N_LHS, D, xl, xu);
        F_lhs = Problem.CalObj(X_lhs);

        % ---- Step 2: Adaptive Random Walk ----
        [X_walk, F_walk] = random_walk(Problem, N_WALK, STEP_SIZE, xl, xu, D);

        % ---- Step 3: Compute Features (M-agnostic) ----
        feat = compute_all_features(X_lhs, F_lhs, X_walk, F_walk, M, D, ...
                                     N_LHS, DBSCAN_K);

        all_results(idx, :, seed_idx) = feat;
        fprintf('done (%.1fs)\n', toc(inst_timer));
    end
end

%% ---- Aggregate across seeds ----
results_mean = mean(all_results, 3);
results_std  = std(all_results, 0, 3);

% Coefficient of variation: CV = std/|mean|, handle near-zero means
results_cv = zeros(size(results_mean));
for i = 1:n_instances
    for j = 1:n_features
        mu = results_mean(i, j);
        sd = results_std(i, j);
        if abs(mu) > 1e-12
            results_cv(i, j) = sd / abs(mu);
        elseif sd > 1e-12
            results_cv(i, j) = Inf;  % mean~0 but nonzero variance
        else
            results_cv(i, j) = 0;    % both zero = perfectly stable
        end
    end
end

%% ---- Export CSVs ----
% Mean features
T_mean = array2table(results_mean, 'VariableNames', feature_names);
T_mean = addvars(T_mean, instance_names, 'Before', 1, 'NewVariableNames', {'instance'});
writetable(T_mean, OUTPUT_MEAN);

% CV (stability) features
T_cv = array2table(results_cv, 'VariableNames', feature_names);
T_cv = addvars(T_cv, instance_names, 'Before', 1, 'NewVariableNames', {'instance'});
writetable(T_cv, OUTPUT_CV);

%% ---- Summary ----
fprintf('\n=== SUMMARY ===\n');
fprintf('Instances: %d | Features: %d | Seeds: %d\n', n_instances, n_features, N_SEEDS);
fprintf('Total time: %.1f seconds\n', toc(total_timer));
fprintf('\nFeature stability (mean CV across instances):\n');
for j = 1:n_features
    cv_vals = results_cv(:, j);
    cv_finite = cv_vals(isfinite(cv_vals));
    if ~isempty(cv_finite)
        fprintf('  %-22s  mean_CV=%.4f  max_CV=%.4f\n', ...
            feature_names{j}, mean(cv_finite), max(cv_finite));
    else
        fprintf('  %-22s  mean_CV=Inf (unstable)\n', feature_names{j});
    end
end
fprintf('\nExported mean features to: %s\n', OUTPUT_MEAN);
fprintf('Exported CV (stability) to: %s\n', OUTPUT_CV);


%% ========================================================================
%  FEATURE COMPUTATION (M-AGNOSTIC)
%  ========================================================================

function feat = compute_all_features(X_lhs, F_lhs, X_walk, F_walk, M, D, ...
                                      N_LHS, DBSCAN_K)
    % Compute all 22 features for one instance, aggregating across all M
    % objectives where applicable.
    feat = zeros(1, 22);
    fi = 0;

    % === Group A: Objective Distribution (6 features) ===

    % A1: Mean pairwise Spearman correlation across all objective pairs
    if M == 2
        corr_val = corr(F_lhs(:,1), F_lhs(:,2), 'Type', 'Spearman');
    else
        % All (M choose 2) pairwise correlations
        corr_vals = [];
        for a = 1:M
            for b = (a+1):M
                corr_vals = [corr_vals; corr(F_lhs(:,a), F_lhs(:,b), 'Type', 'Spearman')]; %#ok<AGROW>
            end
        end
        corr_val = mean(corr_vals);
    end
    fi=fi+1; feat(fi) = corr_val;

    % A2: Conflict degree (already M-agnostic)
    fi=fi+1; feat(fi) = compute_conflict_degree(F_lhs);

    % A3: Mean skewness across all objectives
    sk_vals = zeros(M, 1);
    for m = 1:M
        sk_vals(m) = skewness(F_lhs(:, m));
    end
    fi=fi+1; feat(fi) = mean(sk_vals);

    % A4: Mean kurtosis across all objectives
    ku_vals = zeros(M, 1);
    for m = 1:M
        ku_vals(m) = kurtosis(F_lhs(:, m));
    end
    fi=fi+1; feat(fi) = mean(ku_vals);

    % A5: Mean CV across objectives
    cv_vals = zeros(M, 1);
    for m = 1:M
        cv_vals(m) = std(F_lhs(:, m)) / (abs(mean(F_lhs(:, m))) + 1e-12);
    end
    fi=fi+1; feat(fi) = mean(cv_vals);

    % A6: Max CV across objectives
    fi=fi+1; feat(fi) = max(cv_vals);

    % === Group B: Dominance (3 features) ===
    [nd_mask, dom_depths] = compute_dominance_info(F_lhs);
    fi=fi+1; feat(fi) = sum(nd_mask) / N_LHS;   % prop_nondominated
    fi=fi+1; feat(fi) = mean(dom_depths);         % dom_depth_mean
    fi=fi+1; feat(fi) = std(dom_depths);           % dom_depth_std

    % === Group C: Front Connectivity (6 features) ===
    F_nd = F_lhs(nd_mask, :);
    n_nd = size(F_nd, 1);
    fi=fi+1; feat(fi) = n_nd;  % n_nondominated (reliability context)

    [n_clusters, connectivity, diameter, gap_ratio, curv_var] = ...
        compute_front_connectivity(F_nd, DBSCAN_K);
    fi=fi+1; feat(fi) = n_clusters;
    fi=fi+1; feat(fi) = connectivity;
    fi=fi+1; feat(fi) = diameter;
    fi=fi+1; feat(fi) = gap_ratio;
    fi=fi+1; feat(fi) = curv_var;

    % === Group D: Local Landscape (5 features) ===

    % D1-D2: Autocorrelation lag-1 across ALL objectives
    ac_vals = zeros(M, 1);
    for m = 1:M
        ac_vals(m) = autocorr_lag1(F_walk(:, m));
    end
    fi=fi+1; feat(fi) = mean(ac_vals);  % autocorr_mean
    fi=fi+1; feat(fi) = min(ac_vals);   % autocorr_min (most rugged)

    % D3: Information content (uses Tchebycheff, already M-agnostic)
    fi=fi+1; feat(fi) = compute_information_content(F_walk);

    % D4: Neutrality ratio (already M-agnostic)
    fi=fi+1; feat(fi) = compute_neutrality_ratio(F_walk);

    % D5: Mean FDC across ALL objectives
    fdc_vals = zeros(M, 1);
    for m = 1:M
        fdc_vals(m) = compute_fdc(X_lhs, F_lhs(:, m));
    end
    fi=fi+1; feat(fi) = mean(fdc_vals);

    % === Group E: Structural (2 features) ===
    fi=fi+1; feat(fi) = M;
    fi=fi+1; feat(fi) = D;
end


%% ========================================================================
%  SAMPLING FUNCTIONS
%  ========================================================================

function X = lhs_sample(N, D, xl, xu)
    % Latin Hypercube Sampling in [xl, xu]
    X = zeros(N, D);
    for d = 1:D
        perm = randperm(N);
        X(:, d) = (perm' - rand(N, 1)) / N;
    end
    X = xl + X .* (xu - xl);
end

function [X_walk, F_walk] = random_walk(Problem, N_steps, step_frac, xl, xu, D)
    % Adaptive random walk with dimension-scaled step size.
    % Step size per dimension = step_frac * range_d / sqrt(D)
    % This ensures the Euclidean step magnitude is comparable across dimensions.
    range = xu - xl;
    step = step_frac * range / sqrt(D);

    X_walk = zeros(N_steps, D);
    x = xl + rand(1, D) .* range;
    X_walk(1, :) = x;

    for t = 2:N_steps
        dx = randn(1, D) .* step;
        x_new = x + dx;
        x_new = max(xl, min(xu, x_new));
        X_walk(t, :) = x_new;
        x = x_new;
    end
    F_walk = Problem.CalObj(X_walk);
end


%% ========================================================================
%  GROUP A: OBJECTIVE DISTRIBUTION HELPERS
%  ========================================================================

function conflict = compute_conflict_degree(F)
    % Proportion of sampled pairs where objectives conflict.
    % Works for any number of objectives M.
    N = size(F, 1);
    n_sample = min(N*(N-1)/2, 5000);

    if N < 2
        conflict = 0;
        return;
    end

    idx1 = randi(N, n_sample, 1);
    idx2 = randi(N, n_sample, 1);
    valid = idx1 ~= idx2;
    idx1 = idx1(valid); idx2 = idx2(valid);

    delta = F(idx1, :) - F(idx2, :);
    signs = sign(delta);
    has_pos = any(signs > 0, 2);
    has_neg = any(signs < 0, 2);
    conflict = mean(has_pos & has_neg);
end


%% ========================================================================
%  GROUP B: DOMINANCE HELPERS
%  ========================================================================

function [nd_mask, dom_depths] = compute_dominance_info(F)
    % Compute non-dominated mask and dominance count (R(i) in SPEA2 terms).
    % dom_depths(i) = number of solutions that dominate i.
    % Works for any M.
    N = size(F, 1);
    dom_depths = zeros(N, 1);
    nd_mask = true(N, 1);

    for i = 1:N
        for j = 1:N
            if i == j, continue; end
            if all(F(j,:) <= F(i,:)) && any(F(j,:) < F(i,:))
                nd_mask(i) = false;
                dom_depths(i) = dom_depths(i) + 1;
            end
        end
    end
end


%% ========================================================================
%  GROUP C: FRONT CONNECTIVITY
%  ========================================================================

function [n_clusters, connectivity, diameter, gap_ratio, curv_var] = ...
        compute_front_connectivity(F_nd, k)
    % Front connectivity features computed on the non-dominated set.
    % Works for any M >= 2.
    N = size(F_nd, 1);
    M = size(F_nd, 2);

    if N < 3
        n_clusters = N;
        connectivity = 0;
        diameter = 0;
        gap_ratio = 1;
        curv_var = 0;
        return;
    end

    % Normalize objectives to [0,1]
    F_min = min(F_nd, [], 1);
    F_max = max(F_nd, [], 1);
    F_range = F_max - F_min;
    F_range(F_range < 1e-12) = 1;
    F_norm = (F_nd - F_min) ./ F_range;

    % Pairwise distance matrix
    Dist = pdist2(F_norm, F_norm);

    % ---- DBSCAN clustering ----
    Dist_sorted = sort(Dist, 2);
    k_actual = min(k, N-1);
    knn_dists = Dist_sorted(:, k_actual+1);
    eps = median(knn_dists) * 1.5;

    labels = dbscan_simple(Dist, eps, k_actual);
    n_clusters = max(labels);
    if n_clusters <= 0
        n_clusters = 1;
    end

    % ---- k-NN graph connectivity ----
    adj = false(N, N);
    for i = 1:N
        [~, nn_idx] = sort(Dist(i,:));
        nn_idx = nn_idx(2:min(k_actual+1, N));
        adj(i, nn_idx) = true;
    end
    adj = adj | adj';

    % Connected components via BFS
    [comp_sizes, comp_nodes] = find_components(adj, N);
    connectivity = max(comp_sizes) / N;

    % ---- Graph diameter ----
    [~, largest_comp_id] = max(comp_sizes);
    lc_nodes = comp_nodes{largest_comp_id};
    n_lc = length(lc_nodes);
    if n_lc <= 1
        diameter = 0;
    else
        max_bfs = min(n_lc, 50);
        bfs_sources = lc_nodes(randperm(n_lc, max_bfs));
        max_sp = 0;
        for si = 1:length(bfs_sources)
            sp = bfs_shortest_paths(adj, bfs_sources(si), lc_nodes);
            max_sp = max(max_sp, max(sp));
        end
        diameter = max_sp;
    end

    % ---- Gap ratio ----
    % Unified approach: ratio of largest to median nearest-neighbor distance.
    % This is consistent across any M.
    nn_dists = Dist_sorted(:, 2);  % nearest-neighbor distances
    med_nn = median(nn_dists);
    if med_nn > 1e-12
        gap_ratio = max(nn_dists) / med_nn;
    else
        gap_ratio = 1;
    end

    % ---- Curvature / local dimensionality variance ----
    if M == 2 && N >= 3
        [~, order] = sort(F_norm(:,1));
        F_sorted = F_norm(order, :);
        v1 = F_sorted(2:end-1,:) - F_sorted(1:end-2,:);
        v2 = F_sorted(3:end,:) - F_sorted(2:end-1,:);
        dots = sum(v1 .* v2, 2);
        norms1 = sqrt(sum(v1.^2, 2));
        norms2 = sqrt(sum(v2.^2, 2));
        cos_angles = dots ./ (norms1 .* norms2 + 1e-12);
        cos_angles = max(-1, min(1, cos_angles));
        angles = acos(cos_angles);
        curv_var = var(angles);
    else
        % M>2: local PCA-based dimensionality variance
        curv_var = compute_local_dim_var(F_norm, k_actual);
    end
end

function [comp_sizes, comp_nodes] = find_components(adj, N)
    % Find connected components via BFS
    visited = false(N, 1);
    comp_sizes = [];
    comp_nodes = {};
    comp_id = 0;
    for i = 1:N
        if visited(i), continue; end
        comp_id = comp_id + 1;
        queue = i;
        visited(i) = true;
        nodes = [];
        while ~isempty(queue)
            curr = queue(1); queue(1) = [];
            nodes = [nodes, curr]; %#ok<AGROW>
            neighbors = find(adj(curr,:) & ~visited');
            visited(neighbors) = true;
            queue = [queue, neighbors]; %#ok<AGROW>
        end
        comp_sizes = [comp_sizes, length(nodes)]; %#ok<AGROW>
        comp_nodes{comp_id} = nodes; %#ok<AGROW>
    end
end

function labels = dbscan_simple(Dist, eps, minPts)
    % DBSCAN on precomputed distance matrix
    N = size(Dist, 1);
    labels = zeros(N, 1);
    cluster_id = 0;

    for i = 1:N
        if labels(i) ~= 0, continue; end
        neighbors = find(Dist(i,:) <= eps);
        if length(neighbors) < minPts
            labels(i) = -1;
            continue;
        end
        cluster_id = cluster_id + 1;
        labels(i) = cluster_id;
        seed_set = setdiff(neighbors, i);
        j = 1;
        while j <= length(seed_set)
            q = seed_set(j);
            if labels(q) == -1
                labels(q) = cluster_id;
            end
            if labels(q) ~= 0
                j = j + 1;
                continue;
            end
            labels(q) = cluster_id;
            q_neighbors = find(Dist(q,:) <= eps);
            if length(q_neighbors) >= minPts
                seed_set = union(seed_set, q_neighbors);
            end
            j = j + 1;
        end
    end
end

function sp = bfs_shortest_paths(adj, source, node_set)
    N = size(adj, 1);
    dist = inf(N, 1);
    dist(source) = 0;
    queue = source;
    while ~isempty(queue)
        curr = queue(1); queue(1) = [];
        neighbors = find(adj(curr,:));
        for ni = 1:length(neighbors)
            nb = neighbors(ni);
            if dist(nb) == inf
                dist(nb) = dist(curr) + 1;
                queue = [queue, nb]; %#ok<AGROW>
            end
        end
    end
    sp = dist(node_set);
    sp(isinf(sp)) = 0;
end

function ldv = compute_local_dim_var(F_norm, k)
    % Variance of local dimensionality (first singular value ratio).
    % Proxy for curvature heterogeneity in M>2 objective space.
    N = size(F_norm, 1);
    k_actual = min(k, N-1);
    Dist = pdist2(F_norm, F_norm);
    local_dims = zeros(N, 1);

    for i = 1:N
        [~, nn_idx] = sort(Dist(i,:));
        nn_idx = nn_idx(2:k_actual+1);
        local_data = F_norm(nn_idx, :) - mean(F_norm(nn_idx, :), 1);
        if size(local_data, 1) < 2
            local_dims(i) = 0;
            continue;
        end
        [~, S, ~] = svd(local_data, 'econ');
        s = diag(S);
        if sum(s) > 1e-12
            local_dims(i) = s(1) / sum(s);
        end
    end
    ldv = var(local_dims);
end


%% ========================================================================
%  GROUP D: LOCAL LANDSCAPE HELPERS
%  ========================================================================

function ac = autocorr_lag1(f)
    % Lag-1 autocorrelation of a sequence
    N = length(f);
    if N < 3
        ac = 0;
        return;
    end
    f_mean = mean(f);
    f_centered = f - f_mean;
    num = sum(f_centered(1:end-1) .* f_centered(2:end));
    den = sum(f_centered.^2);
    if abs(den) < 1e-12
        ac = 0;
    else
        ac = num / den;
    end
end

function ic = compute_information_content(F_walk)
    % Information content (Munoz et al. 2015).
    % Uses Tchebycheff scalarization (max of normalized objectives).
    % Works for any M.
    N = size(F_walk, 1);
    if N < 3
        ic = 0;
        return;
    end

    % Normalize using LHS-range would be better, but walk range is practical
    F_min = min(F_walk, [], 1);
    F_range = max(F_walk, [], 1) - F_min;
    F_range(F_range < 1e-12) = 1;
    F_norm = (F_walk - F_min) ./ F_range;
    f_agg = max(F_norm, [], 2);  % Tchebycheff

    diffs = diff(f_agg);
    eps_threshold = 1e-6 * std(f_agg);
    signs = zeros(length(diffs), 1);
    signs(diffs > eps_threshold) = 1;
    signs(diffs < -eps_threshold) = -1;

    transitions = [signs(1:end-1), signs(2:end)];
    unique_trans = unique(transitions, 'rows');
    n_trans = size(transitions, 1);
    probs = zeros(size(unique_trans, 1), 1);
    for t = 1:size(unique_trans, 1)
        probs(t) = sum(all(transitions == unique_trans(t,:), 2)) / n_trans;
    end
    probs = probs(probs > 0);
    ic = -sum(probs .* log2(probs));
end

function nr = compute_neutrality_ratio(F_walk)
    % Fraction of walk steps with negligible change across ALL objectives
    N = size(F_walk, 1);
    if N < 2
        nr = 0;
        return;
    end
    F_range = max(F_walk, [], 1) - min(F_walk, [], 1);
    F_range(F_range < 1e-12) = 1;
    diffs = abs(diff(F_walk)) ./ F_range;
    max_change = max(diffs, [], 2);
    threshold = 1e-4;
    nr = mean(max_change < threshold);
end

function fdc_val = compute_fdc(X, f)
    % Fitness-Distance Correlation (Jones & Forrest 1995).
    % Spearman correlation between fitness and distance to the best solution.
    [~, best_idx] = min(f);
    x_best = X(best_idx, :);
    dists = sqrt(sum((X - x_best).^2, 2));
    fdc_val = corr(f, dists, 'Type', 'Spearman');
end
