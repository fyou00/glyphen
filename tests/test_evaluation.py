"""Uji metrik audit: anotasi kosong tidak boleh dianggap sukses."""

import copy
import unittest

from scripts.evaluate_segmentation import score_review


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.template = {'manifest_sha256': 'manifest', 'source_sha256': {'1': 'scan'},
                         'reviewer': '', 'entries': [
                             {'label': 'lower_a', 'variant': n, 'glyph_sha256': str(n),
                              'correct': None} for n in (1, 2, 3)]}

    def test_no_annotation_has_no_accuracy(self):
        result = score_review(self.template, self.template)
        self.assertIsNone(result['crop_accuracy'])
        self.assertEqual(result['reviewed_boxes'], 0)
        self.assertFalse(result['review_complete'])

    def test_partial_review_uses_reviewed_denominator(self):
        review = copy.deepcopy(self.template)
        review['reviewer'] = 'visual_agent'
        review['entries'][0]['correct'] = True
        review['entries'][1]['correct'] = False
        result = score_review(self.template, review)
        self.assertEqual(result['crop_accuracy'], 0.5)
        self.assertEqual(result['incorrect_boxes'], 1)
        self.assertFalse(result['review_complete'])

    def test_stale_duplicate_unidentified_and_invalid_reviews_fail(self):
        for field, value in [('manifest_sha256', 'stale'), ('source_sha256', {'1': 'other'})]:
            review = {**self.template, field: value}
            with self.assertRaises(ValueError):
                score_review(self.template, review)
        review = copy.deepcopy(self.template)
        review['entries'].append(review['entries'][0])
        with self.assertRaises(ValueError):
            score_review(self.template, review)
        review = copy.deepcopy(self.template)
        review['entries'][0]['correct'] = True
        with self.assertRaises(ValueError):
            score_review(self.template, review)
        review['reviewer'] = 'visual_agent'
        review['entries'][0]['glyph_sha256'] = 'different'
        with self.assertRaises(ValueError):
            score_review(self.template, review)
        for field, value in [('correct', 'true'), ('label', 'unknown')]:
            review = copy.deepcopy(self.template)
            review['reviewer'] = 'visual_agent'
            review['entries'][0][field] = value
            with self.assertRaises(ValueError):
                score_review(self.template, review)


if __name__ == '__main__':
    unittest.main()
