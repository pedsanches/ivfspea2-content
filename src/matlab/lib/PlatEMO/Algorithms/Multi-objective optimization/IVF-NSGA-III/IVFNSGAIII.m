classdef IVFNSGAIII < ALGORITHM
    % <2023> <multi/many> <real/integer/label/binary/permutation> <constrained/none>
    % IVF/NSGA-III: In Vitro Fertilization method coupled to NSGA-III
    %
    % ivf_rate --- 0.10 --- IVF budget: fraction of total evaluations consumed
    % C        --- 0.10 --- Close mothers: fraction of population N
    % Cycles   --- 5    --- Maximum IVF internal recombination cycles

    %------------------------------- Reference --------------------------------
    % S. M. Sampaio, A. Dantas, and C. G. Camilo-Junior, "IVF/NSGA-III: In
    % vitro fertilization method coupled to NSGA-III," in Proceedings of the
    % IEEE Congress on Evolutionary Computation (CEC), 2023, pp. 2066-2073.
    % DOI: 10.1109/CEC53210.2023.10254062
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [ivf_rate, C, Cycles] = Algorithm.ParameterSet(0.10, 0.10, 5);

            %% Generate reference points and initial population
            [Z, Problem.N] = UniformPoint(Problem.N, Problem.M);
            Population     = Problem.Initialization();
            Zmin = min(Population(all(Population.cons<=0,2)).objs, [], 1);

            IVF_Total_FE = 0;

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % IVF phase — cumulative ratio budget trigger (§III-D)
                [IVF_Offspring, IVF_Gen_FE, IVF_Total_FE] = IVF_NSGAIII( ...
                    Problem, Population, Z, Zmin, ...
                    ivf_rate, C, Cycles, IVF_Total_FE);

                % Remaining evaluation budget for NSGA-III operators (§III-D)
                % "evaluations in IVF deducted from host descendants"
                Mating_N = max(Problem.N - IVF_Gen_FE, 0);

                if Mating_N > 0
                    MatingPool   = TournamentSelection(2, Mating_N, ...
                        sum(max(0, Population.cons), 2));
                    GA_Offspring = OperatorGA(Problem, Population(MatingPool));
                else
                    GA_Offspring = [];
                end

                % Transfer: IVF super-individuals + GA offspring →
                % NSGA-III niche preservation selection (§III-C)
                All_Offspring = [IVF_Offspring, GA_Offspring];
                if ~isempty(All_Offspring)
                    feasible_mask = all(All_Offspring.cons <= 0, 2);
                    if any(feasible_mask)
                        Zmin = min([Zmin; All_Offspring(feasible_mask).objs], [], 1);
                    end
                    Population = EnvironmentalSelection( ...
                        [Population, All_Offspring], Problem.N, Z, Zmin);
                end
            end
        end
    end
end
