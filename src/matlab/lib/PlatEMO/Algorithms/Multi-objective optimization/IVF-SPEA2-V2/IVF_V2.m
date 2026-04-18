% IVF_V2 - IVF operator v2 with dissimilar father (H1) and collective
%          cycle continuation (H2).
%
%   Key changes from v1 (IVF.m):
%     1. Father selection: each mother gets a DIFFERENT father, chosen for
%        maximum objective-space distance (top-3 candidates) with binary
%        tournament by SPEA2 fitness.
%     2. Cycle continuation: cycles continue while the AVERAGE population
%        fitness improves (collective criterion), rather than requiring a
%        single offspring to beat the father.
%
%   SBX distribution index: eta_c = 20 (standard).

function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V2( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen)

    FE_Before_IVF = Problem.FE;
    Zmin = 0;
    disC = 20;

    if N_Offspring < 1 || N_Offspring ~= round(N_Offspring)
        error('IVF_V2:NOffspringInvalid', 'N_Offspring must be a positive integer.');
    end

    %% ============ Activation check (budget-only) ============
    if IVF_Total_FE > ivf_rate * Problem.FE
        IVF_Gen_FE = 0;
        IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
        Mating_N = Problem.N;
        return;
    end

    %% =================== Collection Phase ===================
    % H1: Father pool = top half of population by fitness
    [~, SortedIndices] = sort(Fitness, 'ascend');

    NumParents = max(round(Problem.N * C), Problem.M + 1);
    NumParents = min(NumParents, Problem.N);

    Father_Pool_Size = min(round(Problem.N * 0.5), Problem.N);
    Father_Pool_Indices = SortedIndices(1:Father_Pool_Size);
    Father_Pool = Population(Father_Pool_Indices);

    MothersIndices = SortedIndices(1:NumParents);
    Mothers = Population(MothersIndices);

    MotherObjs = Mothers.objs;
    MotherDecs = Mothers.decs;
    Father_Pool_Objs = Father_Pool.objs;
    Father_Pool_Fitness = Fitness(Father_Pool_Indices);

    % Reference father for cycle continuation tag (best individual)
    Current_Father = Population(SortedIndices(1));

    %% =================== EAR Phase (Mutation) ===================
    if M == 0
        MutatedMotherDecs = MotherDecs;
    else
        if EARN == 1
            if ismethod(Problem, 'Initialization_with_no_evaluation')
                MutatedMotherDecs = Problem.Initialization_with_no_evaluation(NumParents);
            else
                MutatedMotherDecs = InitializationWithoutEvaluation(Problem, NumParents);
            end
        else
            [MutatedMotherDecs, MutateMothersIdx] = PolynomialMutation( ...
                MotherDecs, M, V, Problem.lower, Problem.upper, 1, 20);
            for i = 1:length(Mothers)
                Mothers(i).ivf = true;
                if ismember(i, MutateMothersIdx)
                    Mothers(i).mae_mutada = true;
                else
                    Mothers(i).mae = true;
                end
            end
        end
    end

    %% =================== Assisted Reproduction Phase ===================
    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = size(MutatedMotherDecs, 1) * N_Offspring;
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        % H2: Record average fitness before cycle
        avg_fitness_before = mean(Fitness);

        % ---- H1: Dissimilar father per mother crossover ----
        num_mothers = size(MutatedMotherDecs, 1);
        max_new_offspring = num_mothers * N_Offspring;
        IVF_Offspring_decs = zeros(max_new_offspring, size(MutatedMotherDecs, 2));
        n_offspring_rows = 0;

        for mi = 1:num_mothers
            mother_objs = MotherObjs(mi, :);
            mother_dec = MutatedMotherDecs(mi, :);

            % Compute Euclidean distance in objective space
            current_pool_size = size(Father_Pool_Objs, 1);
            if current_pool_size == 0
                continue;
            end

            diffs = bsxfun(@minus, Father_Pool_Objs, mother_objs);
            dists = sqrt(sum(diffs.^2, 2));
            dists(~isfinite(dists)) = -Inf;

            % Exclude self from father pool (robust by object handle identity)
            is_self = arrayfun(@(cand) cand == Mothers(mi), Father_Pool);
            dists(is_self) = -Inf;

            valid_idx = find(dists > -Inf);
            K = min(3, numel(valid_idx));

            if K == 0
                % No valid non-self father available for this mother
                continue;
            else
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
            end

            father_dec = Father_Pool(winner).decs;
            offspring_dec = IVF_Recombination_Single(father_dec, mother_dec, Problem, N_Offspring, disC);

            n_new = size(offspring_dec, 1);
            rows = n_offspring_rows + (1:n_new);
            IVF_Offspring_decs(rows, :) = offspring_dec;
            n_offspring_rows = n_offspring_rows + n_new;
        end

        if n_offspring_rows == 0
            break;
        end

        IVF_Offspring = Problem.Evaluation(IVF_Offspring_decs(1:n_offspring_rows, :));
        for i = 1:length(IVF_Offspring)
            IVF_Offspring(i).ivf = true;
            IVF_Offspring(i).filho = true;
        end

        IVF_Gen_FE = Problem.FE - FE_Before_IVF;

        Current_Father.ivf = true;
        Current_Father.pai = true;
        PopComparacao = [PopComparacao, IVF_Offspring];
        [PopComparacao, PopComparacaoFitness] = EnvironmentalSelection(PopComparacao, Problem.N);

        % ---- H2: Collective continuation criterion ----
        avg_fitness_after = mean(PopComparacaoFitness);
        if avg_fitness_after < avg_fitness_before
            % Population improved collectively — select best offspring as new father
            child_mask = getLogicalTagMask(PopComparacao, 'filho');
            indices_filhos = find(child_mask);
            if ~isempty(indices_filhos)
                Fitness_Offspring = PopComparacaoFitness(indices_filhos);
                [~, best_idx] = min(Fitness_Offspring);
                Current_Father = PopComparacao(indices_filhos(best_idx));
            end
            Fitness = PopComparacaoFitness;
        else
            % No collective improvement — stop cycles
            PopComparacao = clearCycleTags(PopComparacao);
            break;
        end

        % Update father pool for next cycle
        [~, NewSorted] = sort(PopComparacaoFitness, 'ascend');
        new_pool_size = min(Father_Pool_Size, length(PopComparacao));
        Father_Pool_Indices = NewSorted(1:new_pool_size);
        Father_Pool = PopComparacao(Father_Pool_Indices);
        Father_Pool_Objs = Father_Pool.objs;
        Father_Pool_Fitness = PopComparacaoFitness(Father_Pool_Indices);
        Father_Pool_Size = new_pool_size;

        % Clean tags
        PopComparacao = clearCycleTags(PopComparacao);
    end

    %% Finalize
    Population = PopComparacao;
    [Population.ivf] = deal(true);
    Population = clearCycleTags(Population);
    [Population.mae] = deal([]);
    [Population.mae_mutada] = deal([]);

    Mating_N = max(Problem.N - IVF_Gen_FE, 0);
    Zmin = 123412;
    IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
end


%% =================== Single-Pair SBX (dissimilar father) ===================
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


%% =================== Polynomial Mutation ===================
function [MutatedMothers, MutateMothersIdx] = PolynomialMutation(Mothers, M, V, lower, upper, proM, disM)
    if isa(Mothers, 'SOLUTION')
        Mothers_decs = Mothers.decs;
    else
        Mothers_decs = Mothers;
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

    MutatedMothers = min(max(MutatedMothers, Lower), Upper);
end


%% =================== Tag helpers ===================
function mask = getLogicalTagMask(Population, field_name)
    mask = arrayfun(@(ind) ~isempty(ind.(field_name)) && logical(ind.(field_name)), Population);
end

function Population = clearCycleTags(Population)
    [Population.pai] = deal([]);
    [Population.filho] = deal([]);
    [Population.filho_mae_mutada] = deal([]);
end

function PopDec = InitializationWithoutEvaluation(Problem, N)
    PopDec = zeros(N, Problem.D);
    Type = arrayfun(@(i) find(Problem.encoding == i), 1:5, 'UniformOutput', false);

    if ~isempty(Type{1})
        PopDec(:, Type{1}) = unifrnd(repmat(Problem.lower(Type{1}), N, 1), ...
                                     repmat(Problem.upper(Type{1}), N, 1));
    end
    if ~isempty(Type{2})
        PopDec(:, Type{2}) = round(unifrnd(repmat(Problem.lower(Type{2}), N, 1), ...
                                           repmat(Problem.upper(Type{2}), N, 1)));
    end
    if ~isempty(Type{3})
        PopDec(:, Type{3}) = round(unifrnd(repmat(Problem.lower(Type{3}), N, 1), ...
                                           repmat(Problem.upper(Type{3}), N, 1)));
    end
    if ~isempty(Type{4})
        PopDec(:, Type{4}) = logical(randi([0, 1], N, length(Type{4})));
    end
    if ~isempty(Type{5})
        [~, PopDec(:, Type{5})] = sort(rand(N, length(Type{5})), 2);
    end
end
