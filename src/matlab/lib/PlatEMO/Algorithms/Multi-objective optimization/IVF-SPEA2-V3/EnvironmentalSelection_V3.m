function [Population, Fitness] = EnvironmentalSelection_V3(Population, N, Fitness, DistMatrix)
% EnvironmentalSelection_V3 - SPEA2 environmental selection with distance reuse.

%------------------------------- Copyright --------------------------------
% Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
% research purposes. All publications which use this platform or any code
% in the platform should acknowledge the use of "PlatEMO" and reference "Ye
% Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
% for evolutionary multi-objective optimization [educational forum], IEEE
% Computational Intelligence Magazine, 2017, 12(4): 73-87".
%--------------------------------------------------------------------------

    PopObj = Population.objs;
    needDistance = nargin < 4 || isempty(DistMatrix);

    if nargin < 3 || isempty(Fitness)
        [Fitness, ~, ~, DistMatrix] = CalFitness_V3(PopObj);
        needDistance = false;
    end

    Next = Fitness < 1;
    if sum(Next) < N
        [~, Rank] = sort(Fitness, 'ascend');
        Next(Rank(1:min(N, numel(Rank)))) = true;
    elseif sum(Next) > N
        if needDistance
            DistMatrix = PairwiseDistanceMatrix_V3(PopObj);
        end
        Remain = find(Next);
        Del = Truncation_V3(DistMatrix(Remain, Remain), sum(Next) - N);
        Temp = find(Next);
        Next(Temp(Del)) = false;
    end

    Population = Population(Next);
    Fitness = Fitness(Next);
end

function Del = Truncation_V3(Distance, K)
    Distance(1:size(Distance, 1)+1:end) = inf;
    Del = false(1, size(Distance, 1));
    while sum(Del) < K
        Remain = find(~Del);
        subDist = sort(Distance(Remain, Remain), 2);
        [~, Rank] = sortrows(subDist);
        removeIdx = Remain(Rank(1));
        Del(removeIdx) = true;
        Distance(removeIdx, :) = inf;
        Distance(:, removeIdx) = inf;
    end
end

function DistMatrix = PairwiseDistanceMatrix_V3(PopObj)
    N = size(PopObj, 1);
    DistMatrix = pdist2(PopObj, PopObj);
    DistMatrix(1:N+1:end) = inf;
end
