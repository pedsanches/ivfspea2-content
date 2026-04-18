% IVF_P2_COMBINED - Phase 2 combined IVF module
%
%   Supports any combination of the 4 promoted factors via boolean flags:
%     use_H1 (dissimilar father per mother)
%     use_H2 (collective continuation criterion)
%     use_H3 (eta_c = 10 instead of 20)
%     use_H4 (stagnation-based activation — caller passes is_stagnating)
%
%   Extra parameter vs baseline:
%     is_stagnating (boolean) — only used when use_H4 = true
%
%   The function signature adds use_H1, use_H2, use_H3, use_H4, is_stagnating
%   at the end. This allows one algorithm file to serve all 16 factorial
%   combinations in Phase 2.

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_P2_COMBINED( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, N_Obj_Limit, ...
        use_H1, use_H2, use_H3, use_H4, is_stagnating)

    FE_Before_IVF = Problem.FE;
    Zmin = 0;

    %% ============ Activation check ============
    % H4: require stagnation AND budget
    if use_H4
        if ~is_stagnating || IVF_Total_FE > ivf_rate * Problem.FE
            IVF_Gen_FE = 0;
            IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
            Mating_N = Problem.N;
            return;
        end
    else
        % Standard budget-only check
        if IVF_Total_FE > ivf_rate * Problem.FE
            IVF_Gen_FE = 0;
            IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
            Mating_N = Problem.N;
            return;
        end
    end

    % H3: choose SBX distribution index
    if use_H3
        disC = 10;
    else
        disC = 20;
    end

    All_IVF_Offspring = [];

    %% =================== Collection Phase ===================
    IVF_Population = [];
    [~, SortedIndices] = sort(Fitness, 'ascend');

    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    if use_H1
        % H1: Father pool = top half of population by fitness
        Father_Pool_Size = min(round(Problem.N * 0.5), Problem.N);
        Father_Pool_Indices = SortedIndices(1:Father_Pool_Size);
        Father_Pool = Population(Father_Pool_Indices);
        MothersIndices = SortedIndices(1:NumParents);
        Mothers = Population(MothersIndices);

        Father_Pool_Objs = Father_Pool.objs;
        Father_Pool_Fitness = Fitness(Father_Pool_Indices);

        % Reference father for cycle continuation (best individual)
        Reference_Father = Population(SortedIndices(1));
    else
        % Standard: single father from top-2c
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
    end

    %% =================== EAR Phase (Mutation) ===================
    if M == 0
        MutatedMothers = Mothers;
        if use_H1
            IVF_Population = [IVF_Population, MutatedMothers];
        else
            IVF_Population = [IVF_Population, Father, MutatedMothers];
        end
    else
        if EARN == 1
            if use_H1
                MutatedMothers_decs = Problem.Initialization_with_no_evaluation(NumParents);
            else
                MutatedMothers_decs = Problem.Initialization_with_no_evaluation(NumParents - 1);
            end
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
        if use_H1
            IVF_Population = [IVF_Population, MutatedMothers];
        else
            IVF_Population = [IVF_Population, Father, MutatedMothers];
        end
    end

    %% =================== Assisted Reproduction Phase ===================
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = length(MutatedMothers);
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;

    if use_H1
        Current_Father = Reference_Father;
    else
        Current_Father = Father;
    end

    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        % H2: Record average fitness before cycle
        if use_H2
            avg_fitness_before = mean(Fitness);
        end

        % ---- Crossover ----
        if use_H1
            % H1: dissimilar father per mother
            IVF_Offspring_decs = [];
            for mi = 1:length(MutatedMothers)
                mother = MutatedMothers(mi);
                mother_objs = mother.objs;

                % Robust distance computation against non-finite values
                current_pool_size = size(Father_Pool_Objs, 1);
                if current_pool_size == 0
                    continue;
                end
                dists = sqrt(sum((Father_Pool_Objs - repmat(mother_objs, current_pool_size, 1)).^2, 2));
                dists(~isfinite(dists)) = -Inf;

                % Exclude self
                mother_idx_in_pool = find(Father_Pool_Indices == MothersIndices(mi));
                if ~isempty(mother_idx_in_pool)
                    dists(mother_idx_in_pool) = -Inf;
                end

                valid_idx = find(dists > -Inf);
                K = min(3, length(valid_idx));

                if K == 0
                    % Fallback: choose best-fitness candidate from pool
                    [~, winner] = min(Father_Pool_Fitness);
                else
                    [~, ord] = sort(dists(valid_idx), 'descend');
                    top_k_idx = valid_idx(ord(1:K));
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
                end

                father_for_this_mother = Father_Pool(winner);

                offspring_dec = IVF_Recombination_Single(father_for_this_mother, mother, Problem, N_Offspring, disC);
                IVF_Offspring_decs = [IVF_Offspring_decs; offspring_dec];
            end

            if isempty(IVF_Offspring_decs)
                break;
            end
            IVF_Offspring = Problem.Evaluation(IVF_Offspring_decs);
        else
            % Standard: single father for all mothers
            IVF_Offspring = IVF_Recombination(Current_Father, MutatedMothers, Problem, N_Offspring, disC);
            IVF_Offspring = Problem.Evaluation(IVF_Offspring);
        end

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

        % ---- Cycle continuation ----
        if use_H2
            % H2: collective criterion
            avg_fitness_after = mean(PopComparacaoFitness);
            if avg_fitness_after < avg_fitness_before
                % Improved collectively — select best offspring as new father
                indices_filhos = find([PopComparacao.filho]);
                if ~isempty(indices_filhos)
                    Fitness_Offspring = PopComparacaoFitness(indices_filhos);
                    [~, best_idx] = min(Fitness_Offspring);
                    Current_Father = PopComparacao(indices_filhos(best_idx));
                end
                Fitness = PopComparacaoFitness;
            else
                % No improvement — stop
                [PopComparacao.pai] = deal([]);
                [PopComparacao.filho] = deal([]);
                [PopComparacao.filho_mae_mutada] = deal([]);
                break;
            end
        else
            % Standard: single best offspring vs father
            [Current_Father, shouldBreak] = selectFatherByFitness( ...
                PopComparacao, PopComparacaoFitness, Current_Father);
            if shouldBreak
                [PopComparacao.pai] = deal([]);
                [PopComparacao.filho] = deal([]);
                [PopComparacao.filho_mae_mutada] = deal([]);
                break;
            end
        end

        % H1: update father pool for next cycle
        if use_H1
            [~, NewSorted] = sort(PopComparacaoFitness, 'ascend');
            new_pool_size = min(Father_Pool_Size, length(PopComparacao));
            Father_Pool_Indices_local = NewSorted(1:new_pool_size);
            Father_Pool_Indices = Father_Pool_Indices_local;
            Father_Pool = PopComparacao(Father_Pool_Indices);
            Father_Pool_Objs = PopComparacao(Father_Pool_Indices_local).objs;
            Father_Pool_Fitness = PopComparacaoFitness(Father_Pool_Indices_local);
            Father_Pool_Size = new_pool_size;
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


%% =================== Multi-mother SBX (standard single father) ===================
function Offspring = IVF_Recombination(Father, Mothers, Problem, N_Offspring, disC)
    proC = 1;

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


%% =================== Single-Pair SBX (H1 dissimilar) ===================
function Offspring = IVF_Recombination_Single(Father, Mother, Problem, N_Offspring, disC)
    proC = 1;

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
