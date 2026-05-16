import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import twitterapi_client  # noqa: E402


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> bool:
        return False

    def read(self) -> bytes:
        return b'{"ok": true}'


class TweetIdExtractionTests(unittest.TestCase):
    def test_extracts_raw_id(self) -> None:
        self.assertEqual(twitterapi_client.extract_tweet_id("1234567890"), "1234567890")

    def test_extracts_x_status_url(self) -> None:
        self.assertEqual(
            twitterapi_client.extract_tweet_id(
                "https://x.com/ZenithTON/status/2046570503801119055?s=20"
            ),
            "2046570503801119055",
        )

    def test_extracts_mobile_twitter_url(self) -> None:
        self.assertEqual(
            twitterapi_client.extract_tweet_id(
                "https://mobile.twitter.com/user/statuses/42"
            ),
            "42",
        )


class ApiKeyTests(unittest.TestCase):
    def test_normalizes_supported_provider_aliases(self) -> None:
        self.assertEqual(
            twitterapi_client.normalize_api_provider("twitterapi.io"),
            "twitterapi_io",
        )
        self.assertEqual(
            twitterapi_client.normalize_api_provider("xquik.com"),
            "xquik",
        )

    def test_reads_env_api_key(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"TWITTERAPI_IO_KEY": "  'real-key'  "},
            clear=True,
        ):
            self.assertEqual(twitterapi_client.get_api_key(None), "real-key")

    def test_rejects_placeholder_api_key(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"TWITTERAPI_IO_KEY": "your_key_here"},
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "placeholder API key"):
                twitterapi_client.get_api_key(None)

    def test_reads_xquik_env_api_key(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"XQUIK_API_KEY": "xquik-key"},
            clear=True,
        ):
            self.assertEqual(
                twitterapi_client.get_api_key(None, "xquik"),
                "xquik-key",
            )

    def test_reads_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_script = temp_path / "scripts" / "twitterapi_client.py"
            fake_script.parent.mkdir()
            fake_script.touch()
            (temp_path / ".env.local").write_text(
                "TWITTERAPI_IO_KEY=local-key\n",
                encoding="utf-8",
            )

            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                twitterapi_client, "__file__", str(fake_script)
            ):
                self.assertEqual(twitterapi_client.get_api_key(None), "local-key")

    def test_reads_xquik_provider_from_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_script = temp_path / "scripts" / "twitterapi_client.py"
            fake_script.parent.mkdir()
            fake_script.touch()
            (temp_path / ".env.local").write_text(
                "X_API_PROVIDER=xquik\nXQUIK_API_KEY=local-xquik-key\n",
                encoding="utf-8",
            )

            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                twitterapi_client, "__file__", str(fake_script)
            ):
                self.assertEqual(twitterapi_client.normalize_api_provider(), "xquik")
                self.assertEqual(
                    twitterapi_client.get_api_key(None),
                    "local-xquik-key",
                )


class UrlBuildTests(unittest.TestCase):
    def test_builds_relative_api_path(self) -> None:
        self.assertEqual(
            twitterapi_client._build_url(
                "/twitter/tweets",
                {"tweet_ids": "123", "includeReplies": False, "cursor": None},
            ),
            "https://api.twitterapi.io/twitter/tweets?tweet_ids=123&includeReplies=false",
        )

    def test_builds_xquik_relative_api_path(self) -> None:
        self.assertEqual(
            twitterapi_client._build_url(
                "/x/tweets",
                {"ids": "123"},
                "xquik",
            ),
            "https://xquik.com/api/v1/x/tweets?ids=123",
        )

    def test_appends_to_existing_query_on_allowed_full_url(self) -> None:
        self.assertEqual(
            twitterapi_client._build_url(
                "https://api.twitterapi.io/twitter/tweets?tweet_ids=123",
                {"includeReplies": True},
            ),
            "https://api.twitterapi.io/twitter/tweets?tweet_ids=123&includeReplies=true",
        )

    def test_appends_to_existing_query_on_allowed_xquik_full_url(self) -> None:
        self.assertEqual(
            twitterapi_client._build_url(
                "https://xquik.com/api/v1/x/tweets?ids=123",
                {"limit": 1},
                "xquik",
            ),
            "https://xquik.com/api/v1/x/tweets?ids=123&limit=1",
        )

    def test_rejects_non_api_full_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "https://api.twitterapi.io"):
            twitterapi_client._build_url("https://example.com/twitter/tweets", {})

    def test_rejects_xquik_full_url_for_default_provider(self) -> None:
        with self.assertRaisesRegex(ValueError, "https://api.twitterapi.io"):
            twitterapi_client._build_url("https://xquik.com/api/v1/x/tweets", {})

    def test_rejects_plain_http_full_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "https://api.twitterapi.io"):
            twitterapi_client._build_url("http://api.twitterapi.io/twitter/tweets", {})

    def test_rejects_unsupported_method_before_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported HTTP method"):
            twitterapi_client.request_json(
                method="TRACE",
                path="/twitter/tweets",
                api_key="real-key",
            )

    def test_request_json_uses_xquik_auth_headers(self) -> None:
        with mock.patch.object(
            twitterapi_client.urllib.request,
            "urlopen",
            return_value=FakeResponse(),
        ) as urlopen:
            result = twitterapi_client.request_json(
                method="GET",
                path="/x/tweets",
                api_key="xquik-key",
                query={"ids": "123"},
                api_provider="xquik",
            )

        self.assertEqual(result, {"ok": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://xquik.com/api/v1/x/tweets?ids=123",
        )
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(headers["x-api-key"], "xquik-key")
        self.assertEqual(headers["xquik-api-contract"], "2026-04-29")


if __name__ == "__main__":
    unittest.main()
