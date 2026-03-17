classdef IVFSPEA2V2 < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVF/SPEA2 v2 with dissimilar father selection (H1) and collective
    % cycle continuation criterion (H2).
    %
    % C          --- 0.12  --- Collection rate (fraction of population)
    % R          --- 0.225 --- IVF trigger ratio (fraction of total FE budget)
    % M          --- 0.3   --- Fraction of mothers to mutate (EAR light)
    % V          --- 0.1   --- Fraction of decision variables to mutate
    % Cycles     --- 2     --- Maximum IVF cycles per generation
    % N_Offspring --- 1   --- Number of offspring per SBX crossover
    % EARN       --- 0    --- 0: EAR mode, 1: EARN mode

    %------------------------------- Reference --------------------------------
    % IVF/SPEA2 v2: incorporates dissimilar father per mother (H1) and
    % collective continuation criterion (H2), validated through a 3-phase
    % ablation study (see docs/IVFSPEA2_KNOWLEDGE_BASE.md).
    %
    % Base algorithm: E. Zitzler, M. Laumanns, and L. Thiele, SPEA2:
    % Improving the strength Pareto evolutionary algorithm, 2001.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [C, R, M, V, Cycles, N_Offspring, EARN] = ...
                Algorithm.ParameterSet(0.12, 0.225, 0.3, 0.1, 2, 1, 0);

            %% Generate random initial population
            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = CalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % IVF phase (v2: dissimilar father + collective criterion)
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V2(Problem, Population, Fitness, Forca, Distancia, ...
                         R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                         EARN, SPEA2_Gen);

                [Fitness, ~, ~] = CalFitness(Population.objs);

                % Generate offspring via Tournament Selection + GA operators
                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring  = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end
