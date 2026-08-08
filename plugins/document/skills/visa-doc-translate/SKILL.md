---
name: visa-doc-translate
description: Translate visa application documents (images) to English and create a bilingual PDF with original and translation
---

You are helping translate visa application documents for visa applications.

## Instructions

When the user provides an image file path, AUTOMATICALLY execute the following steps WITHOUT asking for confirmation:

1. **Image Conversion**: If the file is HEIC, convert it to PNG using `sips -s format png <input> --out <output>`

2. **Image Rotation**:
   - Check EXIF orientation data
   - Automatically rotate the image based on EXIF data
   - If EXIF orientation is 6, rotate 90 degrees counterclockwise
   - View the image (Read tool) to verify it is upright; apply additional rotation if the document still appears sideways or upside down

3. **Read the Document Directly** (no OCR tools needed):
   - Open the image with the Read tool — Claude reads images natively, so do NOT install or invoke any OCR library
   - Extract all text information from the document, including seals/stamps, headers, tables, and handwritten fields where legible
   - Identify document type (deposit certificate, employment certificate, retirement certificate, etc.)
   - If any text is genuinely illegible, mark it as `[illegible]` in the translation rather than guessing

4. **Translation**:
   - Translate all text content to English professionally
   - Maintain the original document structure and format
   - Use professional terminology appropriate for visa applications
   - Keep proper names in original language with English in parentheses
   - For Chinese names, use pinyin format (e.g., ZHANG San)
   - Preserve all numbers, dates, and amounts accurately

5. **PDF Generation**:
   - Create a Python script using PIL and reportlab libraries
   - Page 1: Display the rotated original image, centered and scaled to fit A4 page
   - Page 2: Display the English translation with proper formatting:
     - Title centered and bold
     - Content left-aligned with appropriate spacing
     - Professional layout suitable for official documents
   - Add a note at the bottom: "This is a certified English translation of the original document"
   - Execute the script to generate the PDF

6. **Output**: Create a PDF file named `<original_filename>_Translated.pdf` in the same directory

## Supported Documents

- Bank deposit certificates (存款证明)
- Income certificates (收入证明)
- Employment certificates (在职证明)
- Retirement certificates (退休证明)
- Property certificates (房产证明)
- Business licenses (营业执照)
- ID cards and passports
- Other official documents

## Technical Implementation

### Required Python Libraries

`pillow` and `reportlab` only. Check availability first:

```bash
python3 -c "import PIL, reportlab; print('ok')"
```

If missing, install them into a virtual environment (project directory or scratchpad). NEVER use `--break-system-packages`:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install pillow reportlab
```

Text extraction requires no libraries at all — the model reads the image directly via the Read tool.

## Important Guidelines

- DO NOT ask for user confirmation at each step
- Automatically determine the best rotation angle
- Ensure all numbers, dates, and amounts are accurately translated
- Use clean, professional formatting
- Complete the entire process and report the final PDF location

## Example Usage

```bash
/document:visa-doc-translate RetirementCertificate.PNG
/document:visa-doc-translate BankStatement.HEIC
/document:visa-doc-translate EmploymentLetter.jpg
```

## Output Example

The skill will:
1. Read the document image directly and extract its text
2. Translate to professional English
3. Generate `<filename>_Translated.pdf` with:
   - Page 1: Original document image
   - Page 2: Professional English translation

Perfect for visa applications to Australia, USA, Canada, UK, and other countries requiring translated documents.
