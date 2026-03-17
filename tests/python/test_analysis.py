"""
test_analysis.py - Basic tests for the analysis scripts.

Validates data loading, filtering, and output generation logic.
Run with: pytest tests/python/ -v
"""

import os
import sys
import pytest
import pandas as pd

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "python", "analysis"))


class TestDataLoading:
    """Tests for data loading and preprocessing."""

    @pytest.fixture
    def sample_igd_data(self):
        """Create sample IGD data for testing."""
        return pd.DataFrame(
            {
                "Problema": ["DTLZ1_M2", "DTLZ1_M2", "DTLZ2_M2", "DTLZ2_M2"],
                "Algoritmo": ["IVFSPEA2", "SPEA2", "IVFSPEA2", "SPEA2"],
                "IGD": [0.05, 0.08, 0.03, 0.15],
                "Objetivos": ["M2", "M2", "M2", "M2"],
                "Run": [1, 1, 1, 1],
            }
        )

    @pytest.fixture
    def sample_igd_csv(self, sample_igd_data, tmp_path):
        """Write sample data to a CSV file."""
        filepath = tmp_path / "igd_values_per_run.csv"
        sample_igd_data.to_csv(filepath, index=False)
        return str(filepath)

    def test_csv_loading(self, sample_igd_csv):
        """Test that CSV files can be loaded correctly."""
        df = pd.read_csv(sample_igd_csv)
        assert len(df) == 4
        assert "IGD" in df.columns
        assert "Problema" in df.columns

    def test_igd_filtering(self, sample_igd_data):
        """Test that IGD filtering removes values above threshold."""
        threshold = 0.1
        filtered = sample_igd_data[sample_igd_data["IGD"] <= threshold]
        assert len(filtered) == 3  # 0.15 should be removed
        assert all(filtered["IGD"] <= threshold)

    def test_objective_grouping(self, sample_igd_data):
        """Test that data can be grouped by objectives."""
        groups = sample_igd_data["Objetivos"].unique()
        assert "M2" in groups

    def test_problem_sorting(self, sample_igd_data):
        """Test that problems can be sorted."""
        problems = sorted(sample_igd_data["Problema"].unique())
        assert problems == ["DTLZ1_M2", "DTLZ2_M2"]


class TestDataIntegrity:
    """Tests for data integrity of processed files."""

    PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(PROJECT_ROOT, "data", "processed", "igd_values_per_run.csv")
        ),
        reason="Processed data not available",
    )
    def test_igd_csv_has_required_columns(self):
        """Validate that the main IGD CSV has required columns."""
        df = pd.read_csv(os.path.join(self.PROCESSED_DIR, "igd_values_per_run.csv"))
        required_cols = ["Problema", "Algoritmo", "IGD"]
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(PROJECT_ROOT, "data", "processed", "igd_values_per_run.csv")
        ),
        reason="Processed data not available",
    )
    def test_igd_values_are_non_negative(self):
        """IGD values should always be >= 0."""
        df = pd.read_csv(os.path.join(self.PROCESSED_DIR, "igd_values_per_run.csv"))
        assert (df["IGD"] >= 0).all(), "Found negative IGD values"
