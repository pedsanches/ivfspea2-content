function [Population, Fitness] = IVFTraceEnvironmentalSelection(Population, N)
    [Fitness, ~, ~] = IVFTraceCalFitness(Population.objs);

    Next = Fitness < 1;
    if sum(Next) < N
        [~, Rank] = sort(Fitness);
        Next(Rank(1:N)) = true;
    elseif sum(Next) > N
        Del = local_truncation(Population(Next).objs, sum(Next) - N);
        Temp = find(Next);
        Next(Temp(Del)) = false;
    end

    Population = Population(Next);
    Fitness = Fitness(Next);
end

function Del = local_truncation(PopObj, K)
    Distance = pdist2(PopObj, PopObj);
    Distance(logical(eye(length(Distance)))) = inf;
    Del = false(1, size(PopObj, 1));
    while sum(Del) < K
        Remain = find(~Del);
        subDist = Distance(Remain, Remain);
        subDist = sort(subDist, 2);
        [~, Rank] = sortrows(subDist);
        Del(Remain(Rank(1))) = true;
        Distance(Remain(Rank(1)), :) = inf;
        Distance(:, Remain(Rank(1))) = inf;
    end
end
