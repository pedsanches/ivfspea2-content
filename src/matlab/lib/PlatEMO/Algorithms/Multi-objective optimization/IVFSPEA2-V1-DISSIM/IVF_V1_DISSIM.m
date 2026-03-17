% IVF_V1_DISSIM - Ablation V2 variant: Dissimilar father per mother (H1)
%
%   KEY CHANGE: Instead of selecting ONE father for all mothers, each
%   mother gets a DIFFERENT father chosen to maximize objective-space
%   distance from that mother. The father must be non-dominated (or from
%   the top fitness pool). Among the top-3 most distant candidates, the
%   winner is selected via binary tournament by SPEA2 fitness.
%
%   This targets the "inbreeding structural bias" where a single father
%   generates correlated offspring that are penalized by SPEA2's density
%   estimator D(i).

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V1_DISSIM( ...
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

    %% =================== Collection Phase ===================
    IVF_Population = [];

    % Sort fitness in ascending order
    [~, SortedIndices] = sort(Fitness, 'ascend');

    % Determine number of parents (at least Problem.M + 1)
    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    % ---- V1 CHANGE: Father pool = top half of population by fitness ----
    % (broader pool to allow dissimilar selection)
    Father_Pool_Size = min(round(Problem.N * 0.5), Problem.N);
    Father_Pool_Indices = SortedIndices(1:Father_Pool_Size);

    % Select mothers (top-c individuals)
    MothersIndices = SortedIndices(1:NumParents);
    Mothers = Population(MothersIndices);

    % Precompute objective values for father pool
    Father_Pool_Objs = Population(Father_Pool_Indices).objs;
    Father_Pool_Fitness = Fitness(Father_Pool_Indices);

    %% =================== EAR Phase (Mutation) ===================
    if M == 0
        MutatedMothers = Mothers;
        IVF_Population = [IVF_Population, MutatedMothers];
    else
        if EARN == 1
            MutatedMothers_decs = Problem.Initialization_with_no_evaluation(NumParents);
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
        IVF_Population = [IVF_Population, MutatedMothers];
    end

    %% =================== Assisted Reproduction Phase ===================
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = length(MutatedMothers);
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;

    % ---- V1 CHANGE: Select dissimilar father PER MOTHER ----
    % For cycle continuation, we track a "reference father" (best offspring)
    % For initial crossover, each mother gets its own father
    Reference_Father = Population(SortedIndices(1));  % best individual as reference
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        % ---- V1 CORE: Select a dissimilar father for EACH mother ----
        IVF_Offspring_decs = [];
        for mi = 1:length(MutatedMothers)
            mother = MutatedMothers(mi);
            mother_objs = mother.objs;

            % Compute distances in objective space from this mother to all father candidates
            dists = sqrt(sum((Father_Pool_Objs - repmat(mother_objs, Father_Pool_Size, 1)).^2, 2));

            % Exclude self (if mother is in the father pool)
            mother_idx_in_pool = find(Father_Pool_Indices == MothersIndices(mi));
            if ~isempty(mother_idx_in_pool)
                dists(mother_idx_in_pool) = -Inf;
            end

            % Select top-3 most distant candidates
            K = min(3, sum(dists > -Inf));
            [~, top_k_idx] = maxk(dists, K);

            % Binary tournament by fitness among top-K distant candidates
            if K >= 2
                t1 = top_k_idx(randi(K));
                t2 = top_k_idx(randi(K));
                if Father_Pool_Fitness(t1) <= Father_Pool_Fitness(t2)
                    winner = t1;
                else
                    winner = t2;
                end
            else
                winner = top_k_idx(1);
            end

            father_for_this_mother = Population(Father_Pool_Indices(winner));

            % SBX crossover with this specific father
            offspring_dec = IVF_Recombination_Single(father_for_this_mother, mother, Problem, N_Offspring);
            IVF_Offspring_decs = [IVF_Offspring_decs; offspring_dec];
        end

        % Evaluate all offspring at once
        IVF_Offspring = Problem.Evaluation(IVF_Offspring_decs);

        for i = 1:length(IVF_Offspring)
            IVF_Offspring(i).ivf = true;
            IVF_Offspring(i).filho = true;
        end

        IVF_Gen_FE = Problem.FE - FE_Before_IVF;
        All_IVF_Offspring = [All_IVF_Offspring, IVF_Offspring];

        Reference_Father.ivf = true;
        Reference_Father.pai = true;
        PopComparacao = [PopComparacao, IVF_Offspring];

        [PopComparacao, PopComparacaoFitness] = EnvironmentalSelection(PopComparacao, Problem.N);

        % Cycle continuation: use standard fitness-based criterion
        [Reference_Father, shouldBreak] = selectFatherByFitness( ...
            PopComparacao, PopComparacaoFitness, Reference_Father);

        % Update father pool objectives for next cycle
        [~, NewSorted] = sort(PopComparacaoFitness, 'ascend');
        new_pool_size = min(Father_Pool_Size, length(PopComparacao));
        Father_Pool_Indices_local = NewSorted(1:new_pool_size);
        Father_Pool_Objs = PopComparacao(Father_Pool_Indices_local).objs;
        Father_Pool_Fitness = PopComparacaoFitness(Father_Pool_Indices_local);
        Father_Pool_Size = new_pool_size;

        % Clean tags
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


%% =================== Single-Pair SBX Crossover ===================
function Offspring = IVF_Recombination_Single(Father, Mother, Problem, N_Offspring)
    proC = 1;
    disC = 20;

    Father_dec = Father.decs;
    Mother_dec = Mother.decs;
    D = length(Father_dec);

    beta = zeros(1, D);
    mu = rand(1, D);

    beta(mu <= 0.5) = (2 * mu(mu <= 0.5)).^(1 / (disC + 1));
    beta(mu > 0.5)  = (2 - 2 * mu(mu > 0.5)).^(-1 / (disC + 1));

    beta = beta .* (-1).^randi([0, 1], 1, D);
    beta(rand(1, D) < 0.5) = 1;
    if rand() > proC
        beta(:) = 1;
    end

    if rand() < 0.5
        Offspring = (Father_dec + Mother_dec) / 2 + beta .* (Father_dec - Mother_dec) / 2;
    else
        Offspring = (Father_dec + Mother_dec) / 2 - beta .* (Father_dec - Mother_dec) / 2;
    end

    % Clamp to bounds
    Offspring = min(max(Offspring, Problem.lower), Problem.upper);
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
