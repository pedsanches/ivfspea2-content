classdef IVFSPEA2 < ALGORITHM
    % <2024> <multi> <real/integer/label/binary/permutation>
    % Strength Pareto evolutionary algorithm 2
    % C  --- 0.11 ---  Coleta
    % R  --- 0.1  ---  Ratio
    % M  --- 0.5  ---  Quantidade de mães a serem mutadas
    % V  --- 0.5  ---  Quantidade de variáveis de decições a ser mutadas
    % Cycles  --- 3 ---  Máximo de Ciclos
    % S  --- 1 ---  Steady State
    % N_Offspring  --- 1 ---  Número de Filhos gerados pelo SBX
    % EARN  --- 0 ---  0 Caso seja outro EAR, 1 para ser EARN
    % N_Obj_Limit --- 0 --- Limite de posição para assumir Current Father, 0 ativa seleção normal

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
            [C,R, M, V, Cycles, S, N_Offspring, EARN, N_Obj_Limit] = Algorithm.ParameterSet(0.11,0.10,0.5,0.5, 3, 1, 1, 0, 0);

            %% Geração da população inicial aleatória
            Population = Problem.Initialization();
            [Fitness, Forca, Distancia]    = CalFitness(Population.objs);
            
            Mating_N = Problem.N;

            IVF_Gen_FE = 0;
            IVF_Total_FE = 0;
            SPEA2_Gen = 1;

            %%Calcula o tamanho da coleta como um valor inteiro
            % ivf_c_size_p_result = floor(Popultation_Size * ivf_c_size_p);
            % ivf_collect_size = max(ivf_c_size, ivf_c_size_p_result)

            %% Otimização
            while Algorithm.NotTerminated(Population)
                [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF(Problem, Population, Fitness, Forca, Distancia, R, C, M, V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, N_Obj_Limit);

                % Fitness is recalculated inside EnvironmentalSelection
                [Fitness,~,~] = CalFitness(Population.objs);
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