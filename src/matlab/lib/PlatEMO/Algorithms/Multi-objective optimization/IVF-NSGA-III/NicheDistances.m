function [d, pi_assoc, PopObj_norm, a_intercept] = NicheDistances(PopObj, Z, Zmin)
% NicheDistances  Perpendicular distances from solutions to NSGA-III reference lines.
%
% Uses the same normalization procedure as NSGA-III EnvironmentalSelection:
% ideal-point shift (Zmin) followed by hyperplane intercept normalization.
% Extracted here so IVF_NSGAIII can access niche distances independently.
%
% Inputs
%   PopObj    [N  x M]  objective values
%   Z         [NZ x M]  reference point directions (unit simplex)
%   Zmin      [1  x M]  ideal point
%
% Outputs
%   d           [N x 1]  min perpendicular distance to nearest reference line
%   pi_assoc    [N x 1]  index of nearest reference line (niche association)
%   PopObj_norm [N x M]  normalized objectives (for reuse)
%   a_intercept [M x 1]  hyperplane intercepts (for reuse in distToX computations)

if isempty(Zmin)
    Zmin = zeros(1, size(PopObj, 2));
end

PopObj_shifted = PopObj - repmat(Zmin, size(PopObj, 1), 1);
[N, M] = size(PopObj_shifted);
NZ     = size(Z, 1);

%% Hyperplane normalization — mirrors EnvironmentalSelection > LastSelection
Extreme = zeros(1, M);
w = zeros(M) + 1e-6 + eye(M);
for i = 1:M
    [~, Extreme(i)] = min(max(PopObj_shifted ./ repmat(w(i,:), N, 1), [], 2));
end
Hyperplane = PopObj_shifted(Extreme, :) \ ones(M, 1);
a = 1 ./ Hyperplane;
if any(isnan(a)) || any(a <= 0)
    a = max(PopObj_shifted, [], 1)';
end
PopObj_norm = PopObj_shifted ./ repmat(a', N, 1);
a_intercept = a;

%% Perpendicular distances to every reference line
Cosine   = 1 - pdist2(PopObj_norm, Z, 'cosine');
Dist_all = repmat(sqrt(sum(PopObj_norm.^2, 2)), 1, NZ) .* ...
           sqrt(max(0, 1 - Cosine.^2));

% For each solution: nearest reference line and its distance
[d, pi_assoc] = min(Dist_all, [], 2);
end
