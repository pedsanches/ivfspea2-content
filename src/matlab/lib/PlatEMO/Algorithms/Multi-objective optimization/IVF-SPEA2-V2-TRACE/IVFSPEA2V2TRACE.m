classdef IVFSPEA2V2TRACE < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % IVF/SPEA2 v2 trace variant for mechanistic case studies.
    %
    % Parameters 1..7 match IVFSPEA2V2.
    % TraceCapturePopulation --- 0 --- 0: summary trace, 1: store pre/post-IVF populations

    properties
        TraceCycles = {}
        TraceParameters = struct()
        TraceCapturePopulation = false
    end

    methods
        function main(Algorithm, Problem)
            [C, R, M, V, Cycles, N_Offspring, EARN, TraceCapturePopulation] = ...
                Algorithm.ParameterSet(0.12, 0.225, 0.3, 0.1, 2, 1, 0, 0);

            Algorithm.TraceCycles = {};
            Algorithm.TraceCapturePopulation = logical(TraceCapturePopulation);
            Algorithm.TraceParameters = struct( ...
                'collection_rate', C, ...
                'ivf_activation_ratio', R, ...
                'mother_mutation_fraction', M, ...
                'variable_mutation_fraction', V, ...
                'max_ivf_cycles', Cycles, ...
                'offspring_per_mother', N_Offspring, ...
                'exploration_mode', EARN, ...
                'capture_population', Algorithm.TraceCapturePopulation);

            Population = Problem.Initialization();
            [Fitness, Forca, Distancia] = IVFTraceCalFitness(Population.objs);

            Mating_N = Problem.N;
            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            while Algorithm.NotTerminated(Population)
                [Population, ~, IVF_Gen_FE, IVF_Total_FE, Mating_N] = ...
                    IVF_V2_TRACE(Problem, Population, Fitness, Forca, Distancia, ...
                        R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, ...
                        EARN, SPEA2_Gen, Algorithm);

                [Fitness, ~, ~] = IVFTraceCalFitness(Population.objs);

                if Mating_N > 0
                    MatingPool = TournamentSelection(2, Mating_N, Fitness);
                    Offspring = OperatorGA(Problem, Population(MatingPool));
                    [Population, Fitness] = IVFTraceEnvironmentalSelection([Population, Offspring], Problem.N);
                end

                SPEA2_Gen = SPEA2_Gen + 1;
            end
        end
    end
end
