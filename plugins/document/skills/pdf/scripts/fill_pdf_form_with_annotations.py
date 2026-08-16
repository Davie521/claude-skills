import json
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText


# Fills a PDF by adding text annotations defined in `fields.json`. See forms.md.


def transform_from_image_coords(bbox, image_width, image_height, pdf_width, pdf_height):
    """Transform bounding box from image (pixel) coordinates to PDF coordinates"""
    # Image coordinates: origin at top-left, y increases downward
    # PDF coordinates: origin at bottom-left, y increases upward
    x_scale = pdf_width / image_width
    y_scale = pdf_height / image_height

    left = bbox[0] * x_scale
    right = bbox[2] * x_scale

    # Flip Y coordinates for PDF
    top = pdf_height - (bbox[1] * y_scale)
    bottom = pdf_height - (bbox[3] * y_scale)

    return left, bottom, right, top


def transform_from_pdf_coords(bbox, pdf_height):
    """Transform bounding box from pdfplumber-style PDF points (y=0 at top) to
    pypdf's PDF coordinates (y=0 at bottom). No scaling needed, only a Y flip."""
    left = bbox[0]
    right = bbox[2]

    pypdf_top = pdf_height - bbox[1]
    pypdf_bottom = pdf_height - bbox[3]

    return left, pypdf_bottom, right, pypdf_top


def fill_pdf_form(input_pdf_path, fields_json_path, output_pdf_path):
    """Fill the PDF form with data from fields.json"""
    
    # `fields.json` format described in forms.md.
    with open(fields_json_path, "r") as f:
        fields_data = json.load(f)
    
    # Open the PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Copy all pages to writer
    writer.append(reader)
    
    # Get PDF dimensions for each page
    pdf_dimensions = {}
    for i, page in enumerate(reader.pages):
        mediabox = page.mediabox
        pdf_dimensions[i + 1] = [mediabox.width, mediabox.height]
    
    # Process each form field
    annotations = []
    for field in fields_data["form_fields"]:
        page_num = field["page_number"]
        
        # Get page dimensions and transform coordinates. The coordinate system is
        # auto-detected: `pdf_width`/`pdf_height` in the page entry means the bounding
        # boxes are already in PDF points (from extract_form_structure.py), while
        # `image_width`/`image_height` means they are pixels from a rendered page image.
        page_info = next(p for p in fields_data["pages"] if p["page_number"] == page_num)
        pdf_width, pdf_height = pdf_dimensions[page_num]

        if "pdf_width" in page_info:
            transformed_entry_box = transform_from_pdf_coords(
                field["entry_bounding_box"],
                float(pdf_height)
            )
        else:
            image_width = page_info["image_width"]
            image_height = page_info["image_height"]
            transformed_entry_box = transform_from_image_coords(
                field["entry_bounding_box"],
                image_width, image_height,
                float(pdf_width), float(pdf_height)
            )

        # Skip empty fields
        if "entry_text" not in field or "text" not in field["entry_text"]:
            continue
        entry_text = field["entry_text"]
        text = entry_text["text"]
        if not text:
            continue
        
        font_name = entry_text.get("font", "Arial")
        font_size = str(entry_text.get("font_size", 14)) + "pt"
        font_color = entry_text.get("font_color", "000000")

        # Font size/color seems to not work reliably across viewers:
        # https://github.com/py-pdf/pypdf/issues/2084
        annotation = FreeText(
            text=text,
            rect=transformed_entry_box,
            font=font_name,
            font_size=font_size,
            font_color=font_color,
            border_color=None,
            background_color=None,
        )
        annotations.append(annotation)
        # page_number is 0-based for pypdf
        writer.add_annotation(page_number=page_num - 1, annotation=annotation)
        
    # Save the filled PDF
    with open(output_pdf_path, "wb") as output:
        writer.write(output)
    
    print(f"Successfully filled PDF form and saved to {output_pdf_path}")
    print(f"Added {len(annotations)} text annotations")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: fill_pdf_form_with_annotations.py [input pdf] [fields.json] [output pdf]")
        sys.exit(1)
    input_pdf = sys.argv[1]
    fields_json = sys.argv[2]
    output_pdf = sys.argv[3]
    
    fill_pdf_form(input_pdf, fields_json, output_pdf)