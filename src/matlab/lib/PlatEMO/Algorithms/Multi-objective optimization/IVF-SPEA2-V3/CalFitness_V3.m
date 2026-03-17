function [Fitness, Forca, Distancia, DistMatrix] = CalFitness_V3(PopObj)
% CalFitness_V3 - SPEA2 fitness with reusable distances and partial k-NN.

%------------------------------- Copyright --------------------------------
% Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
% research purposes. All publications which use this platform or any code
% in the platform should acknowledge the use of "PlatEMO" and reference "Ye
% Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
% for evolutionary multi-objective optimization [educational forum], IEEE
% Computational Intelligence Magazine, 2017, 12(4): 73-87".
%--------------------------------------------------------------------------

    N = size(PopObj, 1);
    if N == 0
        Fitness = zeros(1, 0);
        Forca = Fitness;
        Distancia = zeros(0, 1);
        DistMatrix = zeros(0);
        return;
    end

    %% Detect the dominance relation between each two solutions
    Dominate = false(N);
    for i = 1 : N-1
        Remaining = PopObj(i+1:N, :);
        less = bsxfun(@lt, PopObj(i, :), Remaining);
        greater = bsxfun(@gt, PopObj(i, :), Remaining);
        i_dom_j = all(~greater, 2) & any(less, 2);
        j_dom_i = all(~less, 2) & any(greater, 2);
        Dominate(i, i+1:N) = i_dom_j';
        Dominate(i+1:N, i) = j_dom_i;
    end

    %% Calculate S(i) and R(i)
    S = sum(Dominate, 2);
    R = S' * Dominate;

    %% Calculate D(i)
    DistMatrix = PairwiseDistanceMatrix_V3(PopObj);
    k = max(floor(sqrt(N)), 1);
    kSmallest = mink(DistMatrix, k, 2);
    D = 1 ./ (kSmallest(:, k) + 2);

    Forca = R;
    Distancia = D;
    Fitness = R + D';
end

function DistMatrix = PairwiseDistanceMatrix_V3(PopObj)
    N = size(PopObj, 1);
    DistMatrix = pdist2(PopObj, PopObj);
    DistMatrix(1:N+1:end) = inf;
end
