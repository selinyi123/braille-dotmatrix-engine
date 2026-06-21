from __future__ import annotations

from html import escape
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

__all__ = [
    "ASCII_PRESETS",
    "resolve_ascii_charset",
    "render_ascii_text",
    "render_ascii_html",
    "render_ascii_png",
    "write_ascii_output",
]

ANSI_RESET = "\x1b[0m"
ASCII_PRESETS = {
    "standard": " .:-=+*#%@",
    "dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/*tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "blocks": " ░▒▓█",
    "binary": " .#",
}


def _normalize01(arr: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.float32)
    lo = float(np.min(a)) if a.size else 0.0
    hi = float(np.max(a)) if a.size else 1.0
    if hi - lo < 1e-6:
        return np.clip(a, 0.0, 1.0)
    return np.clip((a - lo) / (hi - lo), 0.0, 1.0)


def resolve_ascii_charset(cfg) -> tuple[str, str]:
    preset = str(getattr(cfg, "ascii_charset_preset", "custom"))
    if preset != "custom":
        if preset not in ASCII_PRESETS:
            raise ValueError(f"Unsupported ascii charset preset: {preset}")
        return ASCII_PRESETS[preset], preset
    charset = str(getattr(cfg, "ascii_charset", " .:-=+*#%@"))
    if not charset:
        raise ValueError("ascii_charset must not be empty")
    return charset, "custom"


def _prepare_image(source_bgr, cols: int, cfg) -> tuple[np.ndarray, np.ndarray]:
    src = np.asarray(source_bgr)
    if src.ndim == 2:
        bgr = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    elif src.shape[2] == 4:
        bgr = src[:, :, :3].astype(np.uint8)
    else:
        bgr = src.astype(np.uint8)

    h, w = bgr.shape[:2]
    aspect = float(getattr(cfg, "ascii_aspect_ratio", 0.50))
    rows = max(1, int(round((h / max(w, 1)) * cols * aspect)))
    resized = cv2.resize(bgr, (cols, rows), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    edge_weight = float(getattr(cfg, "ascii_edge_weight", 0.0))
    if edge_weight > 0 and min(gray.shape) >= 3:
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        edges = _normalize01(np.sqrt(gx * gx + gy * gy))
        gray = np.clip(gray + edges * edge_weight, 0.0, 1.0)

    if bool(getattr(cfg, "ascii_invert", False)):
        gray = 1.0 - gray
    return gray, resized


def _chars_from_luma(luma: np.ndarray, charset: str) -> tuple[np.ndarray, np.ndarray]:
    chars = np.array(list(charset), dtype="<U1")
    idx = np.clip(np.rint(luma * (len(chars) - 1)).astype(np.int32), 0, len(chars) - 1)
    return chars[idx], idx.astype(np.float32) / max(1, len(chars) - 1)


def _ansi_color(ch: str, bgr) -> str:
    b, g, r = [int(x) for x in bgr]
    return f"\x1b[38;2;{r};{g};{b}m{ch}{ANSI_RESET}"


def _quality_report(luma: np.ndarray, quantized: np.ndarray) -> dict:
    mse = float(np.mean((luma - quantized) ** 2)) if luma.size else 0.0
    if min(luma.shape) >= 3:
        gx = cv2.Sobel(luma.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(luma.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        edge_score = float(np.mean(np.sqrt(gx * gx + gy * gy)))
    else:
        edge_score = 0.0
    return {
        "tone_mse": mse,
        "tone_score": float(1.0 / (1.0 + mse)),
        "edge_score": edge_score,
    }


def _ascii_matrix(source_bgr, cfg) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, str]:
    cols = int(getattr(cfg, "output_width_cells", 80))
    charset, preset = resolve_ascii_charset(cfg)
    luma, colors = _prepare_image(source_bgr, cols, cfg)
    matrix, quantized = _chars_from_luma(luma, charset)
    return matrix, quantized, colors, charset, preset


def render_ascii_text(source_bgr, cfg, color: bool | None = None) -> tuple[str, dict]:
    color = bool(getattr(cfg, "ascii_ansi", False)) if color is None else bool(color)
    matrix, quantized, colors, charset, preset = _ascii_matrix(source_bgr, cfg)
    luma, _ = _prepare_image(source_bgr, int(getattr(cfg, "output_width_cells", 80)), cfg)

    lines: list[str] = []
    if color:
        for row_chars, row_colors in zip(matrix, colors):
            lines.append("".join(_ansi_color(ch, px) for ch, px in zip(row_chars.tolist(), row_colors)))
    else:
        lines = ["".join(row.tolist()) for row in matrix]

    text = "\n".join(lines) + "\n"
    report = {
        "backend": "ASCII_COLOR" if color else "ASCII_MONO",
        "rows": int(matrix.shape[0]),
        "cols": int(matrix.shape[1]),
        "charset_size": int(len(charset)),
        "charset_preset": preset,
        "aspect_ratio": float(getattr(cfg, "ascii_aspect_ratio", 0.50)),
        "edge_weight": float(getattr(cfg, "ascii_edge_weight", 0.0)),
        "ansi_color": bool(color),
        "html_available": True,
        "png_preview_available": True,
        "monospace_required": True,
        "quality": _quality_report(luma, quantized),
    }
    return text, report


def render_ascii_html(source_bgr, cfg, color: bool | None = None) -> tuple[str, dict]:
    color = bool(getattr(cfg, "ascii_ansi", False)) if color is None else bool(color)
    matrix, quantized, colors, _, _ = _ascii_matrix(source_bgr, cfg)
    luma, _ = _prepare_image(source_bgr, int(getattr(cfg, "output_width_cells", 80)), cfg)
    lines: list[str] = []
    for row_chars, row_colors in zip(matrix, colors):
        parts: list[str] = []
        for ch, px in zip(row_chars.tolist(), row_colors):
            safe = "&nbsp;" if ch == " " else escape(ch)
            if color:
                b, g, r = [int(x) for x in px]
                parts.append(f'<span style="color: rgb({r},{g},{b})">{safe}</span>')
            else:
                parts.append(safe)
        lines.append("".join(parts))
    body = "<br/>\n".join(lines)
    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<style>body{background:#111;color:#eee;}pre{font-family:monospace;line-height:1;white-space:pre;}</style>"
        "</head><body><pre>" + body + "</pre></body></html>\n"
    )
    return html, _quality_report(luma, quantized)


def render_ascii_png(source_bgr, cfg, path, color: bool | None = None) -> dict:
    color = bool(getattr(cfg, "ascii_ansi", False)) if color is None else bool(color)
    matrix, _, colors, _, _ = _ascii_matrix(source_bgr, cfg)
    font = ImageFont.load_default()
    probe = Image.new("RGB", (1, 1))
    draw_probe = ImageDraw.Draw(probe)
    bbox = draw_probe.textbbox((0, 0), "M", font=font)
    char_w = max(1, bbox[2] - bbox[0])
    char_h = max(1, bbox[3] - bbox[1] + 2)
    pad = 4
    out = Image.new("RGB", (int(matrix.shape[1] * char_w + 2 * pad), int(matrix.shape[0] * char_h + 2 * pad)), (17, 17, 17))
    draw = ImageDraw.Draw(out)
    for row_idx, (row_chars, row_colors) in enumerate(zip(matrix, colors)):
        y = pad + row_idx * char_h
        for col_idx, ch in enumerate(row_chars.tolist()):
            if ch == " ":
                continue
            x = pad + col_idx * char_w
            fill = tuple(int(v) for v in row_colors[col_idx][::-1]) if color else (238, 238, 238)
            draw.text((x, y), ch, font=font, fill=fill)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    return {"png_path": str(path), "width_px": out.size[0], "height_px": out.size[1], "font": "PIL.ImageFont.load_default"}


def write_ascii_output(source_bgr, cfg, path, color: bool | None = None, html_path=None, png_path=None) -> dict:
    text, report = render_ascii_text(source_bgr, cfg, color=color)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if html_path is not None:
        html, html_quality = render_ascii_html(source_bgr, cfg, color=color)
        html_path = Path(html_path)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        report["html_path"] = str(html_path)
        report["html_quality"] = html_quality
    if png_path is not None:
        report["png_preview"] = render_ascii_png(source_bgr, cfg, png_path, color=color)
    return report
