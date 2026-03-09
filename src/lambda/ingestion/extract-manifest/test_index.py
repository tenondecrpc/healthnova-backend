"""Unit tests for extract-manifest Lambda.

Run with: python -m pytest src/lambda/ingestion/extract-manifest/test_index.py
Requires: pytest
"""
import io
import unittest
import zipfile
from unittest.mock import MagicMock, patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src', 'layer', 'python-common', 'python'))

common_mock = MagicMock()
sys.modules['common'] = common_mock
common_mock.get_logger.return_value = MagicMock()

import index as extract_manifest_module


def _make_zip_bytes(filenames: list[str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name in filenames:
            zf.writestr(name, b"data")
    return buf.getvalue()


class TestExtractManifestHandler(unittest.TestCase):
    def _mock_s3(self, zip_bytes: bytes):
        file_size = len(zip_bytes)
        s3 = MagicMock()
        s3.head_object.return_value = {'ContentLength': file_size}

        def get_object(**kwargs):
            range_header = kwargs.get('Range', f'bytes=0-{file_size - 1}')
            start_str, end_str = range_header.replace('bytes=', '').split('-')
            start, end = int(start_str), int(end_str)
            body = MagicMock()
            body.read.return_value = zip_bytes[start:end + 1]
            return {'Body': body}

        s3.get_object.side_effect = get_object
        return s3

    def test_categorizes_xml_ecg_gpx_files(self):
        zip_bytes = _make_zip_bytes([
            "Apple Health Export/exportar.xml",
            "electrocardiograms/ecg1.csv",
            "electrocardiograms/ecg2.csv",
            "workout-routes/route1.gpx",
            "other.txt",
        ])
        s3 = self._mock_s3(zip_bytes)
        with patch.object(extract_manifest_module, 's3_client', s3):
            result = extract_manifest_module.handler(
                {'bucket': 'b', 'key': 'exports/u1/ts.zip', 'userId': 'u1', 'jobId': 'ts'},
                None,
            )
        self.assertEqual(len(result['xmlFiles']), 1)
        self.assertEqual(len(result['ecgFiles']), 2)
        self.assertEqual(len(result['gpxFiles']), 1)
        self.assertEqual(result['status'], 'PROCESSING')

    def test_reads_only_range_requests_not_full_body(self):
        zip_bytes = _make_zip_bytes(["Apple Health Export/exportar.xml"])
        s3 = self._mock_s3(zip_bytes)
        with patch.object(extract_manifest_module, 's3_client', s3):
            extract_manifest_module.handler(
                {'bucket': 'b', 'key': 'exports/u1/ts.zip', 'userId': 'u1', 'jobId': 'ts'},
                None,
            )
        for c in s3.get_object.call_args_list:
            self.assertIn('Range', c.kwargs, "get_object called without Range (full body read)")

    def test_empty_export_returns_empty_manifests(self):
        zip_bytes = _make_zip_bytes(["Apple Health Export/exportar.xml"])
        s3 = self._mock_s3(zip_bytes)
        with patch.object(extract_manifest_module, 's3_client', s3):
            result = extract_manifest_module.handler(
                {'bucket': 'b', 'key': 'k', 'userId': 'u', 'jobId': 'j'},
                None,
            )
        self.assertEqual(result['ecgFiles'], [])
        self.assertEqual(result['gpxFiles'], [])


if __name__ == '__main__':
    unittest.main()
