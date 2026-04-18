classdef IVFSPEA2_P2 < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVFSPEA2 Phase 2: Factorial combination of promoted factors
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
    % use_H1     --- 0    --- Enable H1: dissimilar father per mother
    % use_H2     --- 0    --- Enable H2: collective continuation criterion
    % use_H3     --- 0    --- Enable H3: eta_c = 10 (instead of 20)
    % use_H4     --- 0    --- Enable H4: stagnation-based activation

    %------------------------------- Reference --------------------------------
    % Phase 2 factorial design: any combination of the 4 promoted factors
    % (H1, H2, H3, H4) controlled via the last 4 parameters.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            %% Parameter setting
            [C, R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit, ...
             use_H1, use_H2, use_H3, use_H4] = ...
                Algorithm.ParameterSet(0.11, 0.1, 0, 0, 3, 1, 1, 0, 0, ...
                                       0, 0, 0, 0);

            % Convert to logical
            use_H1 = logical(use_H1);
            use_H2 = logical(use_H2);
            use_H3 = logical(use_H3);
            use_H4 = logical(use_H4);

            %% Generate random initial population
            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = CalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            % H4: Track fitness history for stagnation detection
            stagnation_window = 5;
            fitness_history = nan(1, 10000);  % preallocate
            fitness_history(1) = mean(Fitness);

            %% Optimization loop
            while Algorithm.NotTerminated(Population)
                % H4: compute stagnation flag
                is_stagnating = false;
                if use_H4 && SPEA2_Gen > stagnation_window
                    recent = fitness_history(SPEA2_Gen - stagnation_window:SPEA2_Gen);
                    improvement = recent(1) - recent(end);
                    if improvement < 1e-6
                        is_stagnating = true;
                    end
                end

                % IVF phase (combined module)
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_P2_COMBINED(Problem, Population, Fitness, Forca, Distancia, ...
                         R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                         EARN, SPEA2_Gen, N_Obj_Limit, ...
                         use_H1, use_H2, use_H3, use_H4, is_stagnating);

                [Fitness, ~, ~] = CalFitness(Population.objs);

                % Generate offspring via Tournament Selection + GA operators
                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring  = OperatorGA(Problem, Population(MatingPool));

                    % Environmental selection (survival)
                    [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
                fitness_history(SPEA2_Gen) = mean(Fitness);
            end
        end
    end
end
