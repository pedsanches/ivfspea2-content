function [IVF_Offspring, IVF_Gen_FE] = IVF_NSGAII( ...
        Problem, Population, FrontNo, CrowdDis, R, C, Cycles)
% IVF_NSGAII  IVF operator coupled to NSGA-II (AR variant — no mother mutation).
%
% Reference: S. M. Sampaio and C. G. Camilo, "IVF/NSGAII," LA-CCI 2017.
%
% Algorithm decisions (paper-faithful):
%   Budget gate : per-generation probability R  (§III-D, Table II)
%   Collection  : NSGA-II sort — rank asc, crowding desc  (§III-A)
%   Father      : best individual in S after NSGA-II sort  (§III-A)
%   Mothers     : remainder of S; AR = no mutation  (§II Table I)
%   Crossover   : SBX one offspring per pair, ηc=15  (§IV-C)
%   Objective B : drawn once per IVF invocation  (§III-B, Fig. 4)
%   Continuation: A better than F on objective B  (§III-B, Fig. 4)
%   Transfer    : all super-individuals accumulated across cycles  (§III-C)

IVF_Offspring = [];
IVF_Gen_FE    = 0;

%% Budget gate — §III-D "probability R per generation"
if rand() > R
    return;
end

FE_Before = Problem.FE;

%% ===== COLLECT (§III-A) =====
% "sorted by ranking of non-dominance (ascending order) and
%  by crowding distance (decreasing order)"
FrontNoCol  = FrontNo(:);
CrowdDisCol = CrowdDis(:);
[~, SortIdx] = sortrows([FrontNoCol, -CrowdDisCol], [1, 2]);

NumCollect = max(round(Problem.N * C), 2);  % at least father + 1 mother
NumCollect = min(NumCollect, Problem.N);
S_idx = SortIdx(1:NumCollect);

% "assigning a single individual as Father and the others as Mothers" (§III-B)
Father  = Population(S_idx(1));      % best by NSGA-II ordering
Mothers = Population(S_idx(2:end));  % AR: no mutation applied to mothers

%% ===== GENETIC MANIPULATION (§III-B, Fig. 4) =====
% "Draw a variable B to optimize" — drawn once per IVF module invocation (Fig. 4)
obj_B = randi(Problem.M);

Limite_Maximo_Avals  = Problem.N;
Avaliacoes_Por_Ciclo = length(Mothers);
Current_Father       = Father;
All_Super_Individuals = [];

for cycle = 1:Cycles %#ok<FXUP>
    IVF_Gen_FE = Problem.FE - FE_Before;
    if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals
        break;
    end

    % SBX crossover: current father × each mother, ηc=15 (§IV-C)
    OffspringDecs = IVF_SBX_Batch(Current_Father.decs, Mothers.decs, Problem, 15);
    Offspring     = Problem.Evaluation(OffspringDecs);
    IVF_Gen_FE    = Problem.FE - FE_Before;

    % Accumulate super-individuals (§III-C "transfer more than one super individual")
    All_Super_Individuals = [All_Super_Individuals, Offspring]; %#ok<AGROW>

    % "Sort O by objective B, get best individual A" (Fig. 4)
    OffsObjs = Offspring.objs;  % extract matrix before 2-D indexing (PlatEMO object array)
    [~, best_idx] = min(OffsObjs(:, obj_B));
    A = Offspring(best_idx);

    % "A better than F?" — compare on objective B (Fig. 4)
    % Extract objs vectors before indexing: SOLUTION/objs is a method, so
    % A.objs(k) would be parsed as objs(A,k) — too many args.
    A_objs      = A.objs;
    Father_objs = Current_Father.objs;
    if A_objs(obj_B) < Father_objs(obj_B)
        Current_Father = A;  % "F = A, new cycle"
    else
        break;               % "Terminate = True"
    end
end

IVF_Offspring = All_Super_Individuals;
IVF_Gen_FE    = Problem.FE - FE_Before;
end


%% ===== SBX BATCH: father × all mothers, one offspring per pair =====
function OffspringDecs = IVF_SBX_Batch(Father_dec, Mothers_decs, Problem, disC)
% SBX between one father (broadcast) and each mother.
%   Father_dec   : [1 x D]
%   Mothers_decs : [N x D]
%   Returns      : [N x D] offspring decision variables

proC = 1;
[N, D]  = size(Mothers_decs);
Fathers = repmat(Father_dec, N, 1);

beta    = zeros(N, D);
mu      = rand(N, D);
beta(mu <= 0.5) = (2 .* mu(mu <= 0.5)) .^ (1 / (disC + 1));
beta(mu >  0.5) = (2 - 2 .* mu(mu > 0.5)) .^ (-1 / (disC + 1));
beta = beta .* (-1) .^ randi([0, 1], N, D);
beta(rand(N, D) < 0.5) = 1;
beta(repmat(rand(N, 1) > proC, 1, D)) = 1;

% One child per pair — randomly choose + or - branch (§IVF.m pattern)
signs         = (-1) .^ randi([0, 1], N, 1);
MeanParent    = (Fathers + Mothers_decs) / 2;
DiffParent    = (Fathers - Mothers_decs) / 2;
OffspringDecs = MeanParent + repmat(signs, 1, D) .* beta .* DiffParent;

Lower         = repmat(Problem.lower, N, 1);
Upper         = repmat(Problem.upper, N, 1);
OffspringDecs = min(max(OffspringDecs, Lower), Upper);
end
