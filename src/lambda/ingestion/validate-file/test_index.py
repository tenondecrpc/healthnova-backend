"""Unit tests for validate-file Lambda.

Run with: python -m pytest src/lambda/ingestion/validate-file/test_index.py
Requires: pytest
"""
import io
import unittest
import zipfile
from unittest.mock import MagicMock, patch, call

import sys
import os

# Allow importing the Lambda module without the common layer installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src', 'layer', 'python-common', 'python'))

# Patch common before importing index
common_mock = MagicMock()
sys.modules['common'] = common_mock
common_mock.get_logger.return_value = MagicMock()

import importlib
import index as validate_file_module


def _make_zip_bytes(filenames: list[str]) -> bytes:
    """Create a minimal ZIP in memory with the given entry names."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name in filenames:
            zf.writestr(name, b"data")
    return buf.getvalue()


class TestS3SeekableStream(unittest.TestCase):
    def setUp(self):
        self.zip_bytes = _make_zip_bytes(["Apple Health Export/exportar.xml", "electrocardiograms/ecg1.csv"])
        self.file_size = len(self.zip_bytes)

    def _make_mock_s3(self):
        """Return an S3 client mock that serves byte ranges from self.zip_bytes."""
        s3 = MagicMock()

        def get_object(**kwargs):
            range_header = kwargs.get('Range', f'bytes=0-{self.file_size - 1}')
            start_str, end_str = range_header.replace('bytes=', '').split('-')
            start = int(start_str)
            end = int(end_str)
            chunk = self.zip_bytes[start:end + 1]
            body = MagicMock()
            body.read.return_value = chunk
            return {'Body': body}

        s3.get_object.side_effect = get_object
        return s3

    def test_stream_reads_only_range_requests_not_full_body(self):
        """Verify get_object is called with Range header — never without."""
        s3 = self._make_mock_s3()
        stream = validate_file_module._S3SeekableStream(s3, 'bucket', 'key', self.file_size)
        zf = zipfile.ZipFile(stream)  # type: ignore[arg-type]
        names = zf.namelist()
        zf.close()

        # Every call to get_object must include a Range header
        for c in s3.get_object.call_args_list:
            self.assertIn('Range', c.kwargs, "get_object called without Range header (full body read)")
        self.assertIn('Apple Health Export/exportar.xml', names)

    def test_stream_seek_tell(self):
        s3 = self._make_mock_s3()
        stream = validate_file_module._S3SeekableStream(s3, 'bucket', 'key', self.file_size)
        stream.seek(10)
        self.assertEqual(stream.tell(), 10)
        stream.seek(-5, 1)
        self.assertEqual(stream.tell(), 5)
        stream.seek(0, 2)
        self.assertEqual(stream.tell(), self.file_size)


class TestValidateFileHandler(unittest.TestCase):
    def setUp(self):
        self.zip_bytes = _make_zip_bytes(["Apple Health Export/exportar.xml"])
        self.file_size = len(self.zip_bytes)

    def _mock_s3(self, file_size: int, zip_bytes: bytes):
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

    def test_valid_zip_passes_validation(self):
        s3 = self._mock_s3(self.file_size, self.zip_bytes)
        with patch.object(validate_file_module, 's3_client', s3):
            result = validate_file_module.handler(
                {'bucket': 'b', 'key': 'exports/u1/ts.zip', 'userId': 'u1', 'jobId': 'ts'},
                None,
            )
        self.assertEqual(result['status'], 'VALIDATED')
        self.assertEqual(result['userId'], 'u1')
        # Verify no full-body read (all get_object calls have Range)
        for c in s3.get_object.call_args_list:
            self.assertIn('Range', c.kwargs)

    def test_file_exceeds_max_size_raises(self):
        s3 = MagicMock()
        s3.head_object.return_value = {'ContentLength': 3 * 1024 * 1024 * 1024}
        with patch.object(validate_file_module, 's3_client', s3):
            with self.assertRaises(ValueError, msg="File exceeds maximum"):
                validate_file_module.handler(
                    {'bucket': 'b', 'key': 'k', 'userId': 'u', 'jobId': 'j'},
                    None,
                )

    def test_missing_export_xml_raises(self):
        zip_bytes = _make_zip_bytes(["other_file.txt"])
        file_size = len(zip_bytes)
        s3 = self._mock_s3(file_size, zip_bytes)
        with patch.object(validate_file_module, 's3_client', s3):
            with self.assertRaises(ValueError, msg="ZIP does not contain"):
                validate_file_module.handler(
                    {'bucket': 'b', 'key': 'k', 'userId': 'u', 'jobId': 'j'},
                    None,
                )


if __name__ == '__main__':
    unittest.main()
