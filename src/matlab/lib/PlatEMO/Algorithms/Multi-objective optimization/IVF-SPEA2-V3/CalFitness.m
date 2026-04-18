function [Fitness, Forca, Distancia, DistMatrix] = CalFitness(PopObj)
% CalFitness - SPEA2 fitness with optimized distance computation.
%
%   Returns the full distance matrix (DistMatrix) so it can be reused by
%   EnvironmentalSelection/Truncation, avoiding redundant pdist2 calls.
%   Uses partial sort (mink) instead of full sort to find the k-th nearest
%   neighbour, reducing from O(N^2 log N) to O(N^2 k) where k = sqrt(N).

%------------------------------- Copyright --------------------------------
% Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
% research purposes. All publications which use this platform or any code
% in the platform should acknowledge the use of "PlatEMO" and reference "Ye
% Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
% for evolutionary multi-objective optimization [educational forum], IEEE
% Computational Intelligence Magazine, 2017, 12(4): 73-87".
%--------------------------------------------------------------------------

    N = size(PopObj, 1);

    %% Detect the dominance relation between each two solutions (vectorized)
    Dominate = false(N);
    for i = 1 : N-1
        remaining = PopObj(i+1:N, :);
        less    = bsxfun(@lt, PopObj(i,:), remaining);
        greater = bsxfun(@gt, PopObj(i,:), remaining);
        i_dom_j = all(~greater, 2) & any(less, 2);
        j_dom_i = all(~less, 2) & any(greater, 2);
        Dominate(i, i+1:N) = i_dom_j';
        Dominate(i+1:N, i) = j_dom_i;
    end

    %% Calculate S(i)
    S = sum(Dominate, 2);

    %% Calculate R(i)
    R = zeros(1, N);
    for i = 1 : N
        R(i) = sum(S(Dominate(:,i)));
    end

    %% Calculate D(i) using partial sort (mink)
    DistMatrix = pdist2(PopObj, PopObj);
    DistMatrix(logical(eye(N))) = inf;

    k = floor(sqrt(N));
    k = max(k, 1);  % safety for very small populations

    % mink returns the k smallest values per column; we need per row
    kSmallest = mink(DistMatrix, k, 2);  % [N x k] matrix
    D = 1 ./ (kSmallest(:, k) + 2);

    Forca = R;
    Distancia = D;

    %% Calculate the fitnesses
    Fitness = R + D';
end
