from unittest.mock import MagicMock
from data.models import Stroke
from renderer.stroke_diagram import draw_stroke_diagram


def test_draw_stroke_diagram_with_svg_paths():
    canvas = MagicMock()
    strokes = [
        Stroke(path=[(0.1, 0.2), (0.9, 0.2)], order=1,
               svg_d="M10,20c1,1,2,2,3,3"),
        Stroke(path=[(0.5, 0.1), (0.5, 0.9)], order=2,
               svg_d="M50,10c1,1,2,2,3,3"),
    ]
    draw_stroke_diagram(canvas, "あ", strokes, x=0, y=0, width=100, height=100)
    # Should draw SVG paths and numbered dots
    assert canvas.drawPath.called
    assert canvas.circle.called


def test_draw_stroke_diagram_fallback_without_svg():
    canvas = MagicMock()
    strokes = [
        Stroke(path=[(0.1, 0.2), (0.9, 0.2)], order=1),
        Stroke(path=[(0.5, 0.1), (0.5, 0.9)], order=2),
    ]
    draw_stroke_diagram(canvas, "あ", strokes, x=0, y=0, width=100, height=100)
    # Without svg_d, falls back to font character
    assert canvas.drawCentredString.called
    assert canvas.circle.called


def test_empty_strokes_draws_nothing():
    canvas = MagicMock()
    draw_stroke_diagram(canvas, "あ", [], x=0, y=0, width=100, height=100)
    # No strokes = nothing to draw (no SVG paths, no dots)
    assert not canvas.circle.called
