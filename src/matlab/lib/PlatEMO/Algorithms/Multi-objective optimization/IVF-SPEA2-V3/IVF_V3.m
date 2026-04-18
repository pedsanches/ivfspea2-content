function [Population, Fitness, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V3( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen)

    FE_Before_IVF = Problem.FE;

    if N_Offspring < 1 || N_Offspring ~= round(N_Offspring)
        error('IVF_V3:NOffspringInvalid', 'N_Offspring must be a positive integer.');
    end

    if IVF_Total_FE > ivf_rate * Problem.FE
        IVF_Gen_FE = 0;
        Mating_N = Problem.N;
        return;
    end

    [~, SortedIndices] = sort(Fitness, 'ascend');

    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    Father_Pool_Size = max(1, min(round(Problem.N * 0.5), Problem.N));
    Father_Pool_Indices = SortedIndices(1:Father_Pool_Size);

    MothersIndices = SortedIndices(1:NumParents);
    Mothers = Population(MothersIndices);
    MotherObjs = Mothers.objs;
    MotherDecs = Mothers.decs;

    if M == 0
        MutatedMotherDecs = MotherDecs;
    elseif EARN == 1
        if ismethod(Problem, 'Initialization_with_no_evaluation')
            MutatedMotherDecs = Problem.Initialization_with_no_evaluation(NumParents);
        else
            MutatedMotherDecs = InitializationWithoutEvaluation(Problem, NumParents);
        end
    else
        MutatedMotherDecs = PolynomialMutation(MotherDecs, M, V, Problem.lower, Problem.upper, 20);
    end

    Limit_Max_Evals = Problem.N;
    Evals_Per_Cycle = size(MutatedMotherDecs, 1) * N_Offspring;
    IVF_Gen_FE = 0;

    PopComparacao = Population;
    PopIDs = 1:numel(Population);
    MotherIDs = PopIDs(MothersIndices);
    NextSolutionID = numel(PopIDs) + 1;
    ProxyFitness = ProxyFitness_V3(PopComparacao.objs);
    PopulationChanged = false;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Evals_Per_Cycle > Limit_Max_Evals
            break;
        end

        avg_fitness_before = mean(ProxyFitness);

        current_pool_size = min(Father_Pool_Size, numel(Father_Pool_Indices));
        if current_pool_size == 0
            break;
        end

        Father_Pool_Indices = Father_Pool_Indices(1:current_pool_size);
        Father_Pool = PopComparacao(Father_Pool_Indices);
        Father_Pool_Objs = Father_Pool.objs;
        Father_Pool_Decs = Father_Pool.decs;
        Father_Pool_Fitness = ProxyFitness(Father_Pool_Indices);
        Father_Pool_IDs = PopIDs(Father_Pool_Indices);

        MotherToFatherDists = pdist2(MotherObjs, Father_Pool_Objs);
        MotherToFatherDists(~isfinite(MotherToFatherDists)) = -inf;

        num_mothers = size(MutatedMotherDecs, 1);
        max_new_offspring = num_mothers * N_Offspring;
        IVF_Offspring_Decs = zeros(max_new_offspring, size(MutatedMotherDecs, 2));
        n_offspring_rows = 0;

        for mi = 1:num_mothers
            dists = MotherToFatherDists(mi, :);
            dists(Father_Pool_IDs == MotherIDs(mi)) = -inf;

            valid_idx = find(dists > -inf);
            K = min(3, numel(valid_idx));
            if K == 0
                continue;
            end

            [~, ord] = sort(dists(valid_idx), 'descend');
            top_k_idx = valid_idx(ord(1:K));

            if K >= 2
                draw = randperm(K, 2);
                t1 = top_k_idx(draw(1));
                t2 = top_k_idx(draw(2));
                if Father_Pool_Fitness(t1) <= Father_Pool_Fitness(t2)
                    winner = t1;
                else
                    winner = t2;
                end
            else
                winner = top_k_idx(1);
            end

            offspring_dec = IVF_Recombination_Single( ...
                Father_Pool_Decs(winner, :), MutatedMotherDecs(mi, :), ...
                Problem, N_Offspring, 20);

            n_new = size(offspring_dec, 1);
            rows = n_offspring_rows + (1:n_new);
            IVF_Offspring_Decs(rows, :) = offspring_dec;
            n_offspring_rows = n_offspring_rows + n_new;
        end

        if n_offspring_rows == 0
            break;
        end

        IVF_Offspring = Problem.Evaluation(IVF_Offspring_Decs(1:n_offspring_rows, :));
        IVF_Gen_FE = Problem.FE - FE_Before_IVF;

        OffspringIDs = NextSolutionID:(NextSolutionID + n_offspring_rows - 1);
        NextSolutionID = NextSolutionID + n_offspring_rows;

        [PopComparacao, ProxyFitness, PopIDs] = EnvironmentalSelectionProxy_V3( ...
            [PopComparacao, IVF_Offspring], [PopIDs, OffspringIDs], Problem.N);
        PopulationChanged = true;

        avg_fitness_after = mean(ProxyFitness);
        if avg_fitness_after >= avg_fitness_before
            break;
        end

        [~, NewSorted] = sort(ProxyFitness, 'ascend');
        Father_Pool_Size = min(Father_Pool_Size, numel(PopComparacao));
        Father_Pool_Indices = NewSorted(1:Father_Pool_Size);
    end

    Population = PopComparacao;
    if PopulationChanged
        Fitness = CalFitness_V3(Population.objs);
    end

    if ~isempty(Population)
        [Population.pai] = deal([]);
        [Population.filho] = deal([]);
        [Population.filho_mae_mutada] = deal([]);
        [Population.mae] = deal([]);
        [Population.mae_mutada] = deal([]);
        [Population.ivf] = deal(true);
    end

    Mating_N = max(Problem.N - IVF_Gen_FE, 0);
    IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
end


function [Population, Fitness, PopulationIDs] = EnvironmentalSelectionProxy_V3(Population, PopulationIDs, N)
    Fitness = ProxyFitness_V3(Population.objs);
    if numel(Population) <= N
        return;
    end

    Next = Fitness < 1;
    if sum(Next) < N
        [~, Rank] = sort(Fitness, 'ascend');
        Next(Rank(1:N)) = true;
    elseif sum(Next) > N
        FirstFront = find(Next);
        [~, Rank] = sort(Fitness(FirstFront), 'ascend');
        Next = false(1, numel(Population));
        Next(FirstFront(Rank(1:N))) = true;
    end

    Population = Population(Next);
    PopulationIDs = PopulationIDs(Next);
    Fitness = Fitness(Next);
end


function Fitness = ProxyFitness_V3(PopObj)
    N = size(PopObj, 1);
    if N == 0
        Fitness = zeros(1, 0);
        return;
    end

    FrontNo = NDSort(PopObj, N);
    NearestDist = ApproxNearestNeighborDistance_V3(PopObj);
    Density = 1 ./ (NearestDist + 2);
    Fitness = FrontNo - 1 + Density';
end


function NearestDist = ApproxNearestNeighborDistance_V3(PopObj)
    [N, M] = size(PopObj);
    NearestDist = inf(N, 1);
    if N <= 1
        return;
    end

    for m = 1:M
        [~, Order] = sort(PopObj(:, m), 'ascend');
        Prev = Order(1:end-1);
        Next = Order(2:end);
        Delta = PopObj(Next, :) - PopObj(Prev, :);
        LocalDist = sqrt(sum(Delta.^2, 2));
        NearestDist(Prev) = min(NearestDist(Prev), LocalDist);
        NearestDist(Next) = min(NearestDist(Next), LocalDist);
    end
end


function Offspring = IVF_Recombination_Single(Father_dec, Mother_dec, Problem, N_Offspring, disC)
    proC = 1;
    D = length(Father_dec);

    Offspring = zeros(N_Offspring, D);
    MeanParent = (Father_dec + Mother_dec) / 2;
    DiffParent = (Father_dec - Mother_dec) / 2;

    for oi = 1:N_Offspring
        beta = zeros(1, D);
        mu = rand(1, D);

        beta(mu <= 0.5) = (2 * mu(mu <= 0.5)).^(1 / (disC + 1));
        beta(mu > 0.5) = (2 - 2 * mu(mu > 0.5)).^(-1 / (disC + 1));

        beta = beta .* (-1).^randi([0, 1], 1, D);
        beta(rand(1, D) < 0.5) = 1;
        if rand() > proC
            beta(:) = 1;
        end

        if rand() < 0.5
            Offspring(oi, :) = MeanParent + beta .* DiffParent;
        else
            Offspring(oi, :) = MeanParent - beta .* DiffParent;
        end
    end

    Lower = repmat(Problem.lower, N_Offspring, 1);
    Upper = repmat(Problem.upper, N_Offspring, 1);
    Offspring = min(max(Offspring, Lower), Upper);
end


function MutatedMothers = PolynomialMutation(MothersDecs, M, V, lower, upper, disM)
    [N, D] = size(MothersDecs);
    MutatedMothers = MothersDecs;

    NumMothersToMutate = round(M * N);
    MutateMothersIdx = (N - NumMothersToMutate + 1):N;

    Site = false(N, D);
    for i = MutateMothersIdx
        NumVarsToMutate = round(V * D);
        VarIndices = randperm(D, NumVarsToMutate);
        Site(i, VarIndices) = true;
    end

    mu = rand(N, D);
    Lower = repmat(lower, N, 1);
    Upper = repmat(upper, N, 1);
    MutatedMothers = min(max(MutatedMothers, Lower), Upper);

    temp = Site & mu <= 0.5;
    MutatedMothers(temp) = MutatedMothers(temp) + (Upper(temp) - Lower(temp)) .* ...
        ((2 .* mu(temp) + (1 - 2 .* mu(temp)) .* (1 - (MutatedMothers(temp) - Lower(temp)) ./ ...
        (Upper(temp) - Lower(temp))) .^ (disM + 1)) .^ (1 / (disM + 1)) - 1);

    temp = Site & mu > 0.5;
    MutatedMothers(temp) = MutatedMothers(temp) + (Upper(temp) - Lower(temp)) .* ...
        (1 - (2 .* (1 - mu(temp)) + 2 .* (mu(temp) - 0.5) .* (1 - (Upper(temp) - MutatedMothers(temp)) ./ ...
        (Upper(temp) - Lower(temp))) .^ (disM + 1)) .^ (1 / (disM + 1)));

    MutatedMothers = min(max(MutatedMothers, Lower), Upper);
end


function PopDec = InitializationWithoutEvaluation(Problem, N)
    PopDec = zeros(N, Problem.D);
    Type = arrayfun(@(i) find(Problem.encoding == i), 1:5, 'UniformOutput', false);

    if ~isempty(Type{1})
        span = repmat(Problem.upper(Type{1}) - Problem.lower(Type{1}), N, 1);
        base = repmat(Problem.lower(Type{1}), N, 1);
        PopDec(:, Type{1}) = base + rand(N, length(Type{1})) .* span;
    end
    if ~isempty(Type{2})
        span = repmat(Problem.upper(Type{2}) - Problem.lower(Type{2}), N, 1);
        base = repmat(Problem.lower(Type{2}), N, 1);
        PopDec(:, Type{2}) = round(base + rand(N, length(Type{2})) .* span);
    end
    if ~isempty(Type{3})
        span = repmat(Problem.upper(Type{3}) - Problem.lower(Type{3}), N, 1);
        base = repmat(Problem.lower(Type{3}), N, 1);
        PopDec(:, Type{3}) = round(base + rand(N, length(Type{3})) .* span);
    end
    if ~isempty(Type{4})
        PopDec(:, Type{4}) = logical(randi([0, 1], N, length(Type{4})));
    end
    if ~isempty(Type{5})
        [~, PopDec(:, Type{5})] = sort(rand(N, length(Type{5})), 2);
    end
end
