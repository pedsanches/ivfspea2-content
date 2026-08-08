classdef IVFNSGAII < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation> <constrained/none>
    % IVF/NSGA-II: In Vitro Fertilization method coupled to NSGA-II
    %
    % R      --- 0.5 --- IVFm rate: probability of running IVF per generation
    % C      --- 0.07 --- Collect size: fraction of population N
    % Cycles --- 5   --- Maximum IVF internal recombination cycles

    %------------------------------- Reference --------------------------------
    % S. M. Sampaio and C. G. Camilo, "IVF/NSGAII: In vitro fertilization
    % method coupled to NSGAII," in Proceedings of VI Latin American
    % Conference on Computational Intelligence (LA-CCI), Nov. 2017, pp. 1-6.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [R, C, Cycles] = Algorithm.ParameterSet(0.5, 0.07, 5);

            %% Generate random initial population
            Population = Problem.Initialization();
            [~, FrontNo, CrowdDis] = EnvironmentalSelection(Population, Problem.N);

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % IVF phase — probabilistic trigger (§III-D, Table II)
                [IVF_Offspring, IVF_Gen_FE] = IVF_NSGAII( ...
                    Problem, Population, FrontNo, CrowdDis, R, C, Cycles);

                % Remaining evaluation budget for NSGA-II operators
                % "evaluations performed in IVF deducted from host descendants" (§III-D)
                Mating_N = max(Problem.N - IVF_Gen_FE, 0);

                if Mating_N > 0
                    MatingPool   = TournamentSelection(2, Mating_N, FrontNo, -CrowdDis);
                    GA_Offspring = OperatorGA(Problem, Population(MatingPool));
                else
                    GA_Offspring = [];
                end

                % Transfer: super-individuals + GA offspring submitted to
                % NSGA-II ordering and selection (§III-C)
                All_Offspring = [IVF_Offspring, GA_Offspring];
                if ~isempty(All_Offspring)
                    [Population, FrontNo, CrowdDis] = EnvironmentalSelection( ...
                        [Population, All_Offspring], Problem.N);
                end
            end
        end
    end
end
