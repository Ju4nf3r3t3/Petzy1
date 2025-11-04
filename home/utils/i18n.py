"""Runtime helpers to ensure compiled translation catalogs are available."""
from __future__ import annotations

import logging
import os
import struct
import threading
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Union

try:
    from django.conf import settings
except Exception:  # pragma: no cover - allows import during docs build without Django
    settings = None  # type: ignore


LOGGER = logging.getLogger(__name__)
_LOCK = threading.Lock()
_HAS_RUN = False


class PoSyntaxError(RuntimeError):
    """Raised when a translation catalog cannot be parsed."""


def _unescape(value: str) -> str:
    """Convert a gettext literal into its unicode representation."""

    if not value:
        return ""
    if value[0] == value[-1] == '"':
        value = value[1:-1]
    return bytes(value, "utf-8").decode("unicode_escape")


def _store_message(
    catalog: Dict[str, Union[str, List[str]]],
    *,
    context: Union[str, None],
    msgid: Union[str, None],
    plural: Union[str, None],
    translations: Dict[int, str],
    fuzzy: bool,
) -> None:
    if msgid is None or fuzzy:
        return

    key = msgid
    if plural is not None:
        key = f"{msgid}\x00{plural}"
    if context is not None:
        key = f"{context}\x04{key}"

    if plural is not None:
        ordered = [translations.get(index, "") for index in sorted(translations)]
        catalog[key] = ordered
    else:
        catalog[key] = translations.get(0, "")


def _parse_po(path: Path) -> Dict[str, Union[str, List[str]]]:
    catalog: Dict[str, Union[str, List[str]]] = {}

    context: Union[str, None] = None
    msgid: Union[str, None] = None
    plural: Union[str, None] = None
    translations: Dict[int, str] = {}
    fuzzy = False
    state: Union[str, None] = None

    with path.open("r", encoding="utf-8") as handler:
        for raw_line in handler:
            line = raw_line.strip()

            if not line:
                _store_message(
                    catalog,
                    context=context,
                    msgid=msgid,
                    plural=plural,
                    translations=translations,
                    fuzzy=fuzzy,
                )
                context = None
                msgid = None
                plural = None
                translations = {}
                fuzzy = False
                state = None
                continue

            if line.startswith("#"):
                if line.startswith("#,") and "fuzzy" in line:
                    fuzzy = True
                continue

            if line.startswith("msgctxt"):
                context = _unescape(line[7:].lstrip())
                state = "msgctxt"
                continue

            if line.startswith("msgid_plural"):
                plural = _unescape(line[12:].lstrip())
                state = "msgid_plural"
                continue

            if line.startswith("msgid"):
                _store_message(
                    catalog,
                    context=context,
                    msgid=msgid,
                    plural=plural,
                    translations=translations,
                    fuzzy=fuzzy,
                )
                msgid = _unescape(line[5:].lstrip())
                plural = None
                translations = {}
                fuzzy = False
                state = "msgid"
                continue

            if line.startswith("msgstr["):
                index_end = line.find("]")
                if index_end == -1:
                    raise PoSyntaxError(f"Malformed plural definition in {path}: {line}")
                index = int(line[6:index_end])
                translations[index] = _unescape(line[index_end + 1 :].lstrip(" ="))
                state = f"msgstr[{index}]"
                continue

            if line.startswith("msgstr"):
                translations[0] = _unescape(line[6:].lstrip())
                state = "msgstr"
                continue

            if line.startswith('"') and state:
                fragment = _unescape(line)
                if state == "msgid":
                    msgid = (msgid or "") + fragment
                elif state == "msgid_plural":
                    plural = (plural or "") + fragment
                elif state.startswith("msgstr"):
                    if state == "msgstr":
                        translations[0] = translations.get(0, "") + fragment
                    else:
                        index = int(state[7:-1])
                        translations[index] = translations.get(index, "") + fragment
                elif state == "msgctxt":
                    context = (context or "") + fragment
                continue

            raise PoSyntaxError(f"Unsupported line in {path}: {raw_line.rstrip()}")

    _store_message(
        catalog,
        context=context,
        msgid=msgid,
        plural=plural,
        translations=translations,
        fuzzy=fuzzy,
    )
    return catalog


def _write_mo(path: Path, messages: Dict[str, Union[str, List[str]]]) -> None:
    keys: List[str] = sorted(messages.keys())
    if "" in messages:
        keys.remove("")
        keys.insert(0, "")

    key_lengths: List[int] = []
    value_lengths: List[int] = []
    ids = bytearray()
    strs = bytearray()

    for key in keys:
        message = messages[key]
        if isinstance(message, list):
            text = "\x00".join(message)
        else:
            text = message

        key_bytes = key.encode("utf-8")
        value_bytes = text.encode("utf-8")

        key_lengths.append(len(key_bytes))
        value_lengths.append(len(value_bytes))
        ids.extend(key_bytes + b"\0")
        strs.extend(value_bytes + b"\0")

    n = len(keys)
    keystart = 7 * 4
    valuestart = keystart + n * 8
    idstart = valuestart + n * 8
    strstart = idstart + len(ids)

    with path.open("wb") as handler:
        header = struct.pack("Iiiiiii", 0x950412de, 0, n, keystart, valuestart, 0, 0)
        handler.write(header)

        current = idstart
        for length in key_lengths:
            handler.write(struct.pack("II", length, current))
            current += length + 1

        current = strstart
        for length in value_lengths:
            handler.write(struct.pack("II", length, current))
            current += length + 1

        handler.write(ids)
        handler.write(strs)


def _should_compile(po_path: Path, mo_path: Path) -> bool:
    if not mo_path.exists():
        return True
    return po_path.stat().st_mtime > mo_path.stat().st_mtime


def _iter_locale_directories(locale_paths: Iterable[Union[str, os.PathLike]]) -> Iterable[Path]:
    for path in locale_paths:
        if not path:
            continue
        candidate = Path(path)
        if candidate.exists():
            yield candidate


def ensure_compiled_catalogs(
    *,
    force: bool = False,
    locale_dirs: Sequence[Union[str, os.PathLike]] | None = None,
    languages: Sequence[str] | None = None,
) -> None:
    """Ensure ``django.mo`` files exist for the configured languages."""

    global _HAS_RUN

    with _LOCK:
        if _HAS_RUN and not force:
            return
        _HAS_RUN = True

    if settings is None and (locale_dirs is None or languages is None):
        return

    locale_dirs = locale_dirs or getattr(settings, "LOCALE_PATHS", ())
    languages = languages or [code for code, _ in getattr(settings, "LANGUAGES", ())]

    for base_dir in _iter_locale_directories(locale_dirs):
        for language in languages:
            po_path = base_dir / language / "LC_MESSAGES" / "django.po"
            if not po_path.exists():
                continue
            mo_path = po_path.with_suffix(".mo")
            if not force and not _should_compile(po_path, mo_path):
                continue

            try:
                catalog = _parse_po(po_path)
                mo_path.parent.mkdir(parents=True, exist_ok=True)
                _write_mo(mo_path, catalog)
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.warning("Unable to compile locale %s: %s", po_path, exc)

