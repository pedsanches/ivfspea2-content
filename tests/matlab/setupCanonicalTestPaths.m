function paths = setupCanonicalTestPaths()
% setupCanonicalTestPaths - Configure canonical MATLAB paths for repository tests.

    project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    legacy_mirror = fullfile(project_root, 'src', 'matlab', 'ivf_spea2');
    platemo_root = fullfile(project_root, 'src', 'matlab', 'lib', 'PlatEMO');
    ivf_v2_path = fullfile(platemo_root, 'Algorithms', ...
        'Multi-objective optimization', 'IVF-SPEA2-V2');
    ivf_v3_path = fullfile(platemo_root, 'Algorithms', ...
        'Multi-objective optimization', 'IVF-SPEA2-V3');

    if contains(path, legacy_mirror)
        rmpath(legacy_mirror);
    end

    addpath(genpath(platemo_root));
    addpath(ivf_v3_path, '-begin');
    addpath(ivf_v2_path, '-begin');

    paths = struct( ...
        'project_root', project_root, ...
        'legacy_mirror', legacy_mirror, ...
        'platemo_root', platemo_root, ...
        'ivf_v2_path', ivf_v2_path, ...
        'ivf_v3_path', ivf_v3_path);
end
