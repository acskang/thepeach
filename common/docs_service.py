import html
import logging
from collections import defaultdict
from pathlib import Path

import markdown
from django.conf import settings
from django.http import Http404

from .docs_registry import DOCUMENT_REGISTRY, DocumentEntry

docs_logger = logging.getLogger("common.docs")

DOCS_ROOT = settings.BASE_DIR / "docs"
MARKDOWN_EXTENSIONS = [
    "fenced_code",
    "tables",
    "toc",
    "sane_lists",
]

CATEGORY_TITLES = {
    "platform-foundations": "Platform Foundations",
    "authentication-identity": "Authentication And Identity",
    "api-integration": "API And Integration",
    "media-assets": "Media And Assets",
    "operations-deployment": "Operations And Deployment",
    "repository-workflow": "Repository Workflow",
    "service-guides": "Service Guides",
    "references": "References",
}


def _registry_map():
    return {entry.slug: entry for entry in DOCUMENT_REGISTRY}


def get_all_documents():
    documents = []
    registry = _registry_map()
    for slug, entry in registry.items():
        document = build_document_metadata(entry)
        documents.append(document)
    return sorted(documents, key=lambda item: item["sort_order"])


def build_document_metadata(entry: DocumentEntry):
    file_path = DOCS_ROOT / entry.file_path
    if not file_path.exists():
        docs_logger.warning("document source missing slug=%s file=%s", entry.slug, entry.file_path)
        raise Http404(f"Document source is missing for slug '{entry.slug}'.")

    return {
        "slug": entry.slug,
        "title": entry.title,
        "summary": entry.summary,
        "category": entry.category,
        "category_title": CATEGORY_TITLES.get(entry.category, entry.category),
        "audience": list(entry.audience),
        "sort_order": entry.sort_order,
        "is_featured": entry.is_featured,
        "is_core": entry.is_core,
        "show_in_index": entry.show_in_index,
        "related_slugs": list(entry.related_slugs),
        "status_label": entry.status_label,
        "reading_order": entry.reading_order,
        "icon_key": entry.icon_key,
        "file_path": f"docs/{entry.file_path}",
        "available_url": f"/docs/{entry.slug}/",
    }


def get_document_by_slug(slug: str):
    entry = _registry_map().get(slug)
    if entry is None:
        docs_logger.info("unknown docs slug requested slug=%s", slug)
        raise Http404("Document was not found.")
    return build_document_metadata(entry)


def load_document_content(slug: str):
    metadata = get_document_by_slug(slug)
    source_path = DOCS_ROOT / Path(metadata["file_path"]).name
    if not source_path.exists():
        docs_logger.warning("document source missing at render slug=%s path=%s", slug, source_path)
        raise Http404("Document source file was not found.")

    raw_markdown = source_path.read_text(encoding="utf-8")
    # Escape raw HTML before markdown conversion so markdown stays functional
    # while document rendering does not trust embedded HTML.
    safe_source = html.escape(raw_markdown)
    html_content = markdown.markdown(safe_source, extensions=MARKDOWN_EXTENSIONS)
    metadata["html_content"] = html_content
    metadata["source_markdown"] = raw_markdown
    metadata["source_path"] = str(source_path.relative_to(settings.BASE_DIR))
    return metadata


def get_related_documents(slug: str):
    document = get_document_by_slug(slug)
    related = []
    for related_slug in document["related_slugs"]:
        try:
            related.append(get_document_by_slug(related_slug))
        except Http404:
            continue
    return related


def get_previous_next_documents(slug: str):
    reading_documents = [doc for doc in get_all_documents() if doc["reading_order"] is not None]
    reading_documents.sort(key=lambda item: item["reading_order"])
    for index, document in enumerate(reading_documents):
        if document["slug"] != slug:
            continue
        previous_doc = reading_documents[index - 1] if index > 0 else None
        next_doc = reading_documents[index + 1] if index + 1 < len(reading_documents) else None
        return previous_doc, next_doc
    return None, None


def build_docs_hub_context():
    documents = [doc for doc in get_all_documents() if doc["show_in_index"]]
    featured = [doc for doc in documents if doc["is_featured"]]
    reading_order = [doc for doc in documents if doc["reading_order"] is not None]
    reading_order.sort(key=lambda item: item["reading_order"])

    categories = defaultdict(list)
    for document in documents:
        categories[document["category_title"]].append(document)

    platform_concepts = [
        {
            "name": "accounts",
            "summary": "Centralized authentication, custom user model, JWT issuance, and future SSO expansion surface.",
        },
        {
            "name": "common",
            "summary": "Shared response contracts, base models, exception handling, pagination, and cross-cutting platform utilities.",
        },
        {
            "name": "gateway",
            "summary": "Unified API entry, integration boundary, deterministic routing contracts, and machine-friendly discovery surfaces.",
        },
        {
            "name": "media",
            "summary": "Shared media server for reusable image storage, metadata management, and Nginx-served media delivery.",
        },
        {
            "name": "services",
            "summary": "Application registry and service metadata that support governance, trusted integration, and future platform services.",
        },
        {
            "name": "project/settings",
            "summary": "Base, local, and production settings split with explicit runtime selection and production hardening.",
        },
        {
            "name": "templates / static / media_files / logs / docs",
            "summary": "Operator UI, platform styling, uploaded media storage, log outputs, and long-term operational documentation.",
        },
    ]

    production_summary = [
        "Cloudflare fronts the public edge.",
        "Nginx serves static and media assets directly.",
        "Gunicorn runs Django behind the reverse proxy.",
        "Django handles application logic, APIs, upload validation, and platform pages.",
        "Operational logging must remain file-compatible and production-safe.",
    ]

    useful_navigation = [
        {"label": "Home", "url": "/"},
        {"label": "Applications", "url": "/applications/"},
        {"label": "Assets", "url": "/assets/"},
        {"label": "Auth", "url": "/auth/login/"},
        {"label": "API Root", "url": "/api/v1/"},
        {"label": "Docs System", "url": "/docs/platform-documentation-system/"},
    ]

    docs_logger.info("docs index render count=%s", len(documents))
    return {
        "documents": documents,
        "featured_documents": featured,
        "reading_order_documents": reading_order,
        "category_sections": dict(categories),
        "platform_concepts": platform_concepts,
        "production_summary": production_summary,
        "useful_navigation": useful_navigation,
    }


def build_document_detail_context(slug: str):
    document = load_document_content(slug)
    related_documents = get_related_documents(slug)
    previous_document, next_document = get_previous_next_documents(slug)
    docs_logger.info("docs detail render slug=%s", slug)
    return {
        "document": document,
        "related_documents": related_documents,
        "previous_document": previous_document,
        "next_document": next_document,
    }
