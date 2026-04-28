from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx


class TenableScConfigError(RuntimeError):
    pass


class TenableScApiError(RuntimeError):
    def __init__(self, message: str, status_code: int, response: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


@dataclass(frozen=True)
class TenableScConfig:
    base_url: str
    access_key: str
    secret_key: str
    verify_ssl: bool = True
    timeout_seconds: float = 300.0
    max_retries: int = 3
    backoff_seconds: float = 1.0

    @classmethod
    def from_env(cls) -> "TenableScConfig":
        base_url = os.getenv("TSC_URL", "").strip().rstrip("/")
        access_key = os.getenv("TSC_ACCESS_KEY", "").strip()
        secret_key = os.getenv("TSC_SECRET_KEY", "").strip()
        verify_ssl = os.getenv("TSC_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no"}
        timeout_seconds = float(os.getenv("TSC_TIMEOUT_SECONDS", "300"))
        max_retries = int(os.getenv("TSC_MAX_RETRIES", "3"))
        backoff_seconds = float(os.getenv("TSC_BACKOFF_SECONDS", "1"))

        missing = [
            name
            for name, value in (
                ("TSC_URL", base_url),
                ("TSC_ACCESS_KEY", access_key),
                ("TSC_SECRET_KEY", secret_key),
            )
            if not value
        ]
        if missing:
            raise TenableScConfigError(f"Missing required environment variables: {', '.join(missing)}")

        if not base_url.startswith(("https://", "http://")):
            raise TenableScConfigError("TSC_URL must start with https:// or http://")

        return cls(
            base_url=base_url,
            access_key=access_key,
            secret_key=secret_key,
            verify_ssl=verify_ssl,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
        )


class TenableScClient:
    def __init__(self, config: TenableScConfig | None = None) -> None:
        self.config = config or TenableScConfig.from_env()

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-apikey": f"accesskey={self.config.access_key}; secretkey={self.config.secret_key};",
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        timeout_seconds: float | None = None,
    ) -> Any:
        method = method.upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("method must be one of GET, POST, PUT, PATCH, DELETE")

        normalized_path = self._normalize_path(path)
        url = urljoin(f"{self.config.base_url}/", normalized_path.lstrip("/"))
        timeout = timeout_seconds if timeout_seconds is not None else self.config.timeout_seconds

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                with httpx.Client(verify=self.config.verify_ssl, timeout=timeout, follow_redirects=True) as client:
                    response = client.request(
                        method,
                        url,
                        headers=self.headers,
                        params=params,
                        json=json_body,
                    )
                if response.status_code == 429 and attempt < self.config.max_retries:
                    retry_after = response.headers.get("Retry-After")
                    sleep_seconds = float(retry_after) if retry_after else self.config.backoff_seconds * (attempt + 1)
                    time.sleep(sleep_seconds)
                    continue

                return self._parse_response(response)
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                if attempt < self.config.max_retries:
                    time.sleep(self.config.backoff_seconds * (attempt + 1))
                    continue
                raise

        if last_error:
            raise last_error
        raise RuntimeError("request failed without a response")

    def _parse_response(self, response: httpx.Response) -> Any:
        content_type = response.headers.get("content-type", "")
        body: Any
        if "application/json" in content_type:
            body = response.json()
        else:
            body = response.text

        if response.is_error:
            raise TenableScApiError(
                f"Tenable.sc API returned HTTP {response.status_code}",
                response.status_code,
                body,
            )

        return body

    def download(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        timeout_seconds: float | None = None,
    ) -> httpx.Response:
        method = method.upper()
        if method not in {"GET", "POST"}:
            raise ValueError("download method must be GET or POST")

        normalized_path = self._normalize_path(path)
        url = urljoin(f"{self.config.base_url}/", normalized_path.lstrip("/"))
        timeout = timeout_seconds if timeout_seconds is not None else self.config.timeout_seconds

        with httpx.Client(verify=self.config.verify_ssl, timeout=timeout, follow_redirects=True) as client:
            response = client.request(method, url, headers=self.headers, params=params, json=json_body)
        if response.is_error:
            self._parse_response(response)
        return response

    def upload_file(
        self,
        file_path: str,
        *,
        return_content: bool = False,
        context: str | None = None,
        max_file_size: int | None = None,
        timeout_seconds: float | None = None,
    ) -> Any:
        path = Path(file_path).expanduser()
        if not path.is_file():
            raise ValueError(f"file does not exist: {file_path}")

        url = urljoin(f"{self.config.base_url}/", "rest/file/upload")
        timeout = timeout_seconds if timeout_seconds is not None else self.config.timeout_seconds
        data: dict[str, str] = {"returnContent": "true" if return_content else "false"}
        if context is not None:
            data["context"] = context
        if max_file_size is not None:
            data["MAX_FILE_SIZE"] = str(max_file_size)

        headers = {"Accept": "application/json", "x-apikey": self.headers["x-apikey"]}
        with path.open("rb") as file_obj:
            files = {"Filedata": (path.name, file_obj)}
            with httpx.Client(verify=self.config.verify_ssl, timeout=timeout, follow_redirects=True) as client:
                response = client.post(url, headers=headers, data=data, files=files)
        return self._parse_response(response)

    @staticmethod
    def _normalize_path(path: str) -> str:
        path = path.strip()
        if not path:
            raise ValueError("path is required")
        if path.startswith(("http://", "https://")):
            raise ValueError("path must be relative, not an absolute URL")
        if not path.startswith("/"):
            path = f"/{path}"
        if not path.startswith("/rest/"):
            path = f"/rest{path}"
        return path
