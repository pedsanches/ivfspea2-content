classdef IVFSPEA2V2TRACE < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVF/SPEA2 v2 trace variant for mechanistic case studies.
    %
    % Parameters 1..7 match IVFSPEA2V2.
    % TraceCapturePopulation --- 0 --- 0: summary trace, 1: store pre/post-IVF populations
    %
    % Per-generation dynamics logging (PPSN 2026):
    %   TraceGenerations: cell array of per-generation snapshots containing
    %   IGD, HV, spread, spacing, mean fitness, archive turnover, IVF
    %   activation status, and function evaluations consumed.

    properties
        TraceCycles = {}
        TraceGenerations = {}
        TraceParameters = struct()
        TraceCapturePopulation = false
    end

    methods
        function main(Algorithm, Problem)
            [C, R, M, V, Cycles, N_Offspring, EARN, TraceCapturePopulation] = ...
                Algorithm.ParameterSet(0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0);

            Algorithm.TraceCycles = {};
            Algorithm.TraceGenerations = {};
            Algorithm.TraceCapturePopulation = logical(TraceCapturePopulation);
            Algorithm.TraceParameters = struct( ...
                'collection_rate', C, ...
                'ivf_activation_ratio', R, ...
                'mother_mutation_fraction', M, ...
                'variable_mutation_fraction', V, ...
                'max_ivf_cycles', Cycles, ...
                'offspring_per_mother', N_Offspring, ...
                'exploration_mode', EARN, ...
                'capture_population', Algorithm.TraceCapturePopulation);

            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = IVFTraceCalFitness(Population.objs);

            % Obtain true Pareto front for IGD computation
            TruePF = Problem.GetOptimum(2000);
            % Compute HV normalization constants from true PF
            HV_fmax = max(TruePF, [], 1);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            % Record generation 0 (initial population)
            Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                Population, Fitness, TruePF, HV_fmax, Problem, ...
                SPEA2_Gen, 0, false, [], 0);
            PrevPopObjs = Population.objs;

            while Algorithm.NotTerminated(Population)
                % IVF phase
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V2_TRACE(Problem, Population, Fitness, Forca, Distancia, ...
                        R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                        EARN, SPEA2_Gen, Algorithm);

                [Fitness, ~, ~] = IVFTraceCalFitness(Population.objs);

                % Record post-IVF snapshot (before GA phase)
                ivf_activated = IVF_Gen_FE > 0;
                n_ivf_cycles = 0;
                if ~isempty(Algorithm.TraceCycles)
                    last_cycle = Algorithm.TraceCycles{end};
                    if last_cycle.generation == SPEA2_Gen
                        n_ivf_cycles = last_cycle.ivf_cycle;
                    end
                end

                % GA phase
                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = IVFTraceEnvironmentalSelection([Population, Offspring], Problem.N);
                end

                % Record end-of-generation snapshot
                turnover = local_turnover(PrevPopObjs, Population.objs);
                Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                    Population, Fitness, TruePF, HV_fmax, Problem, ...
                    SPEA2_Gen, n_ivf_cycles, ivf_activated, turnover, IVF_Gen_FE);
                PrevPopObjs = Population.objs;

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end


%% =================== Per-generation snapshot ===================
function snap = local_snapshot(Population, Fitness, TruePF, HV_fmax, Problem, ...
        gen, n_ivf_cycles, ivf_activated, turnover, ivf_fe)

    PopObj = Population.objs;
    [N, M_obj] = size(PopObj);

    % IGD: mean min distance from true PF to population
    igd_val = mean(min(pdist2(TruePF, PopObj), [], 2));

    % HV: normalize by true PF max * 1.1, reference point = ones
    fmin = min(min(PopObj, [], 1), zeros(1, M_obj));
    NormObj = (PopObj - repmat(fmin, N, 1)) ./ repmat((HV_fmax - fmin) * 1.1, N, 1);
    NormObj(any(NormObj > 1, 2), :) = [];
    if isempty(NormObj)
        hv_val = 0;
    elseif M_obj < 4
        hv_val = local_exact_hv(NormObj, ones(1, M_obj));
    else
        hv_val = local_mc_hv(NormObj, ones(1, M_obj), 1e5);
    end

    % Spread: max pairwise Euclidean distance in objective space
    if N > 1
        D_pairs = pdist(PopObj);
        spread_val = max(D_pairs);
    else
        spread_val = 0;
    end

    % Spacing: std of nearest-neighbor distances
    if N > 1
        D_mat = squareform(D_pairs);
        D_mat(logical(eye(N))) = Inf;
        nn_dists = min(D_mat, [], 2);
        spacing_val = std(nn_dists);
    else
        spacing_val = 0;
    end

    % Mean SPEA2 fitness
    mean_fitness = mean(Fitness);

    % Non-dominated fraction
    nd_mask = Fitness < 1;
    nd_fraction = sum(nd_mask) / N;

    snap = struct( ...
        'generation',       gen, ...
        'fe',               Problem.FE, ...
        'igd',              igd_val, ...
        'hv',               hv_val, ...
        'spread',           spread_val, ...
        'spacing',          spacing_val, ...
        'mean_fitness',     mean_fitness, ...
        'nd_fraction',      nd_fraction, ...
        'ivf_activated',    ivf_activated, ...
        'n_ivf_cycles',     n_ivf_cycles, ...
        'ivf_fe',           ivf_fe, ...
        'turnover',         turnover);
end


%% =================== Archive turnover ===================
function t = local_turnover(PrevObjs, CurrObjs)
    % Fraction of current population members that are new (not in previous)
    if isempty(PrevObjs)
        t = 1.0;
        return;
    end
    N = size(CurrObjs, 1);
    dists = pdist2(CurrObjs, PrevObjs);
    min_dists = min(dists, [], 2);
    % Consider a solution "new" if its nearest previous neighbor is > 0
    t = sum(min_dists > 1e-12) / N;
end


%% =================== Exact HV (M < 4) ===================
function score = local_exact_hv(PopObj, RefPoint)
    M = size(PopObj, 2);
    pl = sortrows(PopObj);
    S = {1, pl};
    for k = 1 : M-1
        S_ = {};
        for i = 1 : size(S, 1)
            Stemp = local_slice(cell2mat(S(i,2)), k, RefPoint);
            for j = 1 : size(Stemp, 1)
                temp(1) = {cell2mat(Stemp(j,1)) * cell2mat(S(i,1))};
                temp(2) = Stemp(j,2);
                S_ = local_add(temp, S_);
            end
        end
        S = S_;
    end
    score = 0;
    for i = 1 : size(S, 1)
        p = local_head(cell2mat(S(i,2)));
        score = score + cell2mat(S(i,1)) * abs(p(M) - RefPoint(M));
    end
end


%% =================== Monte Carlo HV (M >= 4) ===================
function score = local_mc_hv(PopObj, RefPoint, SampleNum)
    M = size(PopObj, 2);
    MaxValue = RefPoint;
    MinValue = min(PopObj, [], 1);
    Samples = unifrnd(repmat(MinValue, SampleNum, 1), repmat(MaxValue, SampleNum, 1));
    for i = 1 : size(PopObj, 1)
        domi = true(size(Samples, 1), 1);
        m = 1;
        while m <= M && any(domi)
            domi = domi & PopObj(i,m) <= Samples(:,m);
            m = m + 1;
        end
        Samples(domi,:) = [];
    end
    score = prod(MaxValue - MinValue) * (1 - size(Samples, 1) / SampleNum);
end


%% =================== HV helper functions ===================
function S = local_slice(pl, k, RefPoint)
    p = local_head(pl);
    pl = local_tail(pl);
    ql = [];
    S = {};
    while ~isempty(pl)
        ql = local_insert(p, k+1, ql);
        p_ = local_head(pl);
        cell_(1,1) = {abs(p(k) - p_(k))};
        cell_(1,2) = {ql};
        S = local_add(cell_, S);
        p = p_;
        pl = local_tail(pl);
    end
    ql = local_insert(p, k+1, ql);
    cell_(1,1) = {abs(p(k) - RefPoint(k))};
    cell_(1,2) = {ql};
    S = local_add(cell_, S);
end

function ql = local_insert(p, k, pl)
    flag1 = 0;
    flag2 = 0;
    ql = [];
    hp = local_head(pl);
    while ~isempty(pl) && hp(k) < p(k)
        ql = [ql; hp];
        pl = local_tail(pl);
        hp = local_head(pl);
    end
    ql = [ql; p];
    m = length(p);
    while ~isempty(pl)
        q = local_head(pl);
        for i = k : m
            if p(i) < q(i)
                flag1 = 1;
            else
                if p(i) > q(i)
                    flag2 = 1;
                end
            end
        end
        if ~(flag1 == 1 && flag2 == 0)
            ql = [ql; local_head(pl)];
        end
        pl = local_tail(pl);
    end
end

function p = local_head(pl)
    if isempty(pl)
        p = [];
    else
        p = pl(1,:);
    end
end

function ql = local_tail(pl)
    if size(pl, 1) < 2
        ql = [];
    else
        ql = pl(2:end,:);
    end
end

function S_ = local_add(cell_, S)
    n = size(S, 1);
    m = 0;
    for k = 1 : n
        if isequal(cell_(1,2), S(k,2))
            S(k,1) = {cell2mat(S(k,1)) + cell2mat(cell_(1,1))};
            m = 1;
            break;
        end
    end
    if m == 0
        S(n+1,:) = cell_(1,:);
    end
    S_ = S;
end
