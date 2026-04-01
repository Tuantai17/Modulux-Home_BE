from __future__ import annotations

import hashlib
import html
import logging
import mimetypes
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import (
    BLOG_HTTP_RETRY_ATTEMPTS,
    BLOG_HTTP_TIMEOUT_SECONDS,
    BLOG_SOURCE_BASE_URL,
    BLOG_SOURCE_DETAIL_API_TEMPLATE,
    BLOG_SOURCE_LIST_API,
    MEDIA_BASE_URL,
    MEDIA_ROOT,
)

logger = logging.getLogger(__name__)

BLOG_TYPES = {"DESIGN INSPIRATION", "FEATURED", "BUILDING", "PROJECTS"}
DEFAULT_BLOG_TYPE = "PROJECTS"


def normalize_blog_type(value: str | None) -> str:
    candidate = str(value or "").strip().upper()
    return candidate if candidate in BLOG_TYPES else DEFAULT_BLOG_TYPE


@dataclass(slots=True)
class CrawledBlogLink:
    source_url: str
    slug: str
    blog_type: str


@dataclass(slots=True)
class CrawledBlogItem:
    title: str
    blog_type: str
    slug: str
    content: str
    source_url: str
    source_hash: str
    source_created_at: datetime
    source_updated_at: datetime


class ExternalBlogCrawler:
    def __init__(self) -> None:
        self.session = self._build_session()
        self.media_dir = MEDIA_ROOT / "blogs"
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def crawl_blog_links(self) -> list[CrawledBlogLink]:
        payload = self._get_json(BLOG_SOURCE_LIST_API)
        items = payload.get("data", {}).get("listBlog", [])
        links: list[CrawledBlogLink] = []
        seen: set[str] = set()

        for item in items:
            slug = (item or {}).get("slug") or (item or {}).get("path")
            if not slug:
                continue
            source_url = self._canonical_source_url(slug)
            if source_url in seen:
                continue
            seen.add(source_url)
            links.append(
                CrawledBlogLink(
                    source_url=source_url,
                    slug=slug,
                    blog_type=normalize_blog_type((item or {}).get("type")),
                )
            )

        return links

    def crawl_blog_detail(self, url: str, *, blog_type: str | None = None) -> CrawledBlogItem:
        slug = self._extract_slug(url)
        detail_url = BLOG_SOURCE_DETAIL_API_TEMPLATE.format(slug=quote(slug))
        payload = self._get_json(detail_url).get("data", {})

        if not payload:
            raise ValueError(f"Source blog detail is empty for slug '{slug}'")

        title = payload.get("title") or slug.replace("-", " ").title()
        resolved_type = normalize_blog_type(payload.get("type") or blog_type)
        rendered_html = self._render_source_content(payload)
        rendered_html = self._prepend_cover_image(rendered_html, payload.get("src"), title)
        processed_html = self.process_images(rendered_html)
        source_hash = self.generate_hash(
            self._build_hash_payload(
                blog_type=resolved_type,
                title=title,
                slug=slug,
                cover_image_url=payload.get("src"),
                rendered_html=rendered_html,
            )
        )

        return CrawledBlogItem(
            title=title,
            blog_type=resolved_type,
            slug=self._slugify(payload.get("slug") or title),
            content=processed_html,
            source_url=self._canonical_source_url(slug),
            source_hash=source_hash,
            source_created_at=self._parse_datetime(payload.get("createdAt")),
            source_updated_at=self._parse_datetime(payload.get("updatedAt")),
        )

    def process_images(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content or "", "html.parser")
        for image in soup.find_all("img"):
            src = (image.get("src") or "").strip()
            if not src:
                continue
            if src.startswith(MEDIA_BASE_URL) or src.startswith("/media/"):
                continue
            try:
                local_src = self._download_image(src)
            except Exception:
                logger.warning("Failed to download blog image '%s'", src, exc_info=True)
                continue
            if local_src:
                image["src"] = local_src
        return str(soup)

    def generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _build_hash_payload(
        self,
        *,
        blog_type: str,
        title: str,
        slug: str,
        cover_image_url: str | None,
        rendered_html: str,
    ) -> str:
        return "\n".join(
            [
                blog_type.strip(),
                title.strip(),
                slug.strip(),
                (cover_image_url or "").strip(),
                rendered_html.strip(),
            ]
        )

    def _render_source_content(self, payload: dict[str, Any]) -> str:
        content = payload.get("content")
        if isinstance(content, str):
            return content
        if not isinstance(content, dict):
            return ""

        if isinstance(content.get("html"), str):
            return content["html"]
        if isinstance(content.get("body"), str):
            return content["body"]
        if content.get("type") == "modern":
            if isinstance(content.get("body"), str):
                return content["body"]
            if isinstance(content.get("html"), str):
                return content["html"]

        design = content.get("design")
        if isinstance(design, dict):
            body = design.get("body")
            if isinstance(body, dict):
                return self._render_unlayer_body(body)
            elements = design.get("elements")
            if isinstance(elements, list):
                return self._render_generic_elements(elements)
        if isinstance(design, list):
            return self._render_generic_elements(design)

        return ""

    def _render_unlayer_body(self, body: dict[str, Any]) -> str:
        parts = ['<article class="blog-rich-content">']
        for row in body.get("rows", []):
            parts.append('<section class="blog-row">')
            for column in row.get("columns", []):
                parts.append('<div class="blog-column">')
                for block in column.get("contents", []):
                    parts.append(self._render_block(block))
                parts.append("</div>")
            parts.append("</section>")
        parts.append("</article>")
        return "".join(parts)

    def _render_generic_elements(self, elements: list[dict[str, Any]]) -> str:
        parts = ['<article class="blog-rich-content">']
        for element in elements:
            parts.append(self._render_block(element))
        parts.append("</article>")
        return "".join(parts)

    def _render_block(self, block: dict[str, Any]) -> str:
        block_type = (block or {}).get("type")
        values = (block or {}).get("values", {})
        if not isinstance(values, dict):
            values = {}

        if block_type == "text":
            return f'<div class="blog-text">{values.get("text", "")}</div>'

        if block_type == "heading":
            tag = values.get("headingType") or "h2"
            safe_tag = tag if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} else "h2"
            return f'<{safe_tag} class="blog-heading">{values.get("text", "")}</{safe_tag}>'

        if block_type == "image":
            image_value = values.get("src")
            src = image_value.get("url", "") if isinstance(image_value, dict) else (image_value or "")
            alt = values.get("altText", "")
            if not src:
                return ""
            return (
                '<figure class="blog-image">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" />'
                "</figure>"
            )

        if block_type == "button":
            action = values.get("action", {})
            href = action.get("values", {}).get("href") or "#"
            label = values.get("text") or values.get("label") or "Read more"
            return (
                '<p class="blog-button-wrap">'
                f'<a class="blog-button" href="{html.escape(href, quote=True)}">{label}</a>'
                "</p>"
            )

        if block_type == "divider":
            return "<hr />"

        return ""

    def _prepend_cover_image(self, content_html: str, cover_image_url: str | None, title: str) -> str:
        if not cover_image_url:
            return content_html
        if cover_image_url in (content_html or ""):
            return content_html
        cover = (
            '<figure class="blog-cover" data-blog-cover="true">'
            f'<img src="{html.escape(cover_image_url, quote=True)}" alt="{html.escape(title, quote=True)}" />'
            "</figure>"
        )
        return f"{cover}{content_html}"

    def _download_image(self, url: str) -> str | None:
        hashed_name = hashlib.sha1(url.encode("utf-8")).hexdigest()
        existing = next(self.media_dir.glob(f"{hashed_name}.*"), None)
        if existing:
            return f"{MEDIA_BASE_URL}/blogs/{existing.name}"

        response = self.session.get(url, timeout=BLOG_HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()

        extension = self._guess_extension(url, response.headers.get("Content-Type", ""))
        file_path = self.media_dir / f"{hashed_name}{extension}"
        file_path.write_bytes(response.content)
        return f"{MEDIA_BASE_URL}/blogs/{file_path.name}"

    def _guess_extension(self, url: str, content_type: str) -> str:
        parsed = urlparse(url)
        suffix = Path(parsed.path).suffix.lower()
        if suffix:
            return suffix
        guessed = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
        return guessed or ".jpg"

    def _canonical_source_url(self, slug: str) -> str:
        return urljoin(f"{BLOG_SOURCE_BASE_URL}/", f"blogs/{slug}")

    def _extract_slug(self, url: str) -> str:
        parsed = urlparse(url)
        parts = [part for part in parsed.path.split("/") if part]
        if not parts:
            raise ValueError(f"Invalid blog URL: {url}")
        if len(parts) == 1 and parts[0] != "blogs":
            return parts[0]
        if len(parts) >= 2 and parts[-2] == "blogs":
            return parts[-1]
        if parts[-1] == "blogs":
            raise ValueError(f"Expected blog detail URL but got listing URL: {url}")
        return parts[-1]

    def _parse_datetime(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        clean = []
        for char in ascii_value.lower():
            clean.append(char if char.isalnum() else "-")
        slug = "".join(clean).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]

    def _get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=BLOG_HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()

    def _build_session(self) -> requests.Session:
        retry = Retry(
            total=BLOG_HTTP_RETRY_ATTEMPTS,
            read=BLOG_HTTP_RETRY_ATTEMPTS,
            connect=BLOG_HTTP_RETRY_ATTEMPTS,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": "ModuluxHomesBlogSync/1.0"})
        return session
