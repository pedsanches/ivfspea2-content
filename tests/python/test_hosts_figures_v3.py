"""
test_hosts_figures_v3.py - Tests for the hosts paper figures v3 bump chart.

Run with: pytest tests/python/test_hosts_figures_v3.py -v
"""

import os
import sys

import numpy as np
import pytest
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "python", "analysis"))

from plot_hosts_figures_v3 import (  # noqa: E402
    compute_block_ranks,
    compute_stratified_wtl,
    load_sensitivity,
    compute_sensitivity_relative,
    load_raw_hosts,
)


class TestComputeBlockRanks:
    """Tests for compute_block_ranks()."""

    @pytest.fixture(scope="class")
    def block_ranks(self):
        """Load block ranks once for all tests in this class."""
        return compute_block_ranks()

    def test_returns_dataframe(self, block_ranks):
        assert isinstance(block_ranks, pd.DataFrame)

    def test_has_mean_rank_column(self, block_ranks):
        assert "mean_rank" in block_ranks.columns

    def test_compute_block_ranks_global(self, block_ranks):
        """Global block must exist with mean_rank in [1.0, 3.0]."""
        assert "Global" in block_ranks.index.get_level_values("block"), (
            "Block 'Global' not found"
        )
        global_ranks = block_ranks.xs("Global", level="block")["mean_rank"]
        assert len(global_ranks) > 0, "No algos in Global block"
        assert global_ranks.min() >= 1.0, f"min rank {global_ranks.min()} < 1.0"
        assert global_ranks.max() <= 3.0, f"max rank {global_ranks.max()} > 3.0"

    def test_compute_block_ranks_m2_m3(self, block_ranks):
        """M=2 and M=3 blocks must both exist."""
        blocks = set(block_ranks.index.get_level_values("block"))
        assert "M=2" in blocks, f"Block 'M=2' not found. Available: {blocks}"
        assert "M=3" in blocks, f"Block 'M=3' not found. Available: {blocks}"

    def test_all_expected_blocks_present(self, block_ranks):
        """All nine analytical blocks must be present."""
        expected = {"Global", "M=2", "M=3", "DTLZ", "WFG", "MaF", "ZDT", "IGD", "HV"}
        blocks = set(block_ranks.index.get_level_values("block"))
        missing = expected - blocks
        assert not missing, f"Missing blocks: {missing}"

    def test_three_algos_per_block(self, block_ranks):
        """Each block must contain exactly 3 algo_label entries."""
        counts = block_ranks.groupby(level="block").size()
        bad = counts[counts != 3]
        assert len(bad) == 0, f"Blocks without exactly 3 algos: {bad.to_dict()}"

    def test_m2_m3_mean_rank_range(self, block_ranks):
        """M=2 and M=3 mean ranks must be in [1.0, 3.0]."""
        for block_name in ("M=2", "M=3"):
            ranks = block_ranks.xs(block_name, level="block")["mean_rank"]
            assert ranks.min() >= 1.0
            assert ranks.max() <= 3.0


class TestComputeStratifiedWtl:
    """Tests for compute_stratified_wtl()."""

    @pytest.fixture(scope="class")
    def wtl(self):
        """Load stratified W/T/L once for all tests in this class."""
        return compute_stratified_wtl("igd")

    def test_compute_stratified_wtl_has_family_strata(self, wtl):
        """Both 'DTLZ' and 'M=2' must appear in the stratum column."""
        strata = set(wtl["stratum"].unique())
        assert "DTLZ" in strata, f"'DTLZ' not found in strata: {strata}"
        assert "M=2" in strata, f"'M=2' not found in strata: {strata}"

    def test_compute_stratified_wtl_counts_sum(self, wtl):
        """W+T+L per (stratum, label) must be > 0."""
        wtl = wtl.copy()
        wtl["total"] = wtl["wins"] + wtl["ties"] + wtl["losses"]
        bad = wtl[wtl["total"] == 0]
        assert len(bad) == 0, f"Found (stratum, label) with zero total:\n{bad}"


class TestLoadSensitivity:
    """Tests for load_sensitivity()."""

    @pytest.fixture(scope="class")
    def sensitivity(self):
        return load_sensitivity()

    def test_load_sensitivity_data(self, sensitivity):
        """Verify required columns Problem, R, C are present."""
        for col in ("Problem", "R", "C"):
            assert col in sensitivity.columns, f"Missing column '{col}'"

    def test_load_sensitivity_has_rows(self, sensitivity):
        """Sensitivity CSV must not be empty."""
        assert len(sensitivity) > 0


class TestComputeSensitivityRelative:
    """Tests for compute_sensitivity_relative()."""

    @pytest.fixture(scope="class")
    def dtlz2_rel(self):
        return compute_sensitivity_relative("DTLZ2")

    def test_sensitivity_relative_igd(self, dtlz2_rel):
        """For DTLZ2, the median rel_igd of baseline rows (min R) should be close to 0.

        DTLZ2 has R=0.0 as baseline. Individual rows vary by C, but the baseline is
        the median across all min-R rows, so the median of rel_igd at min-R must be ~0.
        """
        min_r = dtlz2_rel["R"].min()
        baseline_rows = dtlz2_rel[dtlz2_rel["R"] == min_r]
        assert len(baseline_rows) > 0, f"No baseline rows (R={min_r}) for DTLZ2"
        median_rel_igd = baseline_rows["rel_igd"].median()
        assert abs(median_rel_igd) < 0.01, (
            f"Median rel_igd at baseline R={min_r} is {median_rel_igd:.6f}, expected ~0"
        )

    def test_sensitivity_relative_has_rel_igd_column(self, dtlz2_rel):
        """Output must have rel_igd column."""
        assert "rel_igd" in dtlz2_rel.columns

    def test_sensitivity_relative_active_rows(self, dtlz2_rel):
        """Active rows (R>0) must exist and have finite rel_igd."""
        active = dtlz2_rel[dtlz2_rel["R"] > 0.0]
        assert len(active) > 0, "No active (R>0) rows for DTLZ2"
        assert active["rel_igd"].notna().all(), "Some rel_igd values are NaN"


class TestLoadRawHostsData:
    """Tests for load_raw_hosts()."""

    @pytest.fixture(scope="class")
    def raw(self):
        return load_raw_hosts()

    def test_load_raw_hosts_data(self, raw):
        """Verify required columns algo and IGD are present and data is non-empty."""
        assert isinstance(raw, pd.DataFrame), "Expected a DataFrame"
        assert len(raw) > 0, "Raw hosts data must be non-empty"
        for col in ("algo", "IGD"):
            assert col in raw.columns, f"Missing column '{col}'"

    def test_raw_hosts_has_all_algos(self, raw):
        """All 6 algorithms must be present in the raw data."""
        expected = {"IVFSPEA2", "SPEA2", "IVFNSGAII", "NSGAII", "IVFNSGAIII", "NSGAIII"}
        found = set(raw["algo"].unique())
        missing = expected - found
        assert not missing, f"Missing algorithms in raw data: {missing}"

    def test_raw_hosts_igd_finite(self, raw):
        """IGD values must be finite (no NaN or Inf)."""
        assert raw["IGD"].notna().all(), "Some IGD values are NaN"
        assert np.isfinite(raw["IGD"]).all(), "Some IGD values are not finite"
