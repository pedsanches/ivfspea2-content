classdef IVFSPEA2_V1_DISSIM < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVFSPEA2 V2-Ablation: Dissimilar father per mother (H1)
    %
    % C          --- 0.11 --- Collection rate (fraction of population)
    % R          --- 0.1  --- IVF trigger ratio
    % M          --- 0    --- Fraction of mothers to mutate (0 = AR mode)
    % V          --- 0    --- Fraction of decision variables to mutate
    % Cycles     --- 3    --- Maximum IVF cycles per generation
    % S          --- 1    --- Steady State
    % N_Offspring --- 1   --- Number of offspring per SBX crossover
    % EARN       --- 0    --- 0: EAR mode, 1: EARN mode
    % N_Obj_Limit --- 0   --- Father selection limit (0 = normal selection)

    %------------------------------- Reference --------------------------------
    % Ablation variant: instead of selecting one father for all mothers,
    % each mother gets a different father chosen to maximize objective-space
    % distance (dissimilarity). All other mechanics identical to standard.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [C, R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit] = ...
                Algorithm.ParameterSet(0.11, 0.1, 0, 0, 3, 1, 1, 0, 0);

            %% Generate random initial population
            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = CalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % IVF phase (V1: dissimilar father per mother)
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V1_DISSIM(Problem, Population, Fitness, Forca, Distancia, ...
                         R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                         EARN, SPEA2_Gen, N_Obj_Limit);

                [Fitness, ~, ~] = CalFitness(Population.objs);

                % Generate offspring via Tournament Selection + GA operators
                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring  = OperatorGA(Problem, Population(MatingPool));

                    % Environmental selection (survival)
                    [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end
