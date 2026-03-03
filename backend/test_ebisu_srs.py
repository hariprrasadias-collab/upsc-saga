import sys
import os
import unittest
import math

# Add backend to path so we can import app modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.ebisu_srs import predict_recall

class TestEbisuSRS(unittest.TestCase):

    def test_predict_recall_default_params(self):
        """Test recall prediction with default alpha, beta, and halflife."""
        alpha = 3.0
        beta_val = 3.0
        halflife = 1.0 # days

        # At t=0, recall should be 1.0
        recall_0 = predict_recall(alpha, beta_val, halflife, 0)
        self.assertAlmostEqual(recall_0, 1.0)

        # At t=24 hours (1 halflife), the memory has decayed
        recall_24 = predict_recall(alpha, beta_val, halflife, 24)
        self.assertTrue(0.0 < recall_24 < 1.0)

        # At t=48 hours (2 halflifes), the memory has decayed further
        recall_48 = predict_recall(alpha, beta_val, halflife, 48)
        self.assertTrue(0.0 < recall_48 < recall_24)

        # Ensure recall decreases over time
        self.assertTrue(recall_0 > recall_24 > recall_48)

    def test_predict_recall_strong_memory(self):
        """Test recall prediction with strong memory (alpha > beta)."""
        # Compare strong memory vs default memory decay
        recall_strong = predict_recall(4.0, 2.0, 1.0, 24)
        recall_default = predict_recall(3.0, 3.0, 1.0, 24)

        # Strong memory should have higher recall probability
        self.assertTrue(recall_strong > recall_default)

    def test_predict_recall_weak_memory(self):
        """Test recall prediction with weak memory (alpha < beta)."""
        # Compare weak memory vs default memory decay
        recall_weak = predict_recall(2.0, 4.0, 1.0, 24)
        recall_default = predict_recall(3.0, 3.0, 1.0, 24)

        # Weak memory should have lower recall probability
        self.assertTrue(recall_weak < recall_default)

    def test_predict_recall_different_halflife(self):
        """Test recall prediction with different halflifes."""
        alpha = 3.0
        beta_val = 3.0

        # With a longer halflife, memory decays slower
        recall_24_hl1 = predict_recall(alpha, beta_val, 1.0, 24)
        recall_24_hl2 = predict_recall(alpha, beta_val, 2.0, 24)

        self.assertTrue(recall_24_hl2 > recall_24_hl1)

    def test_predict_recall_edge_cases(self):
        """Test recall prediction with edge case inputs."""
        alpha = 3.0
        beta_val = 3.0
        halflife = 1.0

        # Huge elapsed time (should be close to 0)
        recall_huge = predict_recall(alpha, beta_val, halflife, 10000)
        self.assertTrue(0.0 <= recall_huge < 0.0001)

        # Negative elapsed time (ebisu library might handle it as 1.0 or raise an error,
        # but realistically elapsed time is non-negative). Let's test very small elapsed time.
        recall_small = predict_recall(alpha, beta_val, halflife, 0.001)
        self.assertTrue(0.99 < recall_small <= 1.0)

if __name__ == '__main__':
    unittest.main()
