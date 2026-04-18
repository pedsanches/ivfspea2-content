function [Fitness, Forca, Distancia] = IVFTraceCalFitness(PopObj)
    N = size(PopObj, 1);

    Dominate = false(N);
    for i = 1:N-1
        remaining = PopObj(i+1:N, :);
        less = bsxfun(@lt, PopObj(i, :), remaining);
        greater = bsxfun(@gt, PopObj(i, :), remaining);
        i_dom_j = all(~greater, 2) & any(less, 2);
        j_dom_i = all(~less, 2) & any(greater, 2);
        Dominate(i, i+1:N) = i_dom_j';
        Dominate(i+1:N, i) = j_dom_i;
    end

    S = sum(Dominate, 2);
    R = zeros(1, N);
    for i = 1:N
        R(i) = sum(S(Dominate(:, i)));
    end

    Distance = pdist2(PopObj, PopObj);
    Distance(logical(eye(length(Distance)))) = inf;
    Distance = sort(Distance, 2);
    D = 1 ./ (Distance(:, floor(sqrt(N))) + 2);

    Forca = R;
    Distancia = D;
    Fitness = R + D';
end
