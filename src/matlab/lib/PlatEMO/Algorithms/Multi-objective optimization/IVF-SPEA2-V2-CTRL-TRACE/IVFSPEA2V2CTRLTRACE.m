classdef IVFSPEA2V2CTRLTRACE < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVF/SPEA2 v2 trace variant with a minimal turnover-based controller.
    %
    % Parameters 1..8 match IVFSPEA2V2TRACE.
    % WarmupFrac        --- 0.20      --- Fraction of maxFE used before deciding
    % TurnoverThreshold --- 0.232437  --- Keep IVF on iff mean early turnover >= threshold

    properties
        TraceCycles = {}
        TraceGenerations = {}
        TraceParameters = struct()
        TraceCapturePopulation = false
        ControllerState = struct()
    end

    methods
        function main(Algorithm, Problem)
            [C, R, M, V, Cycles, N_Offspring, EARN, TraceCapturePopulation, ...
                WarmupFrac, TurnoverThreshold] = ...
                Algorithm.ParameterSet(0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0, 0.20, 0.232437);

            if ~isfinite(WarmupFrac) || WarmupFrac <= 0 || WarmupFrac >= 1
                error('IVFSPEA2V2CTRLTRACE:WarmupFracInvalid', ...
                    'WarmupFrac must be strictly between 0 and 1.');
            end
            if ~isfinite(TurnoverThreshold)
                error('IVFSPEA2V2CTRLTRACE:TurnoverThresholdInvalid', ...
                    'TurnoverThreshold must be finite.');
            end

            Algorithm.TraceCycles = {};
            Algorithm.TraceGenerations = {};
            Algorithm.TraceCapturePopulation = logical(TraceCapturePopulation);
            Algorithm.ControllerState = local_init_controller_state(WarmupFrac, TurnoverThreshold);
            trace_params = struct( ...
                'collection_rate', C, ...
                'ivf_activation_ratio', R, ...
                'mother_mutation_fraction', M, ...
                'variable_mutation_fraction', V, ...
                'max_ivf_cycles', Cycles, ...
                'offspring_per_mother', N_Offspring, ...
                'exploration_mode', EARN, ...
                'capture_population', Algorithm.TraceCapturePopulation, ...
                'controller_warmup_frac', WarmupFrac, ...
                'controller_turnover_threshold', TurnoverThreshold, ...
                'controller_feature', 'mean_turnover', ...
                'controller_decision_rule', 'keep_if_mean_turnover_ge_threshold', ...
                'controller_final', Algorithm.ControllerState);
            Algorithm.TraceParameters = trace_params;

            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = IVFTraceCalFitness(Population.objs);

            TruePF = Problem.GetOptimum(2000);
            HV_fmax = max(TruePF, [], 1);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                Population, Fitness, TruePF, HV_fmax, Problem, ...
                SPEA2_Gen, 0, false, [], 0, Algorithm.ControllerState);
            PrevPopObjs = Population.objs;

            while Algorithm.NotTerminated(Population)
                Algorithm.ControllerState = local_maybe_decide_controller( ...
                    Algorithm.TraceGenerations, Problem, SPEA2_Gen, Algorithm.ControllerState);
                trace_params = Algorithm.TraceParameters;
                trace_params.controller_final = Algorithm.ControllerState;
                Algorithm.TraceParameters = trace_params;

                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V2_CTRL_TRACE(Problem, Population, Fitness, Forca, Distancia, ...
                        R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                        EARN, SPEA2_Gen, Algorithm, Algorithm.ControllerState.ivf_enabled);

                [Fitness, ~, ~] = IVFTraceCalFitness(Population.objs);

                ivf_activated = IVF_Gen_FE > 0;
                n_ivf_cycles = 0;
                if ~isempty(Algorithm.TraceCycles)
                    last_cycle = Algorithm.TraceCycles{end};
                    if last_cycle.generation == SPEA2_Gen
                        n_ivf_cycles = last_cycle.ivf_cycle;
                    end
                end

                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = IVFTraceEnvironmentalSelection([Population, Offspring], Problem.N);
                end

                turnover = local_turnover(PrevPopObjs, Population.objs);
                Algorithm.TraceGenerations{end+1} = local_snapshot( ...
                    Population, Fitness, TruePF, HV_fmax, Problem, ...
                    SPEA2_Gen, n_ivf_cycles, ivf_activated, turnover, IVF_Gen_FE, ...
                    Algorithm.ControllerState);
                PrevPopObjs = Population.objs;

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end


function state = local_init_controller_state(warmup_frac, turnover_threshold)
    state = struct( ...
        'warmup_frac', warmup_frac, ...
        'turnover_threshold', turnover_threshold, ...
        'decision_made', false, ...
        'ivf_enabled', true, ...
        'decision_fe', NaN, ...
        'decision_generation', NaN, ...
        'observed_turnover_mean', NaN, ...
        'n_turnover_generations', 0);
end

function state = local_maybe_decide_controller(trace_generations, Problem, current_generation, state)
    if state.decision_made
        return;
    end

    if Problem.FE < state.warmup_frac * Problem.maxFE
        return;
    end

    turnovers = [];
    for i = 1:numel(trace_generations)
        g = trace_generations{i};
        if ~isstruct(g) || ~isfield(g, 'turnover')
            continue;
        end
        t = g.turnover;
        if isempty(t) || ~isnumeric(t) || ~isfinite(t)
            continue;
        end
        turnovers(end+1) = double(t); %#ok<AGROW>
    end

    state.decision_made = true;
    state.decision_fe = Problem.FE;
    state.decision_generation = max(current_generation - 1, 0);
    state.n_turnover_generations = numel(turnovers);

    if isempty(turnovers)
        state.ivf_enabled = true;
        state.observed_turnover_mean = NaN;
        return;
    end

    state.observed_turnover_mean = mean(turnovers);
    state.ivf_enabled = state.observed_turnover_mean >= state.turnover_threshold;
end


function snap = local_snapshot(Population, Fitness, TruePF, HV_fmax, Problem, ...
        gen, n_ivf_cycles, ivf_activated, turnover, ivf_fe, controller_state)

    PopObj = Population.objs;
    [N, M_obj] = size(PopObj);

    igd_val = mean(min(pdist2(TruePF, PopObj), [], 2));

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

    if N > 1
        D_pairs = pdist(PopObj);
        spread_val = max(D_pairs);
    else
        spread_val = 0;
    end

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
        'generation', gen, ...
        'fe', Problem.FE, ...
        'igd', igd_val, ...
        'hv', hv_val, ...
        'spread', spread_val, ...
        'spacing', spacing_val, ...
        'mean_fitness', mean_fitness, ...
        'nd_fraction', nd_fraction, ...
        'ivf_activated', ivf_activated, ...
        'n_ivf_cycles', n_ivf_cycles, ...
        'ivf_fe', ivf_fe, ...
        'turnover', turnover, ...
        'controller_decision_made', controller_state.decision_made, ...
        'controller_ivf_enabled', controller_state.ivf_enabled, ...
        'controller_mean_turnover', controller_state.observed_turnover_mean, ...
        'controller_turnover_threshold', controller_state.turnover_threshold, ...
        'controller_warmup_frac', controller_state.warmup_frac);
end


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

function q = local_tail(pl)
    if size(pl,1) < 2
        q = [];
    else
        q = pl(2:end,:);
    end
end

function S_ = local_add(cell_, S)
    n = size(S,1);
    m = 0;
    for k = 1 : n
        if isequal(cell_(1,2),S(k,2))
            S(k,1) = {cell2mat(S(k,1))+cell2mat(cell_(1,1))};
            m = 1;
            break;
        end
    end
    if m == 0
        S_(1:size(S,1),:) = S;
        S_(size(S,1)+1,:) = cell_;
    else
        S_ = S;
    end
end
