import gzip
import struct
import unittest

import numpy as np

from digitlab.supplementary_data import decode, fingerprints, stratified_split, unique_indices


class SupplementaryDataTests(unittest.TestCase):
    def test_upright_decode_and_malformed_inputs(self):
        image = np.zeros((1, 28, 28), dtype=np.uint8)
        image[0, 3, 17] = 255
        payload = gzip.compress(struct.pack(">IIII", 2051, 1, 28, 28) + image.tobytes())
        decoded = decode(payload, 1, True)
        self.assertEqual(int(decoded[0, 17, 3]), 255)
        for value, count, images in ((payload, 2, True),
                                     (gzip.compress(struct.pack(">II", 2049, 1) + b'\x0a'), 1, False),
                                     (gzip.compress(struct.pack(">II", 2049, 1) + b'\x00\x00'), 1, False)):
            with self.subTest(count=count, images=images), self.assertRaises(ValueError):
                decode(value, count, images)

    def test_duplicates_and_reserved_pixels_are_excluded_before_split(self):
        images = np.zeros((5, 28, 28), dtype=np.uint8)
        images[1, 1, 2] = 7
        images[2] = images[1]
        images[3, 2, 3] = 8
        images[4] = images[3]
        kept = unique_indices(images, fingerprints(images[3:4]))
        np.testing.assert_array_equal(kept, [0, 1])

    def test_stratified_partition_is_reproducible_disjoint_and_excludes_other_indices(self):
        labels = np.repeat(np.arange(10), 8)
        indices = np.array([i for i in range(len(labels)) if i % 8 != 0])
        train, validation = stratified_split(labels, indices, validation_per_class=2, seed=3)
        a, b = stratified_split(labels, indices, validation_per_class=2, seed=3)
        np.testing.assert_array_equal(a, train)
        np.testing.assert_array_equal(b, validation)
        self.assertFalse(set(train) & set(validation))
        self.assertEqual(set(train) | set(validation), set(indices))
        np.testing.assert_array_equal(np.bincount(labels[validation]), np.full(10, 2))


if __name__ == "__main__":
    unittest.main()
