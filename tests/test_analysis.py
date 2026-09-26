"""Critical temporal integrity and source reconciliation tests (unittest)."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from src.analysis import read_data, model_frame, metrics, NUMERIC, FEATURES, TEST_START
from src.features import add_time_series_features, add_spike_target
from src.models import time_based_split, build_logistic_regression

ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read_data(ROOT)
        cls.panel = model_frame(cls.raw)

    def test_keys_and_periods(self):
        self.assertEqual(len(self.raw), 585)
        self.assertEqual(self.raw.date.nunique(), 39)
        self.assertEqual(set(self.panel.code), {f"{i:02d}" for i in range(1,14)})
        self.assertEqual(self.panel.date.min(), pd.Timestamp("2023-07-01"))

    def test_official_press_release_anchor(self):
        # PCBS February 2026 release reports Gaza monthly change of 37.92%.
        actual = self.raw.loc[(self.raw.code == "0999") & (self.raw.date == "2026-02-01"), "pct_change"].iloc[0]
        self.assertAlmostEqual(actual, 37.92, places=2)

    def test_target_boundary_and_missing(self):
        result = add_spike_target(pd.DataFrame({"pct_change": [9.99,10.,10.01,np.nan,-20.]}),10)
        self.assertEqual(result.is_spike.iloc[:3].tolist(), [0,1,1])
        self.assertTrue(pd.isna(result.is_spike.iloc[3]))
        self.assertEqual(result.is_spike.iloc[4],0)

    def test_future_and_current_outcomes_cannot_change_predictors(self):
        changed = self.raw.copy()
        cutoff = pd.Timestamp("2025-03-01")
        changed.loc[changed.date >= cutoff, "pct_change"] = 999.
        altered = model_frame(changed)
        before = self.panel.loc[self.panel.date <= cutoff, FEATURES].reset_index(drop=True)
        after = altered.loc[altered.date <= cutoff, FEATURES].reset_index(drop=True)
        pd.testing.assert_frame_equal(before, after)

    def test_group_isolation(self):
        changed = self.raw.copy()
        changed.loc[changed.code == "01", "pct_change"] = 1000.
        altered = model_frame(changed)
        pd.testing.assert_frame_equal(self.panel.loc[self.panel.code != "01", FEATURES].reset_index(drop=True),
                                      altered.loc[altered.code != "01", FEATURES].reset_index(drop=True))

    def test_missing_month_and_duplicate_rejected(self):
        group = self.raw[self.raw.code == "01"].copy()
        with self.assertRaisesRegex(ValueError, "complete monthly"):
            add_time_series_features(group.drop(group.index[5]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            add_time_series_features(pd.concat([group,group.iloc[:1]]))

    def test_train_only_preprocessing_and_split(self):
        train,test = time_based_split(add_spike_target(self.panel,10), TEST_START)
        self.assertLess(train.date.max(),test.date.min())
        self.assertEqual((len(train),len(test)),(260,156))
        self.assertFalse(set(train.date) & set(test.date))
        model = build_logistic_regression(NUMERIC,("code",))
        model.fit(train[FEATURES],train.is_spike.astype(int))
        fitted_mean = model.named_steps["preprocess"].named_transformers_["numeric"].mean_.copy()
        np.testing.assert_allclose(fitted_mean,train[NUMERIC].mean())
        model.predict(test[FEATURES])
        np.testing.assert_array_equal(fitted_mean,model.named_steps["preprocess"].named_transformers_["numeric"].mean_)

    def test_confusion_orientation(self):
        result = metrics(np.array([0,0,1,1,1]),np.array([0,1,0,1,1]))
        self.assertEqual([result[k] for k in ["tn","fp","fn","tp"]],[1,1,1,2])
        self.assertAlmostEqual(result["f1"],2/3)


if __name__ == "__main__":
    unittest.main()
