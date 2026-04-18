function run_controlled_short_benchmark
% run_controlled_short_benchmark
% Controlled, paper-safe short benchmark for runtime and quality comparison.
%
% Runs four algorithms in an isolated sandbox so outputs never touch the
% canonical paper/submission directories:
%   - SPEA2
%   - IVF/SPEA2 v1 (submission baseline profile)
%   - IVF/SPEA2 v2 (C26 profile)
%   - IVF/SPEA2 v3 (same profile as v2)
%
% Metrics captured per run:
%   - IGD
%   - HV
%   - runtime
%
% Environment controls:
%   SHORT_BENCH_TAG      unique folder tag (default: timestamped)
%   SHORT_BENCH_RUNS     runs per config      (default: 6)
%   SHORT_BENCH_RUNBASE  first run id         (default: 9101)
%   SHORT_BENCH_MAXFE    max function evals   (default: 10000)
%   SHORT_BENCH_N        population size      (default: 100)
%   SHORT_BENCH_WORKERS  parallel workers     (default: min(4, local max))
%
% Usage:
%   matlab -batch "addpath('experiments'); run_controlled_short_benchmark"

    PROJECT_ROOT = '/home/pedro/desenvolvimento/ivfspea2';
    PLATEMO_DIR = fullfile(PROJECT_ROOT, 'src', 'matlab', 'lib', 'PlatEMO');
    ALGO_ROOT = fullfile(PLATEMO_DIR, 'Algorithms', 'Multi-objective optimization');
    ORIG_PLATEMO_DIR = pwd;

    original_dir = pwd;
    cleanup_dir = onCleanup(@() cd(original_dir)); %#ok<NASGU>

    tag = strtrim(getenv('SHORT_BENCH_TAG'));
    if isempty(tag)
        tag = ['short_bench_', datestr(now, 'yyyymmdd_HHMMSS')];
    end

    runs_per_config = local_env_number('SHORT_BENCH_RUNS', 6);
    run_base = local_env_number('SHORT_BENCH_RUNBASE', 9101);
    maxFE = local_env_number('SHORT_BENCH_MAXFE', 10000);
    n_pop = local_env_number('SHORT_BENCH_N', 100);
    n_save = 1;

    run_ids = run_base:(run_base + runs_per_config - 1);

    bench_root = fullfile(PROJECT_ROOT, 'data', 'temp', 'controlled_short_benchmark', tag);
    sandbox_dir = fullfile(bench_root, 'sandbox');
    summary_dir = fullfile(bench_root, 'summary');
    log_dir = fullfile(bench_root, 'logs');

    local_ensure_dir(bench_root);
    local_ensure_dir(sandbox_dir);
    local_ensure_dir(fullfile(sandbox_dir, 'Data'));
    local_ensure_dir(summary_dir);
    local_ensure_dir(log_dir);

    benchmark_platemo_dir = fullfile(sandbox_dir, 'platemo_runtime');
    if isfolder(benchmark_platemo_dir)
        rmdir(benchmark_platemo_dir, 's');
    end
    copyfile(PLATEMO_DIR, benchmark_platemo_dir);
    PLATEMO_DIR = benchmark_platemo_dir;
    ALGO_ROOT = fullfile(PLATEMO_DIR, 'Algorithms', 'Multi-objective optimization');

    log_file = fullfile(log_dir, sprintf('benchmark_%s.log', datestr(now, 'yyyymmdd_HHMMSS')));
    diary(log_file);
    cleanup_diary = onCleanup(@() diary('off')); %#ok<NASGU>

    fprintf('=== Controlled Short Benchmark ===\n');
    fprintf('Start: %s\n', datestr(now));
    fprintf('Project root: %s\n', PROJECT_ROOT);
    fprintf('Benchmark tag: %s\n', tag);
    fprintf('Sandbox root: %s\n', bench_root);
    fprintf('Runtime PlatEMO clone: %s\n', PLATEMO_DIR);
    fprintf('Run IDs: %d..%d\n', run_ids(1), run_ids(end));
    fprintf('Runs/config: %d | N: %d | maxFE: %d | save: %d\n\n', ...
        runs_per_config, n_pop, maxFE, n_save);

    addpath(genpath(PLATEMO_DIR));
    cd(PLATEMO_DIR);

    algorithms = local_build_algorithms(ALGO_ROOT);
    local_assert_algorithm_resolution(algorithms, ORIG_PLATEMO_DIR, PLATEMO_DIR);
    benchmark_dirs = {algorithms.AlgoDir};

    problems = local_build_problems();

    config = struct();
    config.tag = tag;
    config.project_root = PROJECT_ROOT;
    config.sandbox_dir = sandbox_dir;
    config.summary_dir = summary_dir;
    config.run_ids = run_ids;
    config.runs_per_config = runs_per_config;
    config.run_base = run_base;
    config.maxFE = maxFE;
    config.N = n_pop;
    config.save = n_save;
    config.algorithms = local_algorithms_for_json(algorithms);
    config.problems = local_problems_for_json(problems);
    local_write_text(fullfile(summary_dir, 'config.json'), jsonencode(config, 'PrettyPrint', true));

    pool = gcp('nocreate');
    created_pool = isempty(pool);
    if created_pool
        workers = local_env_number('SHORT_BENCH_WORKERS', 0);
        cluster = parcluster('Processes');
        if workers <= 0
            workers = min(4, cluster.NumWorkers);
        else
            workers = min(workers, cluster.NumWorkers);
        end
        pool = parpool(cluster, workers);
    end

    fprintf('Parallel workers: %d\n\n', pool.NumWorkers);
    try
        pctRunOnAll('maxNumCompThreads(1);');
    catch
    end

    inventory_rows = cell(0, 8);
    total_errors = 0;
    t_start = tic;

    for pi = 1:numel(problems)
        problem = problems(pi);
        fprintf('--- Problem %s (M=%d, D=%d) ---\n', problem.Name, problem.M, problem.D);

        for ai = 1:numel(algorithms)
            algorithm = algorithms(ai);
            raw_dir = fullfile(sandbox_dir, 'Data', algorithm.ClassName);
            default_data_dir = fullfile(PLATEMO_DIR, 'Data', algorithm.ClassName);
            local_ensure_dir(raw_dir);

            local_sync_run_files(default_data_dir, raw_dir, algorithm.ClassName, ...
                problem.Name, problem.M, problem.D, run_ids);

            existing_runs = local_list_runs(raw_dir, algorithm.ClassName, problem.Name, problem.M, problem.D);
            runs_needed = setdiff(run_ids, existing_runs);

            if isempty(runs_needed)
                fprintf('[SKIP] %s on %s - complete (%d/%d)\n', ...
                    algorithm.Label, problem.Name, numel(existing_runs), runs_per_config);
                inventory_rows(end+1, :) = {algorithm.Label, algorithm.ClassName, problem.Name, ...
                    problem.M, problem.D, numel(existing_runs), runs_per_config, 'OK'}; %#ok<AGROW>
                continue;
            end

            fprintf('[START] %s on %s - missing %d runs\n', ...
                algorithm.Label, problem.Name, numel(runs_needed));
            t_cfg = tic;

            run_errors = cell(1, numel(runs_needed));
            parfor ri = 1:numel(runs_needed)
                run_id = runs_needed(ri);
                try
                    local_prepare_worker(PLATEMO_DIR, benchmark_dirs, algorithm.AlgoDir, sandbox_dir);
                    platemo('algorithm', algorithm.AlgoSpec, ...
                            'problem', problem.Handle, ...
                            'N', n_pop, ...
                            'M', problem.M, ...
                            'D', problem.D, ...
                            'maxFE', maxFE, ...
                            'save', n_save, ...
                            'run', run_id, ...
                            'metName', {'IGD', 'HV'});
                    run_errors{ri} = '';
                catch ME
                    run_errors{ri} = sprintf('run %d: %s', run_id, ME.message);
                end
            end

            failed_idx = find(~cellfun(@isempty, run_errors));
            total_errors = total_errors + numel(failed_idx);
            if ~isempty(failed_idx)
                fprintf('[WARN] %s on %s - %d failures\n', ...
                    algorithm.Label, problem.Name, numel(failed_idx));
                for fi = 1:min(5, numel(failed_idx))
                    fprintf('  %s\n', run_errors{failed_idx(fi)});
                end
            end

            local_sync_run_files(default_data_dir, raw_dir, algorithm.ClassName, ...
                problem.Name, problem.M, problem.D, run_ids);

            existing_runs = local_list_runs(raw_dir, algorithm.ClassName, problem.Name, problem.M, problem.D);
            n_found = numel(intersect(existing_runs, run_ids));
            if n_found >= runs_per_config
                status = 'OK';
            elseif n_found > 0
                status = 'INCOMPLETE';
            else
                status = 'MISSING';
            end

            fprintf('[DONE]  %s on %s - %d/%d (%s) in %.1f s\n', ...
                algorithm.Label, problem.Name, n_found, runs_per_config, status, toc(t_cfg));

            inventory_rows(end+1, :) = {algorithm.Label, algorithm.ClassName, problem.Name, ...
                problem.M, problem.D, n_found, runs_per_config, status}; %#ok<AGROW>
        end
        fprintf('\n');
    end

    elapsed = toc(t_start);
    fprintf('=== Benchmark execution finished in %.1f s ===\n', elapsed);
    fprintf('Total run errors: %d\n\n', total_errors);

    inventory = cell2table(inventory_rows, 'VariableNames', ...
        {'Algorithm', 'ClassName', 'Problem', 'M', 'D', 'FoundRuns', 'ExpectedRuns', 'Status'});
    writetable(inventory, fullfile(summary_dir, 'inventory.csv'));

    per_run = local_collect_per_run_metrics(sandbox_dir, algorithms, problems, run_ids);
    writetable(per_run, fullfile(summary_dir, 'per_run_metrics.csv'));

    by_problem = local_summarize_by_problem(per_run, algorithms, problems, runs_per_config);
    writetable(by_problem, fullfile(summary_dir, 'summary_by_problem.csv'));

    overall = local_summarize_overall(by_problem, algorithms);
    writetable(overall, fullfile(summary_dir, 'summary_overall.csv'));

    local_write_markdown_summary(fullfile(summary_dir, 'summary.md'), config, inventory, by_problem, overall, total_errors);

    fprintf('Summary files written to %s\n', summary_dir);
    fprintf('Log file: %s\n', log_file);

    if created_pool
        delete(pool);
    end
end


function algorithms = local_build_algorithms(algo_root)
    algorithms = struct([]);

    algorithms(1).Label = 'SPEA2';
    algorithms(1).ClassName = 'SPEA2';
    algorithms(1).AlgoDir = fullfile(algo_root, 'SPEA2');
    algorithms(1).AlgoSpec = @SPEA2;

    algorithms(2).Label = 'IVF-SPEA2-v1';
    algorithms(2).ClassName = 'IVFSPEA2';
    algorithms(2).AlgoDir = fullfile(algo_root, 'IVF-SPEA2');
    algorithms(2).AlgoSpec = {@IVFSPEA2, 0.11, 0.10, 0, 0, 3, 1, 1, 0, 0};

    algorithms(3).Label = 'IVF-SPEA2-v2';
    algorithms(3).ClassName = 'IVFSPEA2V2';
    algorithms(3).AlgoDir = fullfile(algo_root, 'IVF-SPEA2-V2');
    algorithms(3).AlgoSpec = {@IVFSPEA2V2, 0.12, 0.225, 0.3, 0.1, 2, 1, 0};

    algorithms(4).Label = 'IVF-SPEA2-v3';
    algorithms(4).ClassName = 'IVFSPEA2V3';
    algorithms(4).AlgoDir = fullfile(algo_root, 'IVF-SPEA2-V3');
    algorithms(4).AlgoSpec = {@IVFSPEA2V3, 0.12, 0.225, 0.3, 0.1, 2, 1, 0};
end


function local_assert_algorithm_resolution(algorithms, orig_platemo_dir, benchmark_platemo_dir)
    assert(~strcmp(orig_platemo_dir, benchmark_platemo_dir), 'Benchmark PlatEMO clone must differ from original path.');
    for i = 1:numel(algorithms)
        resolved = which(algorithms(i).ClassName);
        if isempty(resolved)
            error('Algorithm %s not found on MATLAB path.', algorithms(i).ClassName);
        end
        if ~contains(resolved, benchmark_platemo_dir)
            error('Algorithm %s resolves outside cloned PlatEMO tree: %s', algorithms(i).ClassName, resolved);
        end
    end
end


function problems = local_build_problems()
    problems = struct([]);

    problems(1).Name = 'ZDT1';
    problems(1).Handle = @ZDT1;
    problems(1).M = 2;
    problems(1).D = 30;

    problems(2).Name = 'ZDT3';
    problems(2).Handle = @ZDT3;
    problems(2).M = 2;
    problems(2).D = 30;

    problems(3).Name = 'DTLZ2';
    problems(3).Handle = @DTLZ2;
    problems(3).M = 2;
    problems(3).D = 11;

    problems(4).Name = 'WFG4';
    problems(4).Handle = @WFG4;
    problems(4).M = 2;
    problems(4).D = 11;

    problems(5).Name = 'DTLZ2';
    problems(5).Handle = @DTLZ2;
    problems(5).M = 3;
    problems(5).D = 12;

    problems(6).Name = 'WFG4';
    problems(6).Handle = @WFG4;
    problems(6).M = 3;
    problems(6).D = 12;
end


function local_prepare_worker(platemo_dir, benchmark_dirs, target_dir, sandbox_dir)
    addpath(genpath(platemo_dir));
    local_clear_benchmark_dirs(benchmark_dirs);
    addpath(target_dir, '-begin');
    clear CalFitness EnvironmentalSelection CalFitness_V3 EnvironmentalSelection_V3;
    cd(sandbox_dir);
end


function moved = local_sync_run_files(source_dir, dest_dir, class_name, problem_name, m_obj, d_vars, run_ids)
    moved = 0;
    if ~isfolder(source_dir)
        return;
    end

    local_ensure_dir(dest_dir);
    pattern = sprintf('%s_%s_M%d_D%d_*.mat', class_name, problem_name, m_obj, d_vars);
    files = dir(fullfile(source_dir, pattern));
    for i = 1:numel(files)
        token = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
        if isempty(token)
            continue;
        end

        run_id = str2double(token{1});
        if ~ismember(run_id, run_ids)
            continue;
        end

        source_file = fullfile(source_dir, files(i).name);
        dest_file = fullfile(dest_dir, files(i).name);
        [ok, msg] = movefile(source_file, dest_file, 'f');
        if ~ok
            error('Failed to move benchmark file to sandbox: %s -> %s (%s)', source_file, dest_file, msg);
        end
        moved = moved + 1;
    end
end


function local_clear_benchmark_dirs(benchmark_dirs)
    current_path = regexp(path, pathsep, 'split');
    for i = 1:numel(benchmark_dirs)
        prefix = [benchmark_dirs{i}, filesep];
        mask = strcmp(current_path, benchmark_dirs{i}) | startsWith(current_path, prefix);
        remove_list = current_path(mask);
        for j = 1:numel(remove_list)
            try
                rmpath(remove_list{j});
            catch
            end
        end
    end
end


function runs = local_list_runs(raw_dir, class_name, problem_name, m_obj, d_vars)
    pattern = sprintf('%s_%s_M%d_D%d_*.mat', class_name, problem_name, m_obj, d_vars);
    files = dir(fullfile(raw_dir, pattern));
    runs = zeros(1, numel(files));
    for i = 1:numel(files)
        token = regexp(files(i).name, '_(\d+)\.mat$', 'tokens', 'once');
        if ~isempty(token)
            runs(i) = str2double(token{1});
        end
    end
    runs = unique(runs(runs > 0));
end


function per_run = local_collect_per_run_metrics(sandbox_dir, algorithms, problems, run_ids)
    rows = cell(0, 10);

    for ai = 1:numel(algorithms)
        algorithm = algorithms(ai);
        raw_dir = fullfile(sandbox_dir, 'Data', algorithm.ClassName);

        for pi = 1:numel(problems)
            problem = problems(pi);
            for run_id = run_ids
                mat_path = fullfile(raw_dir, sprintf('%s_%s_M%d_D%d_%d.mat', ...
                    algorithm.ClassName, problem.Name, problem.M, problem.D, run_id));
                if ~isfile(mat_path)
                    continue;
                end

                data = load(mat_path, 'metric');
                igd = local_metric_final(data.metric, 'IGD');
                hv = local_metric_final(data.metric, 'HV');
                runtime_sec = local_metric_final(data.metric, 'runtime');

                rows(end+1, :) = {algorithm.Label, algorithm.ClassName, problem.Name, ...
                    problem.M, problem.D, run_id, igd, hv, runtime_sec, mat_path}; %#ok<AGROW>
            end
        end
    end

    per_run = cell2table(rows, 'VariableNames', ...
        {'Algorithm', 'ClassName', 'Problem', 'M', 'D', 'Run', 'IGD', 'HV', 'RuntimeSec', 'MatPath'});
end


function value = local_metric_final(metric, field_name)
    value = NaN;
    if ~isfield(metric, field_name)
        return;
    end

    raw = metric.(field_name);
    if isnumeric(raw)
        value = raw(end);
    elseif iscell(raw) && ~isempty(raw)
        last = raw{end};
        if isnumeric(last)
            value = last(end);
        end
    end
end


function summary = local_summarize_by_problem(per_run, algorithms, problems, runs_per_config)
    rows = cell(0, 15);

    for pi = 1:numel(problems)
        problem = problems(pi);
        base_mask = strcmp(per_run.Algorithm, 'SPEA2') & strcmp(per_run.Problem, problem.Name) & ...
            per_run.M == problem.M & per_run.D == problem.D;
        base_runtime = median(per_run.RuntimeSec(base_mask), 'omitnan');

        for ai = 1:numel(algorithms)
            algorithm = algorithms(ai);
            mask = strcmp(per_run.Algorithm, algorithm.Label) & strcmp(per_run.Problem, problem.Name) & ...
                per_run.M == problem.M & per_run.D == problem.D;
            subset = per_run(mask, :);

            igd = subset.IGD;
            hv = subset.HV;
            runtime = subset.RuntimeSec;

            runtime_median = median(runtime, 'omitnan');
            rho = runtime_median / base_runtime;
            if strcmp(algorithm.Label, 'SPEA2')
                rho = 1;
            end

            rows(end+1, :) = {algorithm.Label, problem.Name, problem.M, problem.D, height(subset), ...
                runs_per_config, median(igd, 'omitnan'), local_iqr(igd), ...
                median(hv, 'omitnan'), local_iqr(hv), ...
                runtime_median, local_iqr(runtime), rho, base_runtime, ...
                sprintf('%s_M%d_D%d', problem.Name, problem.M, problem.D)}; %#ok<AGROW>
        end
    end

    summary = cell2table(rows, 'VariableNames', ...
        {'Algorithm', 'Problem', 'M', 'D', 'FoundRuns', 'ExpectedRuns', ...
         'IGD_Median', 'IGD_IQR', 'HV_Median', 'HV_IQR', ...
         'Runtime_Median_Sec', 'Runtime_IQR_Sec', 'RhoVsSPEA2', ...
         'SPEA2_Runtime_Median_Sec', 'ProblemKey'});
end


function overall = local_summarize_overall(by_problem, algorithms)
    rows = cell(0, 8);
    for ai = 1:numel(algorithms)
        algorithm = algorithms(ai);
        subset = by_problem(strcmp(by_problem.Algorithm, algorithm.Label), :);

        rows(end+1, :) = {algorithm.Label, height(subset), ...
            median(subset.IGD_Median, 'omitnan'), ...
            median(subset.HV_Median, 'omitnan'), ...
            median(subset.Runtime_Median_Sec, 'omitnan'), ...
            median(subset.RhoVsSPEA2, 'omitnan'), ...
            mean(subset.RhoVsSPEA2, 'omitnan'), ...
            sum(subset.FoundRuns)}; %#ok<AGROW>
    end

    overall = cell2table(rows, 'VariableNames', ...
        {'Algorithm', 'ProblemConfigs', 'MedianOfProblemIGD', 'MedianOfProblemHV', ...
         'MedianOfProblemRuntimeSec', 'MedianRhoVsSPEA2', 'MeanRhoVsSPEA2', 'TotalRunsFound'});
end


function value = local_iqr(x)
    x = x(~isnan(x));
    if isempty(x)
        value = NaN;
    else
        value = iqr(x);
    end
end


function local_write_markdown_summary(file_path, config, inventory, by_problem, overall, total_errors)
    fid = fopen(file_path, 'w');
    assert(fid ~= -1, 'Could not open summary file for writing: %s', file_path);
    cleanup_fid = onCleanup(@() fclose(fid)); %#ok<NASGU>

    fprintf(fid, '# Controlled Short Benchmark\n\n');
    fprintf(fid, '- Tag: `%s`\n', config.tag);
    fprintf(fid, '- Sandbox: `%s`\n', config.sandbox_dir);
    fprintf(fid, '- Summary: `%s`\n', config.summary_dir);
    fprintf(fid, '- Runs per config: `%d`\n', config.runs_per_config);
    fprintf(fid, '- Run IDs: `%d..%d`\n', config.run_ids(1), config.run_ids(end));
    fprintf(fid, '- Population size: `%d`\n', config.N);
    fprintf(fid, '- maxFE: `%d`\n', config.maxFE);
    fprintf(fid, '- Total execution errors: `%d`\n\n', total_errors);

    fprintf(fid, '## Overall\n\n');
    fprintf(fid, '| Algorithm | ProblemConfigs | MedianOfProblemIGD | MedianOfProblemHV | MedianRuntime(s) | MedianRho | MeanRho | TotalRuns |\n');
    fprintf(fid, '|---|---:|---:|---:|---:|---:|---:|---:|\n');
    for i = 1:height(overall)
        fprintf(fid, '| %s | %d | %.6g | %.6g | %.6g | %.6g | %.6g | %d |\n', ...
            overall.Algorithm{i}, overall.ProblemConfigs(i), overall.MedianOfProblemIGD(i), ...
            overall.MedianOfProblemHV(i), overall.MedianOfProblemRuntimeSec(i), ...
            overall.MedianRhoVsSPEA2(i), overall.MeanRhoVsSPEA2(i), overall.TotalRunsFound(i));
    end

    fprintf(fid, '\n## By Problem\n\n');
    fprintf(fid, '| Problem | Algorithm | Runs | IGD median | IGD IQR | HV median | HV IQR | Runtime median(s) | Runtime IQR(s) | Rho vs SPEA2 |\n');
    fprintf(fid, '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n');
    for i = 1:height(by_problem)
        fprintf(fid, '| %s | %s | %d/%d | %.6g | %.6g | %.6g | %.6g | %.6g | %.6g | %.6g |\n', ...
            by_problem.ProblemKey{i}, by_problem.Algorithm{i}, by_problem.FoundRuns(i), ...
            by_problem.ExpectedRuns(i), by_problem.IGD_Median(i), by_problem.IGD_IQR(i), ...
            by_problem.HV_Median(i), by_problem.HV_IQR(i), ...
            by_problem.Runtime_Median_Sec(i), by_problem.Runtime_IQR_Sec(i), ...
            by_problem.RhoVsSPEA2(i));
    end

    fprintf(fid, '\n## Inventory\n\n');
    fprintf(fid, '| Algorithm | Problem | M | D | FoundRuns | ExpectedRuns | Status |\n');
    fprintf(fid, '|---|---|---:|---:|---:|---:|---|\n');
    for i = 1:height(inventory)
        fprintf(fid, '| %s | %s | %d | %d | %d | %d | %s |\n', ...
            inventory.Algorithm{i}, inventory.Problem{i}, inventory.M(i), inventory.D(i), ...
            inventory.FoundRuns(i), inventory.ExpectedRuns(i), inventory.Status{i});
    end
end


function local_ensure_dir(path_str)
    if ~isfolder(path_str)
        mkdir(path_str);
    end
end


function value = local_env_number(name, default_value)
    raw = str2double(getenv(name));
    if isnan(raw) || raw <= 0
        value = default_value;
    else
        value = floor(raw);
    end
end


function local_write_text(file_path, text_value)
    fid = fopen(file_path, 'w');
    assert(fid ~= -1, 'Could not open file for writing: %s', file_path);
    cleanup_fid = onCleanup(@() fclose(fid)); %#ok<NASGU>
    fwrite(fid, text_value);
end


function out = local_algorithms_for_json(algorithms)
    out = struct([]);
    for i = 1:numel(algorithms)
        out(i).Label = algorithms(i).Label; %#ok<AGROW>
        out(i).ClassName = algorithms(i).ClassName; %#ok<AGROW>
        out(i).AlgoDir = algorithms(i).AlgoDir; %#ok<AGROW>
    end
end


function out = local_problems_for_json(problems)
    out = struct([]);
    for i = 1:numel(problems)
        out(i).Name = problems(i).Name; %#ok<AGROW>
        out(i).M = problems(i).M; %#ok<AGROW>
        out(i).D = problems(i).D; %#ok<AGROW>
    end
end
