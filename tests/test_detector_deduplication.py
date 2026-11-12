"""Regression checks for the one model-input change; no model download needed."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import detector
import stylometry

ROOT = Path(__file__).resolve().parents[1]


class SentenceDeduplicationTests(unittest.TestCase):
    def test_repeated_human_paragraph_recovers_original_model_input(self):
        report = json.loads((ROOT/'results/attack_run_2026-11-11_1852_before.json').read_text())
        inputs = {c['attack']['id']: c['attack']['body']['text'] for c in report['requests'] if isinstance(c['attack'].get('body'),dict) and isinstance(c['attack']['body'].get('text'),str)}
        self.assertEqual(detector._deduplicate_sentences(inputs['MF08']), inputs['FP01'])
        original_style = stylometry.style_signal(inputs['MF08'])
        with patch.object(detector, 'perplexity', return_value=45.0) as ppl:
            self.assertEqual(detector.model_signal(inputs['MF08']), 0.5)
        ppl.assert_called_once_with(inputs['FP01'])
        self.assertEqual(stylometry.style_signal(inputs['MF08']), original_style)

    def test_no_duplicates_preserve_whitespace_and_unicode_exactly(self):
        text = '  A different sentence.\n\nنص عربي مختلف!\tLast thought?  '
        self.assertEqual(detector._deduplicate_sentences(text), text)

    def test_exact_matching_preserves_case_punctuation_and_first_order(self):
        text = 'Run. Walk! Run. run. Walk? Walk!'
        expected = 'Run. Walk! run. Walk?'
        self.assertEqual(detector._deduplicate_sentences(text), expected)
        self.assertEqual(detector._deduplicate_sentences(expected), expected)

    def test_nonsentence_inputs_are_unchanged(self):
        for text in ['', 'a'*4000, '🙂'*20, '\x00\x01 test', 'No sentence boundary here']:
            with self.subTest(text=text[:20]):
                self.assertEqual(detector._deduplicate_sentences(text), text)

    def test_nonrepeated_input_uses_original_perplexity_argument(self):
        text = 'This is unchanged. A second sentence!'
        with patch.object(detector, 'perplexity', return_value=45.0) as ppl:
            self.assertEqual(detector.model_signal(text), 0.5)
        ppl.assert_called_once_with(text)


if __name__ == '__main__':
    unittest.main()
