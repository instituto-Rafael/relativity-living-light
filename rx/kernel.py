"""Rx stdlib-only numerical/IO kernel.

Zero third-party imports. The code is intentionally small and auditable.
"""

from __future__ import annotations

import csv
import html
import json
import math
import random
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_csv(path):
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fieldnames=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def simpson(fn, a, b, n=256):
    if b <= a:
        return 0.0
    n = max(2, int(n))
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * fn(a + i * h)
    return total * h / 3.0


def invert_matrix(matrix, eps=1.0e-30):
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be non-empty and square")
    aug = [
        [float(x) for x in matrix[i]]
        + [1.0 if i == j else 0.0 for j in range(n)]
        for i in range(n)
    ]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) <= eps:
            raise ValueError("singular matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [
                    aug[row][j] - factor * aug[col][j]
                    for j in range(2 * n)
                ]
    return [row[n:] for row in aug]


def quad_form(vector, matrix):
    n = len(vector)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("quadratic-form shape mismatch")
    return sum(
        float(vector[i]) * float(matrix[i][j]) * float(vector[j])
        for i in range(n)
        for j in range(n)
    )


def bounded_coordinate_search(objective, start, bounds, maxiter=20, seed=1, random_probes=2):
    if len(start) != len(bounds):
        raise ValueError("start/bounds mismatch")
    rng = random.Random(int(seed))
    x = [
        max(float(lo), min(float(hi), float(value)))
        for value, (lo, hi) in zip(start, bounds)
    ]
    fx = float(objective(x))
    step = [(float(hi) - float(lo)) * 0.12 for lo, hi in bounds]
    evaluations = 1

    for outer in range(max(1, int(maxiter))):
        candidates = []
        for i in range(len(x)):
            for direction in (-1.0, 1.0):
                y = x[:]
                lo, hi = bounds[i]
                y[i] = max(float(lo), min(float(hi), y[i] + direction * step[i]))
                candidates.append(y)
        for _ in range(max(0, int(random_probes))):
            radius = max(0.05, 0.60 ** (outer + 1))
            y = []
            for value, (lo, hi) in zip(x, bounds):
                span = float(hi) - float(lo)
                trial = value + (rng.random() * 2.0 - 1.0) * span * radius
                y.append(max(float(lo), min(float(hi), trial)))
            candidates.append(y)

        improved = False
        for y in candidates:
            fy = float(objective(y))
            evaluations += 1
            if math.isfinite(fy) and fy < fx:
                x, fx = y, fy
                improved = True
        decay = 0.72 if improved else 0.50
        step = [
            max((float(hi) - float(lo)) * 1.0e-6, s * decay)
            for s, (lo, hi) in zip(step, bounds)
        ]

    return {
        "x": x,
        "fun": fx,
        "iterations": max(1, int(maxiter)),
        "evaluations": evaluations,
        "method": "rx_bounded_coordinate_search_v1",
    }


def write_svg_chart(path, title, series, width=900, height=520):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    all_points = []
    for item in series:
        all_points.extend(item.get("points", []))
    if not all_points:
        all_points = [(0.0, 0.0), (1.0, 1.0)]

    xs = [float(p[0]) for p in all_points]
    ys = [float(p[1]) for p in all_points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax = xmin + 1.0
    if ymax == ymin:
        ymax = ymin + 1.0

    left, right, top, bottom = 70.0, 25.0, 55.0, 55.0
    pw = width - left - right
    ph = height - top - bottom

    def sx(x):
        return left + (float(x) - xmin) * pw / (xmax - xmin)

    def sy(y):
        return top + ph - (float(y) - ymin) * ph / (ymax - ymin)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="30" font-size="20" font-family="sans-serif">{html.escape(str(title))}</text>',
        f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" stroke="black"/>',
    ]
    dash = ["", ' stroke-dasharray="7,5"', ' stroke-dasharray="2,5"']
    for idx, item in enumerate(series):
        points = item.get("points", [])
        if not points:
            continue
        coords = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in points)
        out.append(
            f'<polyline points="{coords}" fill="none" stroke="black" stroke-width="{1.5 + (idx % 2)}"{dash[idx % len(dash)]}/>'
        )
        label = html.escape(str(item.get("label", f"series-{idx+1}")))
        out.append(f'<text x="{left+10}" y="{top+18+idx*18}" font-size="12" font-family="monospace">{label}</text>')
    out.append(
        f'<text x="{left}" y="{height-12}" font-size="11" font-family="monospace">'
        f'x=[{xmin:.4g},{xmax:.4g}] y=[{ymin:.4g},{ymax:.4g}]</text>'
    )
    out.append("</svg>")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_svg_bars(path, title, labels, values, width=900, height=520):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = [str(x) for x in labels]
    values = [float(x) for x in values]
    if len(labels) != len(values):
        raise ValueError("labels/values length mismatch")
    if not labels:
        labels = ["empty"]
        values = [0.0]

    left, right, top, bottom = 70.0, 25.0, 55.0, 85.0
    pw = width - left - right
    ph = height - top - bottom
    vmax = max(max(values), 0.0)
    vmin = min(min(values), 0.0)
    if vmax == vmin:
        vmax = vmin + 1.0

    def sy(value):
        return top + (vmax - float(value)) * ph / (vmax - vmin)

    zero_y = sy(0.0)
    slot = pw / max(len(labels), 1)
    bar_w = slot * 0.62
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="30" font-size="20" font-family="sans-serif">{html.escape(str(title))}</text>',
        f'<line x1="{left}" y1="{zero_y:.2f}" x2="{left+pw}" y2="{zero_y:.2f}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" stroke="black"/>',
    ]
    for idx, (label, value) in enumerate(zip(labels, values)):
        x = left + idx * slot + (slot - bar_w) / 2.0
        y = sy(max(value, 0.0))
        y2 = sy(min(value, 0.0))
        h = max(abs(y2 - y), 1.0)
        out.append(
            f'<rect x="{x:.2f}" y="{min(y,y2):.2f}" width="{bar_w:.2f}" height="{h:.2f}" '
            'fill="none" stroke="black"/>'
        )
        out.append(
            f'<text x="{x + bar_w/2:.2f}" y="{top+ph+20}" text-anchor="middle" '
            f'font-size="11" font-family="monospace">{html.escape(label)}</text>'
        )
        out.append(
            f'<text x="{x + bar_w/2:.2f}" y="{min(y,y2)-4:.2f}" text-anchor="middle" '
            f'font-size="10" font-family="monospace">{value:.6g}</text>'
        )
    out.append("</svg>")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_svg_message(path, title, message, width=900, height=320):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="50" font-size="20" font-family="sans-serif">{html.escape(str(title))}</text>',
        f'<text x="40" y="110" font-size="15" font-family="monospace">{html.escape(str(message))}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
