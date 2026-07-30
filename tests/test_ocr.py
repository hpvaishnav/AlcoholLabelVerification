import unittest
from app.services.ocr_service import ocr_service

class TestOCRServiceParsing(unittest.TestCase):

    def test_abv_regex_extraction(self):
        text = "HIGHLAND RESERVE WHISKEY 45.5% ALC/VOL 750 ML"
        parsed = ocr_service._parse_fields_from_text(text)
        self.assertEqual(parsed["alcohol_content"].value, "45.5%")

    def test_proof_regex_extraction(self):
        text = "BOURBON WHISKEY 90 PROOF 750 ML"
        parsed = ocr_service._parse_fields_from_text(text)
        self.assertEqual(parsed["proof"].value, "90")

    def test_net_contents_regex_extraction(self):
        text = "CRAFT IPA 12 FL OZ"
        parsed = ocr_service._parse_fields_from_text(text)
        self.assertEqual(parsed["net_contents"].value, "12 FL OZ")

    def test_government_warning_extraction(self):
        text = "SOME LABEL TEXT GOVERNMENT WARNING: (1) According to the Surgeon General..."
        parsed = ocr_service._parse_fields_from_text(text)
        self.assertTrue(parsed["government_warning"].value.startswith("GOVERNMENT WARNING"))

if __name__ == "__main__":
    unittest.main()
