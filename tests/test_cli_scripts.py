import io
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import twitterapi_call  # noqa: E402
import twitterapi_fetch  # noqa: E402


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
        fetch_tweet.assert_called_once_with("123", "api-key")

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
        fetch_article.assert_called_once_with("123", "api-key")
        fetch_tweet.assert_called_once_with("123", "api-key")


if __name__ == "__main__":
    unittest.main()
