classdef IVFSPEA2V3 < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVF/SPEA2 v3 with runtime-focused IVF optimizations.
    %
    % C          --- 0.12  --- Collection rate (fraction of population)
    % R          --- 0.225 --- IVF trigger ratio (fraction of total FE budget)
    % M          --- 0.3   --- Fraction of mothers to mutate (EAR light)
    % V          --- 0.1   --- Fraction of decision variables to mutate
    % Cycles     --- 2     --- Maximum IVF cycles per generation
    % N_Offspring --- 1    --- Number of offspring per SBX crossover
    % EARN       --- 0     --- 0: EAR mode, 1: EARN mode

    %------------------------------- Reference --------------------------------
    % IVF/SPEA2 v3 preserves the v2 search structure while reducing runtime:
    %   1) no redundant post-IVF exact fitness recomputation in the host loop;
    %   2) exact SPEA2 fitness reuses pairwise distances and partial k-NN sort;
    %   3) IVF inner cycles use a lighter front+density proxy for continuation
    %      and archive updates, reserving exact SPEA2 fitness for the host step.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [C, R, M, V, Cycles, N_Offspring, EARN] = ...
                Algorithm.ParameterSet(0.12, 0.225, 0.3, 0.1, 2, 1, 0);

            %% Generate random initial population
            Population = Problem.Initialization();
            Fitness = CalFitness_V3(Population.objs);

            Mating_N = Problem.N;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                [Population, Fitness, ~, IVF_Total_FE, Mating_N] = ...
                    IVF_V3(Problem, Population, Fitness, [], [], R, C, M, V, ...
                           Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen);

                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring  = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = ...
                        EnvironmentalSelection_V3([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end
