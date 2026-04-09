"""Tests for the EnvComparator class."""

import pytest
from envdiff.comparator import EnvComparator, EnvDifference


class TestEnvComparator:
    """Test suite for EnvComparator."""

    def test_identical_environments(self):
        """Test that identical environments show no differences."""
        source = {"KEY1": "value1", "KEY2": "value2"}
        target = {"KEY1": "value1", "KEY2": "value2"}
        
        comparator = EnvComparator(source, target)
        differences = comparator.compare()
        
        assert len(differences) == 0
        assert not comparator.has_differences()

    def test_missing_keys(self):
        """Test detection of missing keys in target."""
        source = {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}
        target = {"KEY1": "value1"}
        
        comparator = EnvComparator(source, target)
        differences = comparator.compare()
        
        assert len(differences) == 2
        assert comparator.has_differences()
        
        missing = [d for d in differences if d.difference_type == 'missing']
        assert len(missing) == 2
        assert missing[0].key == "KEY2"
        assert missing[1].key == "KEY3"

    def test_extra_keys(self):
        """Test detection of extra keys in target."""
        source = {"KEY1": "value1"}
        target = {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}
        
        comparator = EnvComparator(source, target)
        differences = comparator.compare()
        
        assert len(differences) == 2
        
        extra = [d for d in differences if d.difference_type == 'extra']
        assert len(extra) == 2
        assert extra[0].key == "KEY2"
        assert extra[0].target_value == "value2"

    def test_value_mismatches(self):
        """Test detection of value mismatches."""
        source = {"KEY1": "value1", "KEY2": "production"}
        target = {"KEY1": "value1", "KEY2": "development"}
        
        comparator = EnvComparator(source, target)
        differences = comparator.compare()
        
        assert len(differences) == 1
        assert differences[0].difference_type == 'value_mismatch'
        assert differences[0].key == "KEY2"
        assert differences[0].source_value == "production"
        assert differences[0].target_value == "development"

    def test_mixed_differences(self):
        """Test detection of multiple types of differences."""
        source = {
            "SHARED_KEY": "same_value",
            "CHANGED_KEY": "old_value",
            "MISSING_KEY": "will_be_missing"
        }
        target = {
            "SHARED_KEY": "same_value",
            "CHANGED_KEY": "new_value",
            "EXTRA_KEY": "extra_value"
        }
        
        comparator = EnvComparator(source, target)
        differences = comparator.compare()
        
        assert len(differences) == 3
        
        missing = [d for d in differences if d.difference_type == 'missing']
        extra = [d for d in differences if d.difference_type == 'extra']
        mismatched = [d for d in differences if d.difference_type == 'value_mismatch']
        
        assert len(missing) == 1
        assert len(extra) == 1
        assert len(mismatched) == 1

    def test_empty_environments(self):
        """Test comparison of empty environments."""
        comparator = EnvComparator({}, {})
        differences = comparator.compare()
        
        assert len(differences) == 0
        assert not comparator.has_differences()
