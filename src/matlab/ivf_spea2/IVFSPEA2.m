classdef IVFSPEA2 < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % Strength Pareto Evolutionary Algorithm 2 with In Vitro Fertilization
    %
    % C          --- 0.11 --- Collection rate (fraction of population)
    % R          --- 0.1  --- IVF trigger ratio
    % M          --- 0.5  --- Fraction of mothers to mutate
    % V          --- 0.5  --- Fraction of decision variables to mutate
    % Cycles     --- 3    --- Maximum IVF cycles per generation
    % S          --- 1    --- Steady State
    % N_Offspring --- 1   --- Number of offspring per SBX crossover
    % EARN       --- 0    --- 0: EAR mode, 1: EARN mode
    % N_Obj_Limit --- 0   --- Father selection limit (0 = normal selection)

    %------------------------------- Reference --------------------------------
    % E. Zitzler, M. Laumanns, and L. Thiele, SPEA2: Improving the strength
    % Pareto evolutionary algorithm, Proceedings of the Conference on
    % Evolutionary Methods for Design, Optimization and Control with
    % Applications to Industrial Problems, 2001, 95-100.
    %------------------------------- Copyright --------------------------------
    % Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
    % research purposes. All publications which use this platform or any code
    % in the platform should acknowledge the use of "PlatEMO" and reference "Ye
    % Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
    % for evolutionary multi-objective optimization [educational forum], IEEE
    % Computational Intelligence Magazine, 2017, 12(4): 73-87".
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [C, R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit] = ...
                Algorithm.ParameterSet(13, 0.3, 0.5, 0.5, 2, 1, 1, 0, 0);

            %% Generate random initial population
            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = CalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % IVF phase
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF(Problem, Population, Fitness, Forca, Distancia, ...
                         R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                         EARN, SPEA2_Gen, N_Obj_Limit);

                [Fitness, ~, ~] = CalFitness(Population.objs);

                % Generate offspring via Tournament Selection + GA operators
                MatingPool = TournamentSelection(2, Mating_N, Fitness);
                Offspring  = OperatorGA(Problem, Population(MatingPool));

                % Environmental selection (survival)
                [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end