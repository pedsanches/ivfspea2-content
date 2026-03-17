classdef IVFSPEA2_V4_ADAPTIVE < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVFSPEA2 V2-Ablation: Stagnation-based adaptive trigger (H4)
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
    % Ablation variant: IVF activates only when population stagnation is
    % detected (no improvement in avg fitness over last k=5 generations),
    % subject to the existing budget constraint.
    %--------------------------------------------------------------------------

    methods
        function main(Algorithm, Problem)
            [C, R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit] = ...
                Algorithm.ParameterSet(0.11, 0.1, 0, 0, 3, 1, 1, 0, 0);

            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = CalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            % V4: Track fitness history for stagnation detection
            stagnation_window = 5;
            fitness_history = nan(1, 10000);  % preallocate
            fitness_history(1) = mean(Fitness);

            while Algorithm.NotTerminated(Population)
                % V4: Pass stagnation info to IVF function
                is_stagnating = false;
                if SPEA2_Gen > stagnation_window
                    recent = fitness_history(SPEA2_Gen - stagnation_window:SPEA2_Gen);
                    improvement = recent(1) - recent(end);
                    if improvement < 1e-6
                        is_stagnating = true;
                    end
                end

                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V4_ADAPTIVE(Problem, Population, Fitness, Forca, Distancia, ...
                         R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                         EARN, SPEA2_Gen, N_Obj_Limit, is_stagnating);

                [Fitness, ~, ~] = CalFitness(Population.objs);

                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring  = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = EnvironmentalSelection([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
                fitness_history(SPEA2_Gen) = mean(Fitness);
            end
        end
    end
end
