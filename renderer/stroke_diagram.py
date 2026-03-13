"""Renders stroke order diagrams on flash card backs using KanjiVG paths."""
import re
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import Color
from data.models import Stroke
import config


# KanjiVG viewBox size
_VB = 109.0


def _tokenize_svg_path(d: str) -> list:
    """Tokenize an SVG path 'd' attribute into commands and numbers."""
    return re.findall(
        r"[MmCcSsQqTtLlHhVvAaZz]|[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", d
    )


def _draw_svg_path(c: Canvas, d: str, x: float, y: float,
                   width: float, height: float):
    """Parse an SVG path 'd' attribute and draw it on the reportlab canvas.

    Converts from KanjiVG 109x109 coordinates to the target rectangle.
    SVG Y goes down, PDF Y goes up — we flip vertically.
    """
    if not d:
        return

    tokens = _tokenize_svg_path(d)

    def to_pdf_x(vx: float) -> float:
        return x + (vx / _VB) * width

    def to_pdf_y(vy: float) -> float:
        return y + height - (vy / _VB) * height  # flip Y

    def to_pdf_dx(dvx: float) -> float:
        return (dvx / _VB) * width

    def to_pdf_dy(dvy: float) -> float:
        return -(dvy / _VB) * height  # flip Y for relative

    path = c.beginPath()
    cur_x, cur_y = 0.0, 0.0  # current point in SVG coords
    last_ctrl_x, last_ctrl_y = 0.0, 0.0  # last control point for S/s

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if not re.match(r"[A-Za-z]", token):
            i += 1
            continue

        cmd = token
        i += 1

        def nums(count):
            nonlocal i
            result = []
            for _ in range(count):
                if i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                    result.append(float(tokens[i]))
                    i += 1
                else:
                    result.append(0.0)
            return result

        if cmd == "M":
            coords = nums(2)
            cur_x, cur_y = coords[0], coords[1]
            path.moveTo(to_pdf_x(cur_x), to_pdf_y(cur_y))
            # Implicit lineto for subsequent coordinate pairs
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(2)
                cur_x, cur_y = coords[0], coords[1]
                path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "m":
            coords = nums(2)
            cur_x += coords[0]
            cur_y += coords[1]
            path.moveTo(to_pdf_x(cur_x), to_pdf_y(cur_y))
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(2)
                cur_x += coords[0]
                cur_y += coords[1]
                path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "C":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(6)
                path.curveTo(
                    to_pdf_x(coords[0]), to_pdf_y(coords[1]),
                    to_pdf_x(coords[2]), to_pdf_y(coords[3]),
                    to_pdf_x(coords[4]), to_pdf_y(coords[5]),
                )
                last_ctrl_x, last_ctrl_y = coords[2], coords[3]
                cur_x, cur_y = coords[4], coords[5]

        elif cmd == "c":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(6)
                x1 = cur_x + coords[0]
                y1 = cur_y + coords[1]
                x2 = cur_x + coords[2]
                y2 = cur_y + coords[3]
                ex = cur_x + coords[4]
                ey = cur_y + coords[5]
                path.curveTo(
                    to_pdf_x(x1), to_pdf_y(y1),
                    to_pdf_x(x2), to_pdf_y(y2),
                    to_pdf_x(ex), to_pdf_y(ey),
                )
                last_ctrl_x, last_ctrl_y = x2, y2
                cur_x, cur_y = ex, ey

        elif cmd == "S":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(4)
                # Reflect last control point
                rx = 2 * cur_x - last_ctrl_x
                ry = 2 * cur_y - last_ctrl_y
                path.curveTo(
                    to_pdf_x(rx), to_pdf_y(ry),
                    to_pdf_x(coords[0]), to_pdf_y(coords[1]),
                    to_pdf_x(coords[2]), to_pdf_y(coords[3]),
                )
                last_ctrl_x, last_ctrl_y = coords[0], coords[1]
                cur_x, cur_y = coords[2], coords[3]

        elif cmd == "s":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(4)
                rx = 2 * cur_x - last_ctrl_x
                ry = 2 * cur_y - last_ctrl_y
                x2 = cur_x + coords[0]
                y2 = cur_y + coords[1]
                ex = cur_x + coords[2]
                ey = cur_y + coords[3]
                path.curveTo(
                    to_pdf_x(rx), to_pdf_y(ry),
                    to_pdf_x(x2), to_pdf_y(y2),
                    to_pdf_x(ex), to_pdf_y(ey),
                )
                last_ctrl_x, last_ctrl_y = x2, y2
                cur_x, cur_y = ex, ey

        elif cmd == "L":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(2)
                cur_x, cur_y = coords[0], coords[1]
                path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "l":
            while i < len(tokens) and not re.match(r"[A-Za-z]", tokens[i]):
                coords = nums(2)
                cur_x += coords[0]
                cur_y += coords[1]
                path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "H":
            coords = nums(1)
            cur_x = coords[0]
            path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "h":
            coords = nums(1)
            cur_x += coords[0]
            path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "V":
            coords = nums(1)
            cur_y = coords[0]
            path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd == "v":
            coords = nums(1)
            cur_y += coords[0]
            path.lineTo(to_pdf_x(cur_x), to_pdf_y(cur_y))

        elif cmd in ("Z", "z"):
            path.close()

        else:
            # Skip unknown commands
            pass

    c.drawPath(path, fill=0, stroke=1)


def _draw_synthetic_mark(c: Canvas, stroke: Stroke,
                         x: float, y: float, width: float, height: float):
    """Draw a synthetic dakuten/handakuten mark from path points."""
    def to_pdf(nx: float, ny: float) -> tuple[float, float]:
        return x + nx * width, y + height - ny * height

    if len(stroke.path) > 4:
        # Handakuten: circle from many points
        pts = [to_pdf(*p) for p in stroke.path]
        path = c.beginPath()
        path.moveTo(*pts[0])
        for pt in pts[1:]:
            path.lineTo(*pt)
        path.close()
        c.drawPath(path, fill=0, stroke=1)
    else:
        # Dakuten: short diagonal line
        p0 = to_pdf(*stroke.path[0])
        p1 = to_pdf(*stroke.path[1])
        c.line(p0[0], p0[1], p1[0], p1[1])


def draw_stroke_diagram(c: Canvas, character: str, strokes: list[Stroke],
                        x: float, y: float, width: float, height: float):
    """Draw KanjiVG stroke paths with numbered start indicators.

    Each stroke is drawn as a gray path from KanjiVG data, with a red
    circled number at the start point showing stroke order.
    """
    c.saveState()

    if strokes:
        has_svg = any(s.svg_d for s in strokes)

        if has_svg:
            # Draw each stroke as actual KanjiVG path or synthetic mark
            for stroke in strokes:
                c.setStrokeColorRGB(0.75, 0.75, 0.75)
                c.setLineWidth(config.STROKE_LINE_WIDTH * 1.5)
                c.setLineCap(1)  # round caps
                c.setLineJoin(1)  # round joins
                if stroke.svg_d:
                    _draw_svg_path(c, stroke.svg_d, x, y, width, height)
                elif len(stroke.path) >= 2:
                    # Synthetic stroke (dakuten/handakuten): draw as gray line
                    _draw_synthetic_mark(c, stroke, x, y, width, height)
        else:
            # Fallback: draw the font character in light gray
            font_size = min(width, height) * 0.85
            c.setFillColorRGB(0.82, 0.82, 0.82)
            c.setFont("KleeOne", font_size)
            cx = x + width / 2
            cy = y + height / 2 - font_size / 3
            c.drawCentredString(cx, cy, character)

        # Overlay numbered start indicators
        def to_pdf(nx: float, ny: float) -> tuple[float, float]:
            return x + nx * width, y + height - ny * height

        for stroke in strokes:
            if not stroke.path:
                continue

            sx, sy = to_pdf(*stroke.path[0])

            # Circled number at start
            c.setFillColorRGB(*config.STROKE_NUMBER_COLOR)
            c.circle(sx, sy, config.STROKE_DOT_RADIUS, fill=1, stroke=0)

            # White number
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", config.STROKE_NUMBER_FONT_SIZE)
            num_str = str(stroke.order)
            text_width = c.stringWidth(num_str, "Helvetica-Bold", config.STROKE_NUMBER_FONT_SIZE)
            c.drawString(
                sx - text_width / 2,
                sy - config.STROKE_NUMBER_FONT_SIZE / 3,
                num_str,
            )

    c.restoreState()
