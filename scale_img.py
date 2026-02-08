from typing import Literal, TypedDict
from fpdf import FPDF
from fpdf.image_parsing import preload_image

class FpdfBoundingBox(TypedDict):
    x: float
    y: float
    w: float
    h: float

def scale_and_position_image(
    pdf: FPDF,
    image_path: str,
    bounding_box: FpdfBoundingBox,
    anchor: Literal["TL", "TR", "BL", "BR", "C"],
) -> None:
    if anchor == "C":
        pdf.image(
            str(image_path),
            x=bounding_box["x"],
            y=bounding_box["y"],
            w=bounding_box["w"],
            h=bounding_box["h"],
            keep_aspect_ratio=True,
        )
        return

    info = preload_image(pdf.image_cache, str(image_path))[2]
    _, _, scaled_w, scaled_h = info.scale_inside_box(**bounding_box)

    # default to top left
    x, y = bounding_box["x"], bounding_box["y"]
    if "B" in anchor:
        y = bounding_box["y"] + bounding_box["h"] - scaled_h
    if "R" in anchor:
        x = bounding_box["x"] + bounding_box["w"] - scaled_w

    pdf.image(
        str(image_path),
        x=x,
        y=y,
        w=scaled_w,
        h=scaled_h,
        keep_aspect_ratio=True,
    )
