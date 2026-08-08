function [IVF_Offspring, IVF_Gen_FE, IVF_Total_FE] = IVF_NSGAIII( ...
        Problem, Population, Z, Zmin, ivf_rate, C, Cycles, IVF_Total_FE)
% IVF_NSGAIII  IVF operator coupled to NSGA-III (AR variant, DE manipulation).
%
% Reference: Sampaio, Dantas & Camilo-Junior, IEEE CEC 2023.
%
% Algorithm decisions (paper-faithful):
%   Budget       : cumulative ratio — IVF_Total_FE / Problem.FE  (§III-D, Table I)
%   Collection   : target niche = max perp distance ("worst coverage")  (§III-A)
%   Father       : solution with max perp distance to its ref line  (§III-A)
%   Mothers      : C closest solutions to father in objective space  (§III-A, Fig. 3)
%   Operator     : AR — no mutation  (§IV "AR operator does not alter genes")
%   Crossover    : DE/current-to-best/0, V_i = X_i + F*(X_father - X_i)  (§III-B, Eq.1)
%   Scale factor : F' = distToX(m)/(distToX(m)+distToX(f))  (§III-B, Fig. 8)
%   Dither       : F  = F' + N(0, |1-F'|/10)  (§III-B, Fig. 9)
%   CR           : 1.0 — offspring always equals mutant vector  (§III-B)
%   Continuation : offspring closer to target niche than current father  (§III-B, Fig. 2)
%   Transfer     : all super-individuals accumulated across cycles  (§III-C)

IVF_Offspring = [];
IVF_Gen_FE    = 0;

%% Budget gate — §III-D "percentage limit of current evaluations consumed by IVF"
if IVF_Total_FE > ivf_rate * Problem.FE
    return;
end

FE_Before = Problem.FE;
PopObjs   = Population.objs;

%% ===== NICHE DISTANCES =====
[d_perp, pi_assoc, PopObj_norm, a_intercept] = NicheDistances(PopObjs, Z, Zmin);

%% ===== COLLECT (§III-A) =====
% "Mark as target niche the niche with the worst coverage"
% = solution with greatest perpendicular distance to its reference line
[~, father_idx]  = max(d_perp);
target_niche_j   = pi_assoc(father_idx);  % reference line index of target niche
Father           = Population(father_idx);

% "Collect mothers neighbouring the target niche"
% = C closest solutions to father in objective space (§III-A, Fig. 3)
NumMothers = max(round(Problem.N * C), 1);
NumMothers = min(NumMothers, Problem.N - 1);

dists_to_father            = sqrt(sum((PopObjs - repmat(PopObjs(father_idx,:), Problem.N, 1)).^2, 2));
dists_to_father(father_idx) = Inf;  % exclude father
[~, mother_sort]           = sort(dists_to_father, 'ascend');
Mothers                    = Population(mother_sort(1:NumMothers));

%% ===== GENETIC MANIPULATION (§III-B) =====
% DE/current-to-best/0: V_i = X_i + F*(X_father - X_i)
% CR = 1.0 → offspring always equals mutant vector

Limite_Maximo_Avals  = Problem.N;
Avaliacoes_Por_Ciclo = NumMothers;
Current_Father       = Father;
Current_Father_norm  = PopObj_norm(father_idx, :);
d_father             = DistToRefLine(Current_Father_norm, Z(target_niche_j,:));

All_Super_Individuals = [];

for cycle = 1:Cycles %#ok<FXUP>
    IVF_Gen_FE = Problem.FE - FE_Before;
    if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
        break;
    end

    %% DE offspring for each mother
    MothersObjs   = Mothers.objs;
    MothersDecs   = Mothers.decs;
    Father_dec    = Current_Father.decs;
    OffspringDecs = zeros(NumMothers, Problem.D);

    for mi = 1:NumMothers
        % Perpendicular distance of this mother to target niche reference line (§III-B, Fig. 8)
        mother_norm = (MothersObjs(mi,:) - Zmin) ./ a_intercept';
        d_mother    = DistToRefLine(mother_norm, Z(target_niche_j,:));

        % Adaptive scale factor F' (§III-B, Fig. 8)
        % F' = distToX(mother) / (distToX(mother) + distToX(father))
        denom   = d_mother + d_father;
        F_prime = 0.5;
        if denom > 1e-10
            F_prime = d_mother / denom;
        end

        % Dither: F = F' + N(0, σ), σ = |1-F'|/10 (§III-B, Fig. 9)
        sigma = abs(1 - F_prime) / 10;
        F     = F_prime + randn() * sigma;

        % DE/current-to-best/0 mutation, CR=1.0 → U = V (§III-B, Eq. 1)
        v = MothersDecs(mi,:) + F .* (Father_dec - MothersDecs(mi,:));
        OffspringDecs(mi,:) = min(max(v, Problem.lower), Problem.upper);
    end

    Offspring  = Problem.Evaluation(OffspringDecs);
    IVF_Gen_FE = Problem.FE - FE_Before;

    All_Super_Individuals = [All_Super_Individuals, Offspring]; %#ok<AGROW>

    % Continuation criterion (§III-B, Fig. 2):
    % "New current father?" = any offspring closer to target niche than current father
    % Use a_intercept from population-level normalization (stable basis; too few
    % offspring to recompute hyperplane here).
    Offs_shifted = Offspring.objs - repmat(Zmin, size(Offspring.objs,1), 1);
    Offs_norm    = Offs_shifted ./ repmat(a_intercept', size(Offspring.objs,1), 1);
    d_offs       = DistToRefLine(Offs_norm, Z(target_niche_j,:));

    [min_d, best_idx] = min(d_offs);

    if min_d < d_father
        % New current father found (§Fig. 2 "New current father? Yes")
        Current_Father      = Offspring(best_idx);
        Current_Father_norm = Offs_norm(best_idx, :);
        d_father            = min_d;
    else
        break;  % no improvement — stop cycles
    end
end

IVF_Offspring = All_Super_Individuals;
IVF_Gen_FE    = Problem.FE - FE_Before;
IVF_Total_FE  = IVF_Total_FE + IVF_Gen_FE;
end


%% ===== PERPENDICULAR DISTANCE TO A REFERENCE LINE =====
function d = DistToRefLine(X_norm, z_j)
% Perpendicular distance from each row of X_norm to reference direction z_j.
%   X_norm : [N x M]  (normalized objectives)
%   z_j    : [1 x M]  (reference point direction)
%   d      : [N x 1]
n_z   = z_j / (norm(z_j) + 1e-10);
norms = sqrt(sum(X_norm.^2, 2));
cos_a = X_norm * n_z' ./ (norms + 1e-10);
d     = norms .* sqrt(max(0, 1 - cos_a.^2));
end
