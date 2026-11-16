"""Rx — runtime autoral stdlib-only do RLL.

As implementações deste pacote são do projeto; os algoritmos matemáticos
subjacentes (Simpson, Gauss-Jordan, busca coordenada, etc.) são métodos
matemáticos conhecidos e não são reivindicados como invenções autorais.
"""

from .kernel import (
    bounded_coordinate_search,
    dump_json,
    invert_matrix,
    load_json,
    quad_form,
    read_csv,
    simpson,
    write_csv,
    write_svg_bars,
    write_svg_chart,
    write_svg_message,
)

__all__ = [
    "bounded_coordinate_search",
    "dump_json",
    "invert_matrix",
    "load_json",
    "quad_form",
    "read_csv",
    "simpson",
    "write_csv",
    "write_svg_bars",
    "write_svg_chart",
    "write_svg_message",
]
