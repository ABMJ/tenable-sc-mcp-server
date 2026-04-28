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

    @staticmethod
    def _read_env_file(env_file: str | None) -> dict[str, str]:
        if not env_file:
            return {}
        path = Path(env_file).expanduser()
        if not path.is_file():
            raise TenableScConfigError(f"Config file not found: {env_file}")

        values: dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
        return values

    @staticmethod
    def _pick(name: str, env_file_values: dict[str, str]) -> str:
        value = os.getenv(name)
        if value is not None:
            return value
        return env_file_values.get(name, "")

    @classmethod
    def from_env(cls, *, env_prefix: str = "TSC_", env_file: str | None = None) -> "TenableScConfig":
        env_file_values = cls._read_env_file(env_file)

        def prefixed(name: str) -> str:
            return f"{env_prefix}{name}"

        base_url = cls._pick(prefixed("URL"), env_file_values).strip().rstrip("/")
        access_key = cls._pick(prefixed("ACCESS_KEY"), env_file_values).strip()
        secret_key = cls._pick(prefixed("SECRET_KEY"), env_file_values).strip()
        verify_ssl_raw = cls._pick(prefixed("VERIFY_SSL"), env_file_values).strip() or "true"
        timeout_raw = cls._pick(prefixed("TIMEOUT_SECONDS"), env_file_values).strip() or "300"
        retries_raw = cls._pick(prefixed("MAX_RETRIES"), env_file_values).strip() or "3"
        backoff_raw = cls._pick(prefixed("BACKOFF_SECONDS"), env_file_values).strip() or "1"

        verify_ssl = verify_ssl_raw.lower() not in {"0", "false", "no"}
        timeout_seconds = float(timeout_raw)
        max_retries = int(retries_raw)
        backoff_seconds = float(backoff_raw)

        missing = [
            name
            for name, value in (
                (prefixed("URL"), base_url),
                (prefixed("ACCESS_KEY"), access_key),
                (prefixed("SECRET_KEY"), secret_key),
            )
            if not value
        ]
        if missing:
            prefix_hint = f" (prefix: {env_prefix})" if env_prefix != "TSC_" else ""
            file_hint = f" in {env_file}" if env_file else ""
            raise TenableScConfigError(
                f"Missing required environment variables{prefix_hint}{file_hint}: {', '.join(missing)}"
            )

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
    def __init__(
        self,
        config: TenableScConfig | None = None,
        *,
        env_prefix: str = "TSC_",
        env_file: str | None = None,
    ) -> None:
        self.config = config or TenableScConfig.from_env(env_prefix=env_prefix, env_file=env_file)

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

        response = self._request_with_retries(method, url, params=params, json_body=json_body, timeout=timeout)
        return self._parse_response(response)

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

        response = self._request_with_retries(method, url, params=params, json_body=json_body, timeout=timeout)
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
            response = self._request_with_retries(
                "POST",
                url,
                timeout=timeout,
                raw_headers=headers,
                data=data,
                files=files,
            )
        return self._parse_response(response)

    def _request_with_retries(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        timeout: float,
        raw_headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                with httpx.Client(verify=self.config.verify_ssl, timeout=timeout, follow_redirects=True) as client:
                    response = client.request(
                        method,
                        url,
                        headers=raw_headers or self.headers,
                        params=params,
                        json=json_body,
                        data=data,
                        files=files,
                    )
                if response.status_code == 429 and attempt < self.config.max_retries:
                    retry_after = response.headers.get("Retry-After")
                    sleep_seconds = float(retry_after) if retry_after else self.config.backoff_seconds * (attempt + 1)
                    time.sleep(sleep_seconds)
                    continue
                return response
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                if attempt < self.config.max_retries:
                    time.sleep(self.config.backoff_seconds * (attempt + 1))
                    continue
                raise

        if last_error:
            raise last_error
        raise RuntimeError("request failed without a response")

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
