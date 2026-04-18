% IVF_V2_COLLECTIVE - Ablation V2 variant: Collective continuation criterion (H2)
%
%   KEY CHANGE: Cycle continuation is based on whether the AVERAGE population
%   fitness improved after the IVF cycle, instead of comparing the single
%   best offspring against the father. This captures collective benefit
%   and avoids premature termination when multiple offspring improve the
%   population distribution but no single one beats the father.
%
%   Change from standard IVF.m:
%     Lines 144-152: replaced selectFatherByFitness with avg fitness check

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V2_COLLECTIVE( ...
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

    [~, SortedIndices] = sort(Fitness, 'ascend');

    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    % Father selection: standard top-2c
    Max_Range = min(NumParents * 2, Problem.N);
    Pos_Pai = randi([1, Max_Range]);
    Father_Index = SortedIndices(Pos_Pai);
    Father = Population(Father_Index);

    ParentsIndices = SortedIndices(1:NumParents);

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
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = length(MutatedMothers);
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;
    Current_Father = Father;
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        % ---- V2 CHANGE: Record avg fitness BEFORE this cycle ----
        avg_fitness_before = mean(Fitness);

        IVF_Offspring = IVF_Recombination(Current_Father, MutatedMothers, Cycles, Problem, N_Offspring);
        IVF_Offspring = Problem.Evaluation(IVF_Offspring);

        for i = 1:length(IVF_Offspring)
            IVF_Offspring(i).ivf = true;
            IVF_Offspring(i).filho = true;
        end

        IVF_Gen_FE = Problem.FE - FE_Before_IVF;
        All_IVF_Offspring = [All_IVF_Offspring, IVF_Offspring];

        Current_Father.ivf = true;
        Current_Father.pai = true;
        PopComparacao = [PopComparacao, IVF_Offspring];

        [PopComparacao, PopComparacaoFitness] = EnvironmentalSelection(PopComparacao, Problem.N);

        % ---- V2 CHANGE: Collective continuation criterion ----
        avg_fitness_after = mean(PopComparacaoFitness);

        if avg_fitness_after < avg_fitness_before
            % Population improved collectively: select best offspring as new father
            indices_filhos = find([PopComparacao.filho]);
            if ~isempty(indices_filhos)
                Fitness_Offspring = PopComparacaoFitness(indices_filhos);
                [~, best_idx] = min(Fitness_Offspring);
                Current_Father = PopComparacao(indices_filhos(best_idx));
            end
            % Update fitness reference for next cycle
            Fitness = PopComparacaoFitness;
        else
            % No collective improvement: terminate IVF
            % Clean tags before break
            [PopComparacao.pai] = deal([]);
            [PopComparacao.filho] = deal([]);
            [PopComparacao.filho_mae_mutada] = deal([]);
            break;
        end

        % Clean tags
        [PopComparacao.pai] = deal([]);
        [PopComparacao.filho] = deal([]);
        [PopComparacao.filho_mae_mutada] = deal([]);
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

    Lower = repmat(Problem.lower, size(Offspring, 1), 1);
    Upper = repmat(Problem.upper, size(Offspring, 1), 1);
    Offspring = min(max(Offspring, Lower), Upper);
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
