function [Fitness, Forca, Distancia] = CalFitness(PopObj)
    % Calculate the fitness of each solution
    
    %------------------------------- Copyright --------------------------------
    % Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
    % research purposes. All publications which use this platform or any code
    % in the platform should acknowledge the use of "PlatEMO" and reference "Ye
    % Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
    % for evolutionary multi-objective optimization [educational forum], IEEE
    % Computational Intelligence Magazine, 2017, 12(4): 73-87".
    %--------------------------------------------------------------------------
    
        N = size(PopObj,1);
    
        %% Detect the dominance relation between each two solutions (vectorized)
        Dominate = false(N);
        for i = 1 : N-1
            remaining = PopObj(i+1:N, :);
            less    = bsxfun(@lt, PopObj(i,:), remaining);  % i < j per objective
            greater = bsxfun(@gt, PopObj(i,:), remaining);  % i > j per objective
            i_dom_j = all(~greater, 2) & any(less, 2);     % i dominates j
            j_dom_i = all(~less, 2) & any(greater, 2);     % j dominates i
            Dominate(i, i+1:N) = i_dom_j';
            Dominate(i+1:N, i) = j_dom_i;
        end
        
        %% Calculate S(i)
        S = sum(Dominate,2);
        
        %% Calculate R(i)
        R = zeros(1,N);
        for i = 1 : N
            R(i) = sum(S(Dominate(:,i)));
        end
        
        %% Calculate D(i)
        Distance = pdist2(PopObj,PopObj);
        Distance(logical(eye(length(Distance)))) = inf;
        Distance = sort(Distance,2);
        D = 1./(Distance(:,floor(sqrt(N)))+2);

        Forca = R;
        Distancia = D;
        
        %% Calculate the fitnesses
        Fitness = R + D';
    end