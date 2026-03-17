% IVF - In Vitro Fertilization operator for SPEA2
%
%   [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF(...)
%
%   Performs selection and offspring generation through mutation and crossover,
%   inspired by the In Vitro Fertilization (IVF) metaphor.
%
%   Inputs:
%     Problem       - Problem instance (used for evaluation and bounds)
%     Population    - Current population (array of SOLUTION objects)
%     Fitness       - Fitness vector for the population
%     Forca         - Strength values (S(i) from SPEA2)
%     Distancia     - Distance values (D(i) from SPEA2)
%     ivf_rate      - Ratio controlling IVF activation based on FE budget
%     C             - Collection rate (fraction of individuals to select)
%     M             - Fraction of mothers to mutate (0 = AR mode)
%     V             - Fraction of decision variables to mutate per mother
%     Cycles        - Maximum number of IVF cycles per generation
%     IVF_Total_FE  - Cumulative FE consumed by IVF across all generations
%     N_Offspring   - Number of offspring per SBX crossover (1 or 2)
%     EARN          - 0: EAR mode (polynomial mutation), 1: EARN (random)
%     SPEA2_Gen     - Current host generation number
%     N_Obj_Limit   - Father selection limit (0 = normal fitness-based)
%
%   Outputs:
%     Population    - Updated population after IVF
%     Zmin          - Reserved (placeholder)
%     IVF_Gen_FE    - FE consumed by IVF in this generation
%     IVF_Total_FE  - Updated cumulative FE consumed by IVF
%     Mating_N      - Adjusted mating pool size for the host algorithm

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, N_Obj_Limit)

    FE_Before_IVF = Problem.FE;
    Zmin = 0;

    %% Check IVF activation trigger
    % Skip IVF if accumulated FE exceeds the allowed rate
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

    % Select father randomly within an extended range
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
        % AR mode: no mutation of mothers
        MutatedMothers = Mothers;
        IVF_Population = [IVF_Population, Father, MutatedMothers];
    else
        if EARN == 1
            % EARN mode: generate random solutions instead of mutating
            MutatedMothers_decs = Problem.Initialization_with_no_evaluation(NumParents - 1);
            Mothers.setDec(MutatedMothers_decs);
        else
            % EAR mode: apply polynomial mutation
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
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = length(MutatedMothers);
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;
    Current_Father = Father;
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        % Check if adding more evaluations would exceed the limit
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        % Crossover father with all mothers
        IVF_Offspring = IVF_Recombination(Current_Father, MutatedMothers, Cycles, Problem, N_Offspring);
        IVF_Offspring = Problem.Evaluation(IVF_Offspring);

        % Tag offspring
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

        % Environmental selection on combined population
        [PopComparacao, PopComparacaoFitness] = EnvironmentalSelection(PopComparacao, Problem.N);

        if N_Obj_Limit == 0
            % Normal selection: pick best child by fitness
            [Current_Father, shouldBreak] = selectFatherByFitness( ...
                PopComparacao, PopComparacaoFitness, Current_Father);
        else
            % N_Obj_Limit selection: pick best child within range
            [Current_Father, shouldBreak] = selectFatherByRank( ...
                PopComparacao, PopComparacaoFitness, Max_Range);
        end

        % Clean tags for next cycle
        for i = 1:length(PopComparacao)
            PopComparacao(i).pai = [];
            PopComparacao(i).filho = [];
            PopComparacao(i).filho_mae_mutada = [];
        end

        if shouldBreak
            break;
        end
    end

    %% Finalize
    Population = PopComparacao;
    for i = 1:length(Population)
        Population(i).ivf = true;
        Population(i).filho = [];
        Population(i).pai = [];
        Population(i).mae = [];
    end

    Mating_N = max(Problem.N - IVF_Gen_FE, 2);
    Zmin = 123412;
    IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
end


%% =================== Helper: Father Selection by Fitness ===================
function [newFather, shouldBreak] = selectFatherByFitness(Pop, PopFitness, currentFather)
    shouldBreak = false;
    newFather = currentFather;

    indices_pai = find(cellfun(@(x) ~isempty(x) && x, {Pop.pai}));

    if ~isempty(indices_pai)
        Fitness_Father = PopFitness(indices_pai);
    else
        Fitness_Father = 100000;
    end

    indices_filhos = find(cellfun(@(x) ~isempty(x) && x, {Pop.filho}));

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
    newFather = Pop(1);  % default

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
    % PolynomialMutation - Applies polynomial mutation to a subset of mothers.
    %
    %   M - Fraction of mothers to mutate (e.g., 0.5 = 50%)
    %   V - Fraction of variables to mutate per mother (e.g., 0.3 = 30%)

    if isa(Mothers, 'SOLUTION')
        Mothers_decs = Mothers.decs;
    end

    [N, D] = size(Mothers_decs);
    MutatedMothers = Mothers_decs;

    % Select which mothers to mutate (last NumMothersToMutate)
    NumMothersToMutate = round(M * N);
    MutateMothersIdx = (N - NumMothersToMutate + 1):N;

    % Select which variables to mutate within chosen mothers
    Site = false(N, D);
    for i = MutateMothersIdx
        NumVarsToMutate = round(V * D);
        VarIndices = randperm(D, NumVarsToMutate);
        Site(i, VarIndices) = true;
    end

    mu = rand(N, D);
    Lower = repmat(lower, N, 1);
    Upper = repmat(upper, N, 1);

    % Clamp within bounds
    MutatedMothers = min(max(MutatedMothers, Lower), Upper);

    % Apply mutation (mu <= 0.5)
    temp = Site & mu <= 0.5;
    MutatedMothers(temp) = MutatedMothers(temp) + (Upper(temp) - Lower(temp)) .* ...
        ((2 .* mu(temp) + (1 - 2 .* mu(temp)) .* (1 - (MutatedMothers(temp) - Lower(temp)) ./ ...
        (Upper(temp) - Lower(temp))) .^ (disM + 1)) .^ (1 / (disM + 1)) - 1);

    % Apply mutation (mu > 0.5)
    temp = Site & mu > 0.5;
    MutatedMothers(temp) = MutatedMothers(temp) + (Upper(temp) - Lower(temp)) .* ...
        (1 - (2 .* (1 - mu(temp)) + 2 .* (mu(temp) - 0.5) .* (1 - (Upper(temp) - MutatedMothers(temp)) ./ ...
        (Upper(temp) - Lower(temp))) .^ (disM + 1)) .^ (1 / (disM + 1)));
end


%% =================== IVF Recombination (SBX Crossover) ===================
function Offspring = IVF_Recombination(Father, Mothers, ~, Problem, N_Offspring)
    % Recombines one father with multiple mothers using SBX crossover.

    proC = 1;   % Crossover probability (100%)
    disC = 20;  % SBX distribution index

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
        % Generate a single offspring randomly
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
