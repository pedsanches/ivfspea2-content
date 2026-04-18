%% process_engineering_suite.m
% Robust post-processing for the engineering validation suite.
%
% Core rules:
% - Use common run IDs across all algorithms per problem.
% - Recompute IGD against empirical PF (union of feasible points).
% - Recompute HV from final populations (problem GetOptimum reference).
% - Report Wilcoxon symbols from IVF/SPEA2 perspective.
%
% Environment controls:
%   ENG_SUITE_STAGE       = SCREEN | MAIN         (default: MAIN)
%   ENG_SUITE_TARGET_RUNS = positive integer      (defaults: SCREEN=10, MAIN=60)
%   ENG_SUITE_PROBLEMS_FILE = CSV path with columns Problem,M (optional)
%                             If provided, overrides built-in problem lists.
%
% Usage:
%   matlab -batch "run('experiments/process_engineering_suite.m')"
%   ENG_SUITE_STAGE=SCREEN ENG_SUITE_PROBLEMS_FILE=config/engineering_candidates_rwmop_m23.csv \
%     matlab -batch "run('experiments/process_engineering_suite.m')"

%% Paths
project_root = '/home/pedro/desenvolvimento/ivfspea2';
platemo_dir  = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
addpath(genpath(platemo_dir));

%% Controls
stage = upper(strtrim(getenv('ENG_SUITE_STAGE')));
if isempty(stage)
    stage = 'MAIN';
end

switch stage
    case 'SCREEN'
        target_runs_default = 10;
        problems = {
            'RWMOP20', 2;
            'RWMOP13', 3;
            'RWMOP8',  3;
            'RWMOP24', 3;
            'RWMOP21', 2;
            'RWMOP29', 2;
        };
        search_dirs = {
            fullfile(project_root, 'data', 'engineering_screening')
        };
        output_dir = fullfile(project_root, 'results', 'engineering_screening');
    case 'MAIN'
        target_runs_default = 60;
        problems = {
            'RWMOP9',  2;
            'RWMOP21', 2;
            'RWMOP8',  3;
        };
        search_dirs = {
            fullfile(project_root, 'data', 'engineering_suite')
        };
        output_dir = fullfile(project_root, 'results', 'engineering_suite');
    otherwise
        error('Invalid ENG_SUITE_STAGE=%s', stage);
end

problems_file = strtrim(getenv('ENG_SUITE_PROBLEMS_FILE'));
if ~isempty(problems_file)
    problems = local_load_problem_list(problems_file, project_root);
end

target_runs = str2double(getenv('ENG_SUITE_TARGET_RUNS'));
if isnan(target_runs) || target_runs <= 0
    target_runs = target_runs_default;
end

if ~isfolder(output_dir)
    mkdir(output_dir);
end

%% Algorithms
algorithms = {
    'IVFSPEA2',  'IVF/SPEA2';
    'SPEA2',     'SPEA2';
    'MFOSPEA2',  'MFO/SPEA2';
    'SPEA2SDE',  'SPEA2+SDE';
    'NSGAII',    'NSGA-II';
    'NSGAIII',   'NSGA-III';
    'MOEAD',     'MOEA/D';
    'AGEMOEAII', 'AGE-MOEA-II';
    'ARMOEA',    'AR-MOEA';
};

ref_algo = 'IVFSPEA2';

%% Containers
raw_rows = {};
summary_rows = {};
pairwise_rows = {};

fprintf('=== Engineering suite post-processing (%s) ===\n', stage);
fprintf('Target common runs/problem: %d\n', target_runs);
fprintf('Problems: %d\n', size(problems,1));
if ~isempty(problems_file)
    fprintf('Problem list source: %s\n', problems_file);
end

for pi = 1:size(problems,1)
    problem_name = problems{pi,1};
    M_obj = problems{pi,2};
    fprintf('\n--- %s (M=%d) ---\n', problem_name, M_obj);

    % Discover available run IDs per algorithm
    run_ids_per_algo = cell(size(algorithms,1),1);
    file_map_per_algo = cell(size(algorithms,1),1);
    for ai = 1:size(algorithms,1)
        algo_name = algorithms{ai,1};
        [runs, fmap] = local_collect_run_files(search_dirs, algo_name, problem_name, M_obj);
        run_ids_per_algo{ai} = runs;
        file_map_per_algo{ai} = fmap;
        fprintf('  %-11s runs found: %d\n', algo_name, numel(runs));
    end

    common_runs = run_ids_per_algo{1};
    for ai = 2:size(algorithms,1)
        common_runs = intersect(common_runs, run_ids_per_algo{ai});
    end
    common_runs = sort(common_runs);

    if isempty(common_runs)
        fprintf('  [WARN] No common runs across all algorithms. Skipping %s.\n', problem_name);
        continue;
    end

    selected_runs = common_runs(1:min(target_runs, numel(common_runs)));
    fprintf('  Common runs (all algorithms): %d | selected: %d\n', numel(common_runs), numel(selected_runs));

    % Save selected run IDs for provenance
    runs_file = fullfile(output_dir, sprintf('%s_common_runs_%s.csv', lower(problem_name), lower(stage)));
    fid_runs = fopen(runs_file, 'w');
    fprintf(fid_runs, 'Problem,Stage,RunID\n');
    for r = selected_runs
        fprintf(fid_runs, '%s,%s,%d\n', problem_name, stage, r);
    end
    fclose(fid_runs);

    % Load feasible final populations
    run_objs = cell(size(algorithms,1), numel(selected_runs));
    run_cons = cell(size(algorithms,1), numel(selected_runs));
    run_n_total = zeros(size(algorithms,1), numel(selected_runs));
    run_n_feasible = zeros(size(algorithms,1), numel(selected_runs));
    run_file = strings(size(algorithms,1), numel(selected_runs));

    all_feasible_objs = [];

    for ai = 1:size(algorithms,1)
        fmap = file_map_per_algo{ai};
        for ri = 1:numel(selected_runs)
            run_id = selected_runs(ri);
            if ~isKey(fmap, run_id)
                continue;
            end

            fpath = fmap(run_id);
            run_file(ai,ri) = string(fpath);
            try
                d = load(fpath);
                [objs, cons] = local_extract_final(d);
                if isempty(objs)
                    continue;
                end

                run_n_total(ai,ri) = size(objs,1);
                if isempty(cons)
                    feasible = true(size(objs,1),1);
                    cons = zeros(size(objs,1),1);
                else
                    feasible = all(cons <= 0, 2);
                end

                fobjs = objs(feasible,:);
                fcons = cons(feasible,:);
                run_n_feasible(ai,ri) = size(fobjs,1);

                run_objs{ai,ri} = fobjs;
                run_cons{ai,ri} = fcons;

                if ~isempty(fobjs)
                    all_feasible_objs = [all_feasible_objs; fobjs]; %#ok<AGROW>
                end
            catch ME
                fprintf('  [WARN] failed loading %s: %s\n', fpath, ME.message);
            end
        end
    end

    if isempty(all_feasible_objs)
        fprintf('  [WARN] No feasible points collected for %s. Skipping.\n', problem_name);
        continue;
    end

    % Empirical PF from all feasible points
    all_feasible_objs = unique(all_feasible_objs, 'rows');
    front_no = NDSort(all_feasible_objs, 1);
    pf_empirical = all_feasible_objs(front_no == 1, :);

    % Problem reference for HV
    prob = feval(problem_name);
    hv_ref = prob.GetOptimum(10000);
    if size(hv_ref,2) ~= M_obj
        hv_ref = hv_ref(:,1:M_obj);
    end

    % Compute run-level metrics
    igd_vals = nan(size(algorithms,1), numel(selected_runs));
    hv_vals  = nan(size(algorithms,1), numel(selected_runs));

    for ai = 1:size(algorithms,1)
        for ri = 1:numel(selected_runs)
            objs = run_objs{ai,ri};
            cons = run_cons{ai,ri};
            if isempty(objs)
                continue;
            end

            igd_vals(ai,ri) = mean(min(pdist2(pf_empirical, objs), [], 2));
            hv_vals(ai,ri)  = local_hv(objs, cons, hv_ref);
        end
    end

    % Build summary and raw rows
    ref_idx = find(strcmp(algorithms(:,1), ref_algo), 1, 'first');
    ref_igd = igd_vals(ref_idx, :);
    ref_hv  = hv_vals(ref_idx, :);
    ref_igd = ref_igd(~isnan(ref_igd));
    ref_hv  = ref_hv(~isnan(ref_hv));

    igd_plus = 0; igd_eq = 0; igd_minus = 0;
    hv_plus  = 0; hv_eq  = 0; hv_minus  = 0;

    for ai = 1:size(algorithms,1)
        algo_name = algorithms{ai,1};
        disp_name = algorithms{ai,2};

        v_igd = igd_vals(ai,:);
        v_hv  = hv_vals(ai,:);
        v_igd_valid = v_igd(~isnan(v_igd));
        v_hv_valid  = v_hv(~isnan(v_hv));

        med_igd = median(v_igd_valid);
        iqr_igd = iqr(v_igd_valid);
        med_hv = median(v_hv_valid);
        iqr_hv = iqr(v_hv_valid);

        if strcmp(algo_name, ref_algo)
            p_igd = NaN; sym_igd = '---';
            p_hv  = NaN; sym_hv  = '---';
        else
            [p_igd, sym_igd] = local_vs_ivf_symbol(ref_igd, v_igd_valid, 'IGD');
            [p_hv,  sym_hv]  = local_vs_ivf_symbol(ref_hv,  v_hv_valid,  'HV');

            switch sym_igd
                case '+'
                    igd_plus = igd_plus + 1;
                case '-'
                    igd_minus = igd_minus + 1;
                case '='
                    igd_eq = igd_eq + 1;
                % 'N/A' intentionally excluded from counts
            end
            switch sym_hv
                case '+'
                    hv_plus = hv_plus + 1;
                case '-'
                    hv_minus = hv_minus + 1;
                case '='
                    hv_eq = hv_eq + 1;
                % 'N/A' intentionally excluded from counts
            end
        end

        feasible_run_rate = sum(run_n_feasible(ai,:) > 0) / numel(selected_runs);

        summary_rows(end+1,:) = { ...
            stage, problem_name, M_obj, algo_name, disp_name, ...
            numel(selected_runs), numel(v_igd_valid), numel(v_hv_valid), ...
            feasible_run_rate, med_igd, iqr_igd, med_hv, iqr_hv, ...
            p_igd, sym_igd, p_hv, sym_hv ...
        }; %#ok<AGROW>

        for ri = 1:numel(selected_runs)
            raw_rows(end+1,:) = { ...
                stage, problem_name, M_obj, algo_name, disp_name, selected_runs(ri), ...
                run_n_total(ai,ri), run_n_feasible(ai,ri), ...
                igd_vals(ai,ri), hv_vals(ai,ri), char(run_file(ai,ri)) ...
            }; %#ok<AGROW>
        end
    end

    pairwise_rows(end+1,:) = {stage, problem_name, M_obj, 'IGD', igd_plus, igd_eq, igd_minus}; %#ok<AGROW>
    pairwise_rows(end+1,:) = {stage, problem_name, M_obj, 'HV',  hv_plus,  hv_eq,  hv_minus}; %#ok<AGROW>

    fprintf('  Pairwise vs IVF (IGD) +/=/-: %d/%d/%d\n', igd_plus, igd_eq, igd_minus);
    fprintf('  Pairwise vs IVF (HV)  +/=/-: %d/%d/%d\n', hv_plus, hv_eq, hv_minus);
end

%% Save CSVs
raw_header = {'Stage','Problem','M','Algorithm','Display','RunID','NTotalPoints','NFeasiblePoints','IGD_PF','HV','SourceFile'};
summary_header = {'Stage','Problem','M','Algorithm','Display','NCommonRuns','NValidIGD','NValidHV','FeasibleRunRate','MedianIGD_PF','IQRIGD_PF','MedianHV','IQRHV','P_vs_IVF_IGD','SymbolIGD','P_vs_IVF_HV','SymbolHV'};
pairwise_header = {'Stage','Problem','M','Metric','Plus','Equal','Minus'};

raw_file = fullfile(output_dir, sprintf('engineering_suite_raw_%s.csv', lower(stage)));
summary_file = fullfile(output_dir, sprintf('engineering_suite_summary_%s.csv', lower(stage)));
pairwise_file = fullfile(output_dir, sprintf('engineering_suite_pairwise_%s.csv', lower(stage)));

local_write_csv(raw_file, raw_header, raw_rows);
local_write_csv(summary_file, summary_header, summary_rows);
local_write_csv(pairwise_file, pairwise_header, pairwise_rows);

%% Save LaTeX table (summary)
tex_file = fullfile(output_dir, sprintf('engineering_suite_table_%s.tex', lower(stage)));
local_write_latex_table(tex_file, summary_rows, summary_header, stage);

fprintf('\nSaved:\n  %s\n  %s\n  %s\n  %s\n', raw_file, summary_file, pairwise_file, tex_file);
fprintf('=== Engineering suite post-processing done ===\n');

%% ===== Local functions =====
function problems = local_load_problem_list(input_path, project_root)
problems = {};

path_try = input_path;
if ~isfile(path_try)
    path_try = fullfile(project_root, input_path);
end
if ~isfile(path_try)
    error('ENG_SUITE_PROBLEMS_FILE not found: %s', input_path);
end

tbl = readtable(path_try, 'TextType', 'string');
required = {'Problem', 'M'};
for i = 1:numel(required)
    if ~ismember(required{i}, tbl.Properties.VariableNames)
        error('Problems CSV must contain columns: Problem,M');
    end
end

has_include = ismember('Include', tbl.Properties.VariableNames);
for i = 1:height(tbl)
    if has_include && ~local_truthy(tbl.Include(i))
        continue;
    end

    p = strtrim(char(tbl.Problem(i)));
    if isempty(p)
        continue;
    end

    m = str2double(string(tbl.M(i)));
    if isnan(m) || m <= 0 || abs(m - round(m)) > 0
        error('Invalid M at row %d in %s', i, path_try);
    end

    problems(end+1,:) = {upper(p), round(m)}; %#ok<AGROW>
end

if isempty(problems)
    error('No valid rows found in %s', path_try);
end
end

function tf = local_truthy(v)
if islogical(v)
    tf = all(v);
    return;
end
if isnumeric(v)
    tf = all(v ~= 0);
    return;
end
s = lower(strtrim(char(string(v))));
tf = ismember(s, {'1','true','yes','y'});
end

function [runs, fmap] = local_collect_run_files(search_dirs, algo_name, problem_name, M_obj)
runs = [];
fmap = containers.Map('KeyType', 'double', 'ValueType', 'char');

prefix = sprintf('%s_%s_M%d_', algo_name, problem_name, M_obj);

all_runs = [];
all_paths = {};
all_datenum = [];

for di = 1:numel(search_dirs)
    root = search_dirs{di};
    if ~isfolder(root)
        continue;
    end
    files = dir(fullfile(root, '**', '*.mat'));
    for i = 1:numel(files)
        fname = files(i).name;
        if ~startsWith(fname, prefix)
            continue;
        end

        tk = regexp(fname, '_(\d+)\.mat$', 'tokens', 'once');
        if isempty(tk)
            continue;
        end

        run_id = str2double(tk{1});
        if isnan(run_id)
            continue;
        end
        all_runs(end+1) = run_id; %#ok<AGROW>
        all_paths{end+1} = fullfile(files(i).folder, files(i).name); %#ok<AGROW>
        all_datenum(end+1) = files(i).datenum; %#ok<AGROW>
    end
end

if isempty(all_runs)
    return;
end

[u_runs, ~, idx] = unique(all_runs);
for k = 1:numel(u_runs)
    pos = find(idx == k);
    [~, best_rel] = max(all_datenum(pos));
    best_pos = pos(best_rel);
    fmap(u_runs(k)) = all_paths{best_pos};
end

runs = sort(cell2mat(keys(fmap)));
end

function [objs, cons] = local_extract_final(data_struct)
objs = [];
cons = [];

if isfield(data_struct, 'result') && iscell(data_struct.result) && ~isempty(data_struct.result)
    final_pop = data_struct.result{end};
    if iscell(final_pop) && ~isempty(final_pop)
        final_pop = final_pop{end};
    end
    if isobject(final_pop)
        try objs = final_pop.objs; end %#ok<TRYNC>
        try cons = final_pop.cons; end %#ok<TRYNC>
    elseif isnumeric(final_pop)
        objs = final_pop;
    end
end

if isempty(objs)
    fields = fieldnames(data_struct);
    for fi = 1:numel(fields)
        val = data_struct.(fields{fi});
        if isstruct(val) && isfield(val, 'objs')
            objs = val.objs;
            if isfield(val, 'cons')
                cons = val.cons;
            end
            return;
        end
    end
end

if ~isempty(objs) && isempty(cons)
    cons = zeros(size(objs,1),1);
end
end

function hv = local_hv(objs, cons, hv_ref)
try
    if isempty(cons)
        cons = zeros(size(objs,1),1);
    end
    dummy_dec = zeros(size(objs,1),1);
    pop = SOLUTION(dummy_dec, objs, cons);
    hv = HV(pop, hv_ref);
catch
    hv = NaN;
end
end

function [p, symbol] = local_vs_ivf_symbol(ref_vals, cmp_vals, metric)
if isempty(ref_vals) || isempty(cmp_vals) || numel(ref_vals) < 3 || numel(cmp_vals) < 3
    p = NaN;
    symbol = 'N/A';
    return;
end

p = ranksum(ref_vals, cmp_vals);
if p >= 0.05
    symbol = '=';
    return;
end

med_ref = median(ref_vals);
med_cmp = median(cmp_vals);

switch metric
    case 'IGD'
        if med_ref < med_cmp
            symbol = '+'; % IVF better (lower IGD)
        else
            symbol = '-';
        end
    case 'HV'
        if med_ref > med_cmp
            symbol = '+'; % IVF better (higher HV)
        else
            symbol = '-';
        end
    otherwise
        symbol = '=';
end
end

function local_write_csv(file_path, header, rows)
fid = fopen(file_path, 'w');
fprintf(fid, '%s\n', strjoin(header, ','));
for i = 1:size(rows,1)
    line = strings(1, numel(header));
    for j = 1:numel(header)
        val = rows{i,j};
        if isnumeric(val)
            if isscalar(val)
                if isnan(val)
                    line(j) = "";
                else
                    line(j) = string(val);
                end
            else
                line(j) = "";
            end
        else
            line(j) = string(val);
        end

        if contains(line(j), ',')
            line(j) = '"' + line(j) + '"';
        end
    end
    fprintf(fid, '%s\n', strjoin(cellstr(line), ','));
end
fclose(fid);
end

function local_write_latex_table(file_path, summary_rows, header, stage)
if isempty(summary_rows)
    fid = fopen(file_path, 'w');
    fprintf(fid, '%% No summary rows available for stage %s\n', stage);
    fclose(fid);
    return;
end

% Column mapping in summary_rows
col_problem = find(strcmp(header, 'Problem'));
col_display = find(strcmp(header, 'Display'));
col_n = find(strcmp(header, 'NCommonRuns'));
col_med_igd = find(strcmp(header, 'MedianIGD_PF'));
col_iqr_igd = find(strcmp(header, 'IQRIGD_PF'));
col_sym_igd = find(strcmp(header, 'SymbolIGD'));
col_med_hv = find(strcmp(header, 'MedianHV'));
col_iqr_hv = find(strcmp(header, 'IQRHV'));
col_sym_hv = find(strcmp(header, 'SymbolHV'));

problems = unique(summary_rows(:, col_problem), 'stable');

fid = fopen(file_path, 'w');
fprintf(fid, '\\begin{table*}[t]\n');
fprintf(fid, '\\centering\\scriptsize\n');
fprintf(fid, '\\caption{Engineering suite (%s): robust metrics with common-run matching. IGD is recomputed against empirical PF per problem. Symbols in vs-IVF columns: $+$ IVF/SPEA2 better, $-$ worse, $=$ no significant difference (Wilcoxon, $\\alpha=0.05$).}\n', stage);
fprintf(fid, '\\label{tab:engineering_suite_%s}\n', lower(stage));
fprintf(fid, '\\resizebox{\\textwidth}{!}{%%\n');
fprintf(fid, '\\begin{tabular}{llrcccc}\n');
fprintf(fid, '\\toprule\n');
fprintf(fid, 'Problem & Algorithm & $n$ & IGD$_{PF}$ median (IQR) & vs IVF (IGD) & HV median (IQR) & vs IVF (HV) \\\\n');
fprintf(fid, '\\midrule\n');

for p = 1:numel(problems)
    prob = problems{p};
    idx = find(strcmp(summary_rows(:, col_problem), prob));
    block = summary_rows(idx, :);

    med_igd_vals = nan(size(block,1),1);
    med_hv_vals = nan(size(block,1),1);
    for i = 1:size(block,1)
        med_igd_vals(i) = block{i, col_med_igd};
        med_hv_vals(i) = block{i, col_med_hv};
    end

    [~, best_igd_idx] = min(med_igd_vals);
    [~, best_hv_idx] = max(med_hv_vals);

    for i = 1:size(block,1)
        disp_name = block{i, col_display};
        n_common = block{i, col_n};
        med_igd = block{i, col_med_igd};
        iqr_igd = block{i, col_iqr_igd};
        sym_igd = block{i, col_sym_igd};
        med_hv = block{i, col_med_hv};
        iqr_hv = block{i, col_iqr_hv};
        sym_hv = block{i, col_sym_hv};

        if isnan(med_igd) || isnan(iqr_igd)
            igd_text = '---';
        else
            igd_text = sprintf('%.4e (%.3e)', med_igd, iqr_igd);
            if i == best_igd_idx
                igd_text = ['\\textbf{', igd_text, '}'];
            end
        end
        if isnan(med_hv) || isnan(iqr_hv)
            hv_text = '---';
        else
            hv_text = sprintf('%.4e (%.3e)', med_hv, iqr_hv);
            if i == best_hv_idx
                hv_text = ['\\textbf{', hv_text, '}'];
            end
        end

        if strcmp(sym_igd, '---'), sym_igd = '---'; end
        if strcmp(sym_hv, '---'), sym_hv = '---'; end

        fprintf(fid, '%s & %s & %d & %s & %s & %s & %s \\\\n', ...
            prob, disp_name, n_common, igd_text, sym_igd, hv_text, sym_hv);
    end

    if p < numel(problems)
        fprintf(fid, '\\midrule\n');
    end
end

fprintf(fid, '\\botrule\n');
fprintf(fid, '\\end{tabular}\n');
fprintf(fid, '}\n');
fprintf(fid, '\\end{table*}\n');
fclose(fid);
end
