import unittest
from app.comparator import comparator, normalize_text

class TestLabelComparator(unittest.TestCase):

    def test_text_normalization(self):
        self.assertEqual(normalize_text("HIGHLAND RESERVE!"), "highland reserve")
        self.assertEqual(normalize_text("  45.0%   ABV  "), "45.0% abv")

    def test_exact_field_match_pass(self):
        res = comparator.compare_field("Brand Name", "HIGHLAND RESERVE", "HIGHLAND RESERVE", 0.95)
        self.assertEqual(res["status"], "PASS")
        self.assertGreaterEqual(res["match_score"], 0.90)

    def test_fuzzy_field_near_match_review(self):
        # Spelling variation
        res = comparator.compare_field("Brand Name", "EL TEQUILEÑO REPOSADO", "EL TEQUILENO REPOSADO", 0.85)
        self.assertIn(res["status"], ["PASS", "NEEDS REVIEW"])

    def test_mismatched_field_reject(self):
        res = comparator.compare_field("Alcohol Content", "14.8%", "13.5%", 0.95)
        self.assertEqual(res["status"], "REJECT")

    def test_government_warning_strict_pass(self):
        expected = "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
        extracted = expected
        res = comparator.validate_government_warning(expected, extracted)
        self.assertEqual(res["status"], "PASS")

    def test_government_warning_lowercase_reject(self):
        expected = "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL..."
        extracted = "Government Warning: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY."
        res = comparator.validate_government_warning(expected, extracted)
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("ALL CAPS", res["explanation"])

    def test_government_warning_missing_reject(self):
        res = comparator.validate_government_warning("GOVERNMENT WARNING...", "")
        self.assertEqual(res["status"], "REJECT")
        self.assertIn("CRITICAL REGULATORY VIOLATION", res["explanation"])

if __name__ == "__main__":
    unittest.main()
