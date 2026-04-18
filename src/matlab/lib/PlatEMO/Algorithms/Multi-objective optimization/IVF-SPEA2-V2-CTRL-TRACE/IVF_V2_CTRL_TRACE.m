function [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V2_CTRL_TRACE( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, TraceAlgorithm, ivf_enabled)

    if ~ivf_enabled
        Zmin = 0;
        IVF_Gen_FE = 0;
        Mating_N = Problem.N;
        return;
    end

    [Population, Zmin, IVF_Gen_FE, IVF_Total_FE, Mating_N] = IVF_V2_TRACE( ...
        Problem, Population, Fitness, Forca, Distancia, ivf_rate, C, M, ...
        V, Cycles, IVF_Total_FE, N_Offspring, EARN, SPEA2_Gen, TraceAlgorithm);
end
