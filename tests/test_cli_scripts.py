import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import twitterapi_call  # noqa: E402
import twitterapi_fetch  # noqa: E402
import twitterapi_media  # noqa: E402


def run_cli(main_func, argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch.object(sys, "argv", argv), mock.patch(
        "sys.stdout", stdout
    ), mock.patch("sys.stderr", stderr):
        code = main_func()
    return code, stdout.getvalue(), stderr.getvalue()


class TwitterApiCallCliTests(unittest.TestCase):
    def test_get_calls_documented_endpoint(self) -> None:
        with mock.patch.object(
            twitterapi_call, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_call,
            "request_json",
            return_value={"status": "success"},
        ) as request_json:
            code, stdout, stderr = run_cli(
                twitterapi_call.main,
                [
                    "xapi",
                    "--method",
                    "get",
                    "--path",
                    "/oapi/my/info",
                    "--query-json",
                    '{"sample": true}',
                ],
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn('"status": "success"', stdout)
        request_json.assert_called_once_with(
            method="GET",
            path="/oapi/my/info",
            api_key="api-key",
            query={"sample": True},
            body=None,
            api_provider="twitterapi_io",
        )

    def test_get_calls_xquik_endpoint_when_provider_selected(self) -> None:
        with mock.patch.object(
            twitterapi_call, "get_api_key", return_value="api-key"
        ) as get_api_key, mock.patch.object(
            twitterapi_call,
            "request_json",
            return_value={"tweets": [{"id": "123"}]},
        ) as request_json:
            code, stdout, stderr = run_cli(
                twitterapi_call.main,
                [
                    "xapi",
                    "--api-provider",
                    "xquik",
                    "--method",
                    "get",
                    "--path",
                    "/x/tweets",
                    "--query-json",
                    '{"ids": "123"}',
                ],
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn('"tweets"', stdout)
        get_api_key.assert_called_once_with(None, "xquik")
        request_json.assert_called_once_with(
            method="GET",
            path="/x/tweets",
            api_key="api-key",
            query={"ids": "123"},
            body=None,
            api_provider="xquik",
        )

    def test_rejects_mutating_methods_without_explicit_flag(self) -> None:
        for method in ("POST", "PATCH", "PUT", "DELETE"):
            with self.subTest(method=method), mock.patch.object(
                twitterapi_call, "get_api_key"
            ) as get_api_key, mock.patch.object(
                twitterapi_call, "request_json"
            ) as request_json:
                code, _stdout, stderr = run_cli(
                    twitterapi_call.main,
                    [
                        "xapi",
                        "--method",
                        method,
                        "--path",
                        "/twitter/post/create",
                        "--body-json",
                        '{"text": "draft"}',
                    ],
                )

                self.assertEqual(code, 1)
                self.assertIn("--allow-mutation", stderr)
                get_api_key.assert_not_called()
                request_json.assert_not_called()

    def test_allows_mutating_method_with_explicit_flag(self) -> None:
        with mock.patch.object(
            twitterapi_call, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_call,
            "request_json",
            return_value={"status": "success"},
        ) as request_json:
            code, _stdout, stderr = run_cli(
                twitterapi_call.main,
                [
                    "xapi",
                    "--method",
                    "POST",
                    "--path",
                    "/twitter/post/create",
                    "--body-json",
                    '{"text": "draft"}',
                    "--allow-mutation",
                ],
            )

        self.assertEqual(code, 0, stderr)
        request_json.assert_called_once_with(
            method="POST",
            path="/twitter/post/create",
            api_key="api-key",
            query={},
            body={"text": "draft"},
            api_provider="twitterapi_io",
        )

    def test_invalid_query_json_fails_before_request(self) -> None:
        with mock.patch.object(
            twitterapi_call, "get_api_key"
        ) as get_api_key, mock.patch.object(
            twitterapi_call,
            "request_json",
        ) as request_json:
            code, _stdout, stderr = run_cli(
                twitterapi_call.main,
                [
                    "xapi",
                    "--path",
                    "/oapi/my/info",
                    "--query-json",
                    "{not-json}",
                ],
            )

        self.assertEqual(code, 1)
        self.assertIn("Invalid --query-json", stderr)
        get_api_key.assert_not_called()
        request_json.assert_not_called()


class TwitterApiFetchCliTests(unittest.TestCase):
    def test_tweet_mode_calls_tweet_fetcher(self) -> None:
        with mock.patch.object(
            twitterapi_fetch, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_fetch,
            "fetch_tweet",
            return_value={"kind": "tweet", "tweet_id": "123"},
        ) as fetch_tweet:
            code, stdout, stderr = run_cli(
                twitterapi_fetch.main,
                ["xread", "--input", "123", "--mode", "tweet"],
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn('"kind": "tweet"', stdout)
        fetch_tweet.assert_called_once_with("123", "api-key", "twitterapi_io")

    def test_tweet_mode_passes_xquik_provider(self) -> None:
        with mock.patch.object(
            twitterapi_fetch, "get_api_key", return_value="api-key"
        ) as get_api_key, mock.patch.object(
            twitterapi_fetch,
            "fetch_tweet",
            return_value={"kind": "tweet", "tweet_id": "123", "source": "xquik"},
        ) as fetch_tweet:
            code, stdout, stderr = run_cli(
                twitterapi_fetch.main,
                [
                    "xread",
                    "--api-provider",
                    "xquik",
                    "--input",
                    "123",
                    "--mode",
                    "tweet",
                ],
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn('"source": "xquik"', stdout)
        get_api_key.assert_called_once_with(None, "xquik")
        fetch_tweet.assert_called_once_with("123", "api-key", "xquik")

    def test_auto_mode_falls_back_from_article_to_tweet(self) -> None:
        with mock.patch.object(
            twitterapi_fetch, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_fetch,
            "fetch_article",
            side_effect=RuntimeError("Article not found"),
        ) as fetch_article, mock.patch.object(
            twitterapi_fetch,
            "fetch_tweet",
            return_value={"kind": "tweet", "tweet_id": "123"},
        ) as fetch_tweet:
            code, stdout, stderr = run_cli(
                twitterapi_fetch.main,
                ["xread", "--input", "https://x.com/user/status/123"],
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn('"tweet_id": "123"', stdout)
        fetch_article.assert_called_once_with("123", "api-key", "twitterapi_io")
        fetch_tweet.assert_called_once_with("123", "api-key", "twitterapi_io")


class TwitterApiMediaTests(unittest.TestCase):
    def sample_tweet(self) -> dict:
        return {
            "extendedEntities": {
                "media": [
                    {
                        "media_key": "13_2049617901142118400",
                        "type": "video",
                        "video_info": {
                            "variants": [
                                {
                                    "content_type": "application/x-mpegURL",
                                    "url": "https://video.twimg.com/amplify_video/2049617901142118400/pl/sample.m3u8",
                                },
                                {
                                    "bitrate": 832000,
                                    "content_type": "video/mp4",
                                    "url": "https://video.twimg.com/amplify_video/2049617901142118400/vid/avc1/640x360/low.mp4?tag=21",
                                },
                                {
                                    "bitrate": 2176000,
                                    "content_type": "video/mp4",
                                    "url": "https://video.twimg.com/amplify_video/2049617901142118400/vid/avc1/1280x720/high.mp4?tag=21",
                                },
                            ]
                        },
                    }
                ]
            }
        }

    def test_selects_best_mp4_variant(self) -> None:
        videos = twitterapi_media.downloadable_videos(self.sample_tweet())

        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["bitrate"], 2176000)
        self.assertIn("1280x720", videos[0]["url"])

    def test_rejects_non_twitter_media_download_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "video.twimg.com"):
            twitterapi_media.validate_download_url("https://example.com/video.mp4")

        with self.assertRaisesRegex(ValueError, "video.twimg.com"):
            twitterapi_media.validate_download_url("http://video.twimg.com/video.mp4")

    def test_downloads_tweet_media_and_prints_file_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            twitterapi_media, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_media,
            "request_json",
            return_value={"status": "success", "tweets": [self.sample_tweet()]},
        ) as request_json, mock.patch.object(
            twitterapi_media,
            "download_file",
            return_value=12345,
        ) as download_file:
            code, stdout, stderr = run_cli(
                twitterapi_media.main,
                [
                    "xmedia",
                    "https://x.com/Yoda4ever/status/2049680135658336270?s=20",
                    "--output-dir",
                    temp_dir,
                ],
            )

        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertEqual(result["kind"], "media_download")
        self.assertEqual(result["tweet_id"], "2049680135658336270")
        self.assertEqual(result["files"][0]["bytes"], 12345)
        self.assertEqual(result["files"][0]["bitrate"], 2176000)
        self.assertTrue(result["files"][0]["path"].endswith("-media-1-2176000.mp4"))
        request_json.assert_called_once_with(
            method="GET",
            path="/twitter/tweets",
            query={"tweet_ids": "2049680135658336270"},
            api_key="api-key",
            api_provider="twitterapi_io",
        )
        download_file.assert_called_once()
        self.assertIn("1280x720", download_file.call_args.args[0])
        self.assertEqual(download_file.call_args.kwargs, {"overwrite": False})

    def test_downloads_xquik_media_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            twitterapi_media, "get_api_key", return_value="api-key"
        ) as get_api_key, mock.patch.object(
            twitterapi_media,
            "request_json",
            return_value={
                "tweets": [
                    {
                        "media": [
                            {
                                "type": "video",
                                "mediaUrl": "https://video.twimg.com/amplify_video/1/vid/avc1/1280x720/high.mp4?tag=21",
                            }
                        ]
                    }
                ]
            },
        ) as request_json, mock.patch.object(
            twitterapi_media,
            "download_file",
            return_value=321,
        ) as download_file:
            code, stdout, stderr = run_cli(
                twitterapi_media.main,
                [
                    "xmedia",
                    "2049680135658336270",
                    "--api-provider",
                    "xquik",
                    "--output-dir",
                    temp_dir,
                ],
            )

        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertEqual(result["source"], "xquik")
        self.assertEqual(result["files"][0]["bytes"], 321)
        get_api_key.assert_called_once_with(None, "xquik")
        request_json.assert_called_once_with(
            method="GET",
            path="/x/tweets",
            query={"ids": "2049680135658336270"},
            api_key="api-key",
            api_provider="xquik",
        )
        self.assertIn("1280x720", download_file.call_args.args[0])

    def test_errors_when_tweet_has_no_video_variants(self) -> None:
        with mock.patch.object(
            twitterapi_media, "get_api_key", return_value="api-key"
        ), mock.patch.object(
            twitterapi_media,
            "request_json",
            return_value={
                "status": "success",
                "tweets": [{"extendedEntities": {"media": [{"type": "photo"}]}}],
            },
        ), mock.patch.object(twitterapi_media, "download_file") as download_file:
            code, _stdout, stderr = run_cli(
                twitterapi_media.main,
                ["xmedia", "2049680135658336270"],
            )

        self.assertEqual(code, 1)
        self.assertIn("No downloadable MP4 video variants", stderr)
        download_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
