% IVF_ABL_DOM - Ablation variant: Pareto dominance-based selection
%
%   Identical to the standard IVF operator except that collection and father
%   selection use Pareto non-dominated sorting (NDSort) instead of SPEA2
%   fitness F(i) = R(i) + D(i). This simulates the original IVF/NSGA-II
%   approach where selection is based on dominance rank + crowding distance.
%
%   Changes from standard IVF.m:
%     - Collection: sort by NDSort front number (then by crowding distance
%       within the same front) instead of SPEA2 fitness
%     - Father selection: same dominance-based ranking
%     - All other mechanics (EAR, SBX, environmental selection) unchanged

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_ABL_DOM( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, N_Obj_Limit)

    FE_Before_IVF = Problem.FE;
    Zmin = 0;

    %% Check IVF activation trigger
    if IVF_Total_FE > ivf_rate * Problem.FE
        IVF_Gen_FE = 0;
        IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
        Mating_N = Problem.N;
        return;
    end

    All_IVF_Offspring = [];

    %% =================== Collection Phase (Dominance-based) ===================
    IVF_Population = [];

    % ABLATION: Use non-dominated sorting + crowding distance for ranking
    PopObj = Population.objs;
    [FrontNo, ~] = NDSort(PopObj, inf);
    CrowdDis = CrowdingDistance(PopObj, FrontNo);

    % Create composite ranking: primary = front number, secondary = -crowding
    % Lower composite score = better (front 1 first, higher crowding preferred)
    CompositeRank = FrontNo' * max(CrowdDis) - CrowdDis';
    [~, SortedIndices] = sort(CompositeRank, 'ascend');

    % Determine number of parents (at least Problem.M + 1)
    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    % Select father randomly within top-2c by dominance ranking (keep 2c for fairness)
    Max_Range = min(NumParents * 2, Problem.N);
    Pos_Pai = randi([1, Max_Range]);
    Father_Index = SortedIndices(Pos_Pai);
    Father = Population(Father_Index);

    % Select best individuals as mother candidates
    ParentsIndices = SortedIndices(1:NumParents);

    % Ensure mothers are the best individuals excluding the father
    if ismember(Father_Index, ParentsIndices)
        MothersIndices = ParentsIndices(ParentsIndices ~= Father_Index);
    else
        MothersIndices = ParentsIndices(1:NumParents - 1);
    end

    Mothers = Population(MothersIndices);

    %% =================== EAR Phase (Mutation) ===================
    if M == 0
        MutatedMothers = Mothers;
        IVF_Population = [IVF_Population, Father, MutatedMothers];
    else
        if EARN == 1
            MutatedMothers_decs = Problem.Initialization_with_no_evaluation(NumParents - 1);
            Mothers.setDec(MutatedMothers_decs);
        else
            [MutatedMothers_decs, MutateMothersIdx] = PolynomialMutation( ...
                Mothers, M, V, Problem.lower, Problem.upper, 1, 20);
            Mothers.setDec(MutatedMothers_decs);
            for i = 1:length(Mothers)
                Mothers(i).ivf = true;
                if ismember(i, MutateMothersIdx)
                    Mothers(i).mae_mutada = true;
                else
                    Mothers(i).mae = true;
                end
            end
        end

        MutatedMothers = Mothers;
        IVF_Population = [IVF_Population, Father, MutatedMothers];
    end

    %% =================== Assisted Reproduction Phase ===================
    % NOTE: Environmental selection still uses SPEA2 mechanism (unchanged)
    % Only the IVF collection/selection is dominance-based
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = length(MutatedMothers);
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;
    Current_Father = Father;
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        IVF_Offspring = IVF_Recombination(Current_Father, MutatedMothers, Cycles, Problem, N_Offspring);
        IVF_Offspring = Problem.Evaluation(IVF_Offspring);

        for i = 1:length(IVF_Offspring)
            IVF_Offspring(i).ivf = true;
            if MutatedMothers(i).mae_mutada
                IVF_Offspring(i).filho_mae_mutada = true;
            else
                IVF_Offspring(i).filho = true;
            end
        end

        IVF_Gen_FE = Problem.FE - FE_Before_IVF;
        All_IVF_Offspring = [All_IVF_Offspring, IVF_Offspring];

        Current_Father.ivf = true;
        Current_Father.pai = true;
        PopComparacao = [PopComparacao, IVF_Offspring];

        [PopComparacao, PopComparacaoFitness] = EnvironmentalSelection(PopComparacao, Problem.N);

        if N_Obj_Limit == 0
            [Current_Father, shouldBreak] = selectFatherByFitness( ...
                PopComparacao, PopComparacaoFitness, Current_Father);
        else
            [Current_Father, shouldBreak] = selectFatherByRank( ...
                PopComparacao, PopComparacaoFitness, Max_Range);
        end

        [PopComparacao.pai] = deal([]);
        [PopComparacao.filho] = deal([]);
        [PopComparacao.filho_mae_mutada] = deal([]);

        if shouldBreak
            break;
        end
    end

    %% Finalize
    Population = PopComparacao;
    [Population.ivf] = deal(true);
    [Population.filho] = deal([]);
    [Population.pai] = deal([]);
    [Population.mae] = deal([]);

    Mating_N = max(Problem.N - IVF_Gen_FE, 0);
    Zmin = 123412;
    IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
end


%% =================== Crowding Distance ===================
function CrowdDis = CrowdingDistance(PopObj, FrontNo)
    % Compute crowding distance for each solution
    [N, M] = size(PopObj);
    CrowdDis = zeros(1, N);

    Fronts = setdiff(unique(FrontNo), inf);
    for f = Fronts
        Front = find(FrontNo == f);
        Fmax = max(PopObj(Front, :), [], 1);
        Fmin = min(PopObj(Front, :), [], 1);
        for m = 1:M
            [~, Rank] = sort(PopObj(Front, m));
            CrowdDis(Front(Rank(1))) = inf;
            CrowdDis(Front(Rank(end))) = inf;
            for k = 2:length(Front)-1
                if Fmax(m) - Fmin(m) > 0
                    CrowdDis(Front(Rank(k))) = CrowdDis(Front(Rank(k))) + ...
                        (PopObj(Front(Rank(k+1)), m) - PopObj(Front(Rank(k-1)), m)) / (Fmax(m) - Fmin(m));
                end
            end
        end
    end
end


%% =================== Helper: Father Selection by Fitness ===================
function [newFather, shouldBreak] = selectFatherByFitness(Pop, PopFitness, currentFather)
    shouldBreak = false;
    newFather = currentFather;

    indices_pai = find([Pop.pai]);

    if ~isempty(indices_pai)
        Fitness_Father = PopFitness(indices_pai);
    else
        Fitness_Father = 100000;
    end

    indices_filhos = find([Pop.filho]);

    if isempty(indices_filhos)
        shouldBreak = true;
        return;
    end

    Fitness_Offspring = PopFitness(indices_filhos);
    [min_fitness, melhor_idx_filho] = min(Fitness_Offspring);
    idx_melhor_filho = indices_filhos(melhor_idx_filho);

    if min_fitness < Fitness_Father
        newFather = Pop(idx_melhor_filho);
    else
        shouldBreak = true;
    end
end


%% =================== Helper: Father Selection by Rank ===================
function [newFather, shouldBreak] = selectFatherByRank(Pop, PopFitness, MaxRange)
    shouldBreak = false;
    newFather = Pop(1);

    [~, sortedIndices] = sort(PopFitness);
    selectionRange = 1:min(MaxRange, length(Pop));

    for i = selectionRange
        idx = sortedIndices(i);
        if any(Pop(idx).filho) || any(Pop(idx).filho_mae_mutada)
            newFather = Pop(idx);
            return;
        end
    end

    shouldBreak = true;
end


%% =================== Polynomial Mutation ===================
function [MutatedMothers, MutateMothersIdx] = PolynomialMutation(Mothers, M, V, lower, upper, proM, disM)
    if isa(Mothers, 'SOLUTION')
        Mothers_decs = Mothers.decs;
    end

    [N, D] = size(Mothers_decs);
    MutatedMothers = Mothers_decs;

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
end


%% =================== IVF Recombination (SBX Crossover) ===================
function Offspring = IVF_Recombination(Father, Mothers, ~, Problem, N_Offspring)
    proC = 1;
    disC = 20;

    Father_dec  = Father.decs;
    Mothers_dec = Mothers.decs;
    [N, D] = size(Mothers_dec);

    Fathers_dec = repmat(Father_dec, N, 1);
    beta = zeros(N, D);
    mu = rand(N, D);

    beta(mu <= 0.5) = (2 * mu(mu <= 0.5)).^(1 / (disC + 1));
    beta(mu > 0.5)  = (2 - 2 * mu(mu > 0.5)).^(-1 / (disC + 1));

    beta = beta .* (-1).^randi([0, 1], N, D);
    beta(rand(N, D) < 0.5) = 1;
    beta(repmat(rand(N, 1) > proC, 1, D)) = 1;

    if N_Offspring == 1
        if rand() < 0.5
            Offspring = (Fathers_dec + Mothers_dec) / 2 + beta .* (Fathers_dec - Mothers_dec) / 2;
        else
            Offspring = (Fathers_dec + Mothers_dec) / 2 - beta .* (Fathers_dec - Mothers_dec) / 2;
        end
    else
        Offspring = [(Fathers_dec + Mothers_dec) / 2 + beta .* (Fathers_dec - Mothers_dec) / 2;
                     (Fathers_dec + Mothers_dec) / 2 - beta .* (Fathers_dec - Mothers_dec) / 2];
    end

    % Clamp offspring to problem bounds (matching OperatorGA behavior)
    Lower = repmat(Problem.lower, size(Offspring, 1), 1);
    Upper = repmat(Problem.upper, size(Offspring, 1), 1);
    Offspring = min(max(Offspring, Lower), Upper);
end
