classdef SPEA2TRACE < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % SPEA2 baseline with per-generation dynamics logging.
    %
    % Identical to PlatEMO's SPEA2 but records per-generation snapshots
    % (IGD, HV, spread, spacing, turnover, mean fitness, ND fraction)
    % for paired comparison with IVFSPEA2V2TRACE.
    %
    % No additional parameters beyond standard SPEA2.

    properties
        TraceGenerations = {}
    end

    methods
        function main(Algorithm, Problem)
            %% Generate random population
            Population = Problem.Initialization();
            Fitness = CalFitness(Population.objs);

            % Obtain true Pareto front for IGD computation
            TruePF = Problem.GetOptimum(2000);
            HV_fmax = max(TruePF, [], 1);

            Algorithm.TraceGenerations = {};
            gen = 1;

            % Record generation 0 (initial population)
            Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                Population, Fitness, TruePF, HV_fmax, Problem, gen, 0);
            PrevPopObjs = Population.objs;

            %% Optimization
            while Algorithm.NotTerminated(Population)
                MatingPool = TournamentSelection(2, Problem.N, Fitness);
                Offspring = OperatorGA(Problem, Population(MatingPool));
                [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);

                turnover = local_turnover(PrevPopObjs, Population.objs);
                Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                    Population, Fitness, TruePF, HV_fmax, Problem, gen, turnover);
                PrevPopObjs = Population.objs;

                gen = gen + 1;
            end
        end
    end
end


%% =================== Per-generation snapshot ===================
function snap = local_snapshot(Population, Fitness, TruePF, HV_fmax, Problem, gen, turnover)
    PopObj = Population.objs;
    [N, M_obj] = size(PopObj);

    % IGD
    igd_val = mean(min(pdist2(TruePF, PopObj), [], 2));

    % HV
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

    % Spread
    if N > 1
        D_pairs = pdist(PopObj);
        spread_val = max(D_pairs);
    else
        spread_val = 0;
    end

    % Spacing
    if N > 1
        D_mat = squareform(D_pairs);
        D_mat(logical(eye(N))) = Inf;
        nn_dists = min(D_mat, [], 2);
        spacing_val = std(nn_dists);
    else
        spacing_val = 0;
    end

    mean_fitness = mean(Fitness);
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
        'ivf_activated',    false, ...
        'n_ivf_cycles',     0, ...
        'ivf_fe',           0, ...
        'turnover',         turnover);
end


%% =================== Archive turnover ===================
function t = local_turnover(PrevObjs, CurrObjs)
    if isempty(PrevObjs)
        t = 1.0;
        return;
    end
    N = size(CurrObjs, 1);
    dists = pdist2(CurrObjs, PrevObjs);
    min_dists = min(dists, [], 2);
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
