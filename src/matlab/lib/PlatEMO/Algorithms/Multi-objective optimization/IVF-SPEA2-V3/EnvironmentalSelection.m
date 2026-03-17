function [Population, Fitness] = EnvironmentalSelection(Population, N, Fitness, DistMatrix)
% EnvironmentalSelection - SPEA2 environmental selection (optimized).
%
%   Accepts optional pre-computed Fitness and DistMatrix to avoid redundant
%   CalFitness and pdist2 calls. When called without these arguments, falls
%   back to computing them internally.
%
%   Usage:
%     [Pop, Fit] = EnvironmentalSelection(Pop, N)                    % legacy
%     [Pop, Fit] = EnvironmentalSelection(Pop, N, Fitness, DistMatrix) % optimized

%------------------------------- Copyright --------------------------------
% Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
% research purposes. All publications which use this platform or any code
% in the platform should acknowledge the use of "PlatEMO" and reference "Ye
% Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
% for evolutionary multi-objective optimization [educational forum], IEEE
% Computational Intelligence Magazine, 2017, 12(4): 73-87".
%--------------------------------------------------------------------------

    %% Calculate fitness if not provided
    if nargin < 3 || isempty(Fitness)
        [Fitness, ~, ~, DistMatrix] = CalFitness(Population.objs);
    end

    %% Environmental selection
    Next = Fitness < 1;
    if sum(Next) < N
        [~, Rank] = sort(Fitness);
        Next(Rank(1:N)) = true;
    elseif sum(Next) > N
        % Reuse pre-computed distance matrix for truncation
        Remain = find(Next);
        Del = Truncation(DistMatrix(Remain, Remain), sum(Next) - N);
        Temp = find(Next);
        Next(Temp(Del)) = false;
    end
    % Population for next generation
    Population = Population(Next);
    Fitness    = Fitness(Next);
end

function Del = Truncation(Distance, K)
% Select part of the solutions by truncation using pre-computed distances

    Distance(logical(eye(size(Distance,1)))) = inf;
    Del = false(1, size(Distance, 1));
    while sum(Del) < K
        Remain   = find(~Del);
        subDist  = Distance(Remain, Remain);
        subDist  = sort(subDist, 2);
        [~, Rank] = sortrows(subDist);
        Del(Remain(Rank(1))) = true;
        % Invalidate removed individual to avoid sub-matrix reallocation
        Distance(Remain(Rank(1)), :) = inf;
        Distance(:, Remain(Rank(1))) = inf;
    end
end
