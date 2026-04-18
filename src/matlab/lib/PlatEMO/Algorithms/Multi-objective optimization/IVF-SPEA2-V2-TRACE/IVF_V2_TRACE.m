function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V2_TRACE( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, TraceAlgorithm)

    FE_Before_IVF = Problem.FE;
    Zmin = 0;
    disC = 20;

    if N_Offspring < 1 || N_Offspring ~= round(N_Offspring)
        error('IVF_V2_TRACE:NOffspringInvalid', 'N_Offspring must be a positive integer.');
    end

    if IVF_Total_FE > ivf_rate * Problem.FE
        IVF_Gen_FE = 0;
        IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
        Mating_N = Problem.N;
        return;
    end

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

    Current_Father = Population(SortedIndices(1));

    MutateMothersIdx = [];
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

    mother_mutated_mask = false(size(MutatedMotherDecs, 1), 1);
    mother_mutated_mask(MutateMothersIdx) = true;

    Limite_Maximo_Avals = Problem.N;
    Avaliacoes_Por_Ciclo = size(MutatedMotherDecs, 1) * N_Offspring;
    IVF_Gen_FE = Problem.FE - FE_Before_IVF;
    PopComparacao = Population;

    for IVF_Cycle = 1:Cycles
        if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
            break;
        end

        avg_fitness_before = mean(Fitness);
        num_mothers = size(MutatedMotherDecs, 1);
        max_new_offspring = num_mothers * N_Offspring;
        IVF_Offspring_decs = zeros(max_new_offspring, size(MutatedMotherDecs, 2));
        child_mother_objs = zeros(max_new_offspring, size(MotherObjs, 2));
        child_father_objs = zeros(max_new_offspring, size(MotherObjs, 2));
        child_parent_distance_obj = zeros(max_new_offspring, 1);
        child_mother_mutated = false(max_new_offspring, 1);
        child_mother_fitness = zeros(max_new_offspring, 1);
        child_father_fitness = zeros(max_new_offspring, 1);
        n_offspring_rows = 0;
        problem_fe_before_cycle = Problem.FE;
        ivf_gen_fe_before_cycle = IVF_Gen_FE;

        if TraceAlgorithm.TraceCapturePopulation
            population_before_objs = PopComparacao.objs;
        else
            population_before_objs = [];
        end

        for mi = 1:num_mothers
            mother_objs = MotherObjs(mi, :);
            mother_dec = MutatedMotherDecs(mi, :);
            current_pool_size = size(Father_Pool_Objs, 1);
            if current_pool_size == 0
                continue;
            end

            diffs = bsxfun(@minus, Father_Pool_Objs, mother_objs);
            dists = sqrt(sum(diffs.^2, 2));
            dists(~isfinite(dists)) = -Inf;

            is_self = arrayfun(@(cand) cand == Mothers(mi), Father_Pool);
            dists(is_self) = -Inf;

            valid_idx = find(dists > -Inf);
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

            father_dec = Father_Pool(winner).decs;
            father_objs = Father_Pool(winner).objs;
            offspring_dec = IVF_Recombination_Single(father_dec, mother_dec, Problem, N_Offspring, disC);

            n_new = size(offspring_dec, 1);
            rows = n_offspring_rows + (1:n_new);
            IVF_Offspring_decs(rows, :) = offspring_dec;
            child_mother_objs(rows, :) = repmat(mother_objs, n_new, 1);
            child_father_objs(rows, :) = repmat(father_objs, n_new, 1);
            child_parent_distance_obj(rows) = dists(winner);
            child_mother_mutated(rows) = mother_mutated_mask(mi);
            child_mother_fitness(rows) = Fitness(MothersIndices(mi));
            child_father_fitness(rows) = Father_Pool_Fitness(winner);
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
        [PopComparacao, PopComparacaoFitness] = IVFTraceEnvironmentalSelection(PopComparacao, Problem.N);

        child_selected = local_child_survival_mask(IVF_Offspring, PopComparacao);
        child_selected_fitness = nan(n_offspring_rows, 1);
        for ci = 1:n_offspring_rows
            idx = local_solution_index(PopComparacao, IVF_Offspring(ci));
            if idx > 0
                child_selected_fitness(ci) = PopComparacaoFitness(idx);
            end
        end

        avg_fitness_after = mean(PopComparacaoFitness);
        collective_improved = avg_fitness_after < avg_fitness_before;

        if TraceAlgorithm.TraceCapturePopulation
            population_after_objs = PopComparacao.objs;
        else
            population_after_objs = [];
        end

        cycle_trace = struct( ...
            'generation', SPEA2_Gen, ...
            'ivf_cycle', IVF_Cycle, ...
            'problem_fe_before', problem_fe_before_cycle, ...
            'problem_fe_after', Problem.FE, ...
            'ivf_gen_fe_before', ivf_gen_fe_before_cycle, ...
            'ivf_gen_fe_after', IVF_Gen_FE, ...
            'avg_fitness_before', avg_fitness_before, ...
            'avg_fitness_after', avg_fitness_after, ...
            'collective_improved', collective_improved, ...
            'num_mothers', num_mothers, ...
            'num_children', n_offspring_rows, ...
            'num_selected_children', sum(child_selected), ...
            'population_before_objs', population_before_objs, ...
            'population_after_objs', population_after_objs, ...
            'mother_objs', child_mother_objs(1:n_offspring_rows, :), ...
            'father_objs', child_father_objs(1:n_offspring_rows, :), ...
            'child_objs', IVF_Offspring.objs, ...
            'child_parent_distance_obj', child_parent_distance_obj(1:n_offspring_rows), ...
            'child_mother_mutated', child_mother_mutated(1:n_offspring_rows), ...
            'child_mother_fitness', child_mother_fitness(1:n_offspring_rows), ...
            'child_father_fitness', child_father_fitness(1:n_offspring_rows), ...
            'child_selected', child_selected, ...
            'child_selected_fitness_after_env', child_selected_fitness);
        TraceAlgorithm.TraceCycles{end + 1} = cycle_trace;

        if collective_improved
            child_mask = getLogicalTagMask(PopComparacao, 'filho');
            indices_filhos = find(child_mask);
            if ~isempty(indices_filhos)
                Fitness_Offspring = PopComparacaoFitness(indices_filhos);
                [~, best_idx] = min(Fitness_Offspring);
                Current_Father = PopComparacao(indices_filhos(best_idx));
            end
            Fitness = PopComparacaoFitness;
        else
            PopComparacao = clearCycleTags(PopComparacao);
            break;
        end

        [~, NewSorted] = sort(PopComparacaoFitness, 'ascend');
        new_pool_size = min(Father_Pool_Size, length(PopComparacao));
        Father_Pool_Indices = NewSorted(1:new_pool_size);
        Father_Pool = PopComparacao(Father_Pool_Indices);
        Father_Pool_Objs = Father_Pool.objs;
        Father_Pool_Fitness = PopComparacaoFitness(Father_Pool_Indices);
        Father_Pool_Size = new_pool_size;

        PopComparacao = clearCycleTags(PopComparacao);
    end

    Population = PopComparacao;
    [Population.ivf] = deal(true);
    Population = clearCycleTags(Population);
    [Population.mae] = deal([]);
    [Population.mae_mutada] = deal([]);

    Mating_N = max(Problem.N - IVF_Gen_FE, 0);
    Zmin = 123412;
    IVF_Total_FE = IVF_Total_FE + IVF_Gen_FE;
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

function child_selected = local_child_survival_mask(Children, Population)
    child_selected = false(length(Children), 1);
    for ci = 1:length(Children)
        child_selected(ci) = local_solution_index(Population, Children(ci)) > 0;
    end
end

function idx = local_solution_index(Population, Target)
    idx = 0;
    for pi = 1:length(Population)
        if Population(pi) == Target
            idx = pi;
            return;
        end
    end
end
