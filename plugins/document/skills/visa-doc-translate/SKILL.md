---
name: visa-doc-translate
description: Produce an UNCERTIFIED draft English translation of visa application document images as a bilingual PDF (original + translation). Output is a draft for a human translator to review and certify — it is not a certified translation and must not be filed as one.
---

You are helping translate visa application documents for visa applications.

## What this produces — and what it does not

This skill produces an **uncertified draft translation** for the applicant's own
use or for a qualified translator to review. It is not a certified translation
and must never claim to be one.

"Certified translation" is a term of art, and each authority sets its own bar.
Roughly:

- **US / USCIS** — a *full* translation (summaries not accepted) with the
  translator's certification that it is complete and accurate AND that they are
  competent to translate. No credential, no notarisation
  (8 CFR 103.2(b)(3)).
- **Canada / IRCC** — either a Canadian certified translator (member in good
  standing of a provincial or territorial body — certification from elsewhere
  does not waive this), or *any* person fluent in both languages who swears an
  affidavit before someone authorised to administer oaths in the country where
  the translator lives; that officer must themselves understand English or
  French. Never the applicant, a family member, or their representative.
- **UK** — the translation must carry confirmation that it is accurate, the
  date, and the translator's (or translation company official's) full name,
  **signature**, and contact details. Leave-to-remain and ILR routes
  additionally require a qualified translator plus their credentials
  (Appendix FM-SE 1(j)).
- **Australia** — translations done in Australia need a NAATI-credentialled
  translator (include their NAATI practitioner number). Translators outside
  Australia need no NAATI credential, but their full name, address, telephone
  number, and qualifications/experience must be endorsed on the translation,
  in English.

Verify the current rule for the specific route rather than trusting this list —
it changes. What does not change: every one of them attaches to a named human
who attests and is accountable. That is the part a model cannot supply. None of
these authorities addresses machine translation either way, so do not tell the
user a reviewed machine draft is definitely acceptable — say it is untested for
their route and they should confirm. What is certain is that an unreviewed draft
satisfies none of them.

If the user's stated purpose is an actual submission, say up front that a person
has to certify it before filing. Produce the draft anyway — it saves that person
time — but label it honestly.

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

5. **Verification pass** (do not skip — a transposed digit on a deposit
   certificate is far more damaging than an awkward phrasing):
   - Re-read the image a second time and check *only* the numbers, dates,
     account/ID numbers, and names against what you wrote
   - Confirm the amount's currency, magnitude and any grouping separators —
     Chinese documents may write 人民币壹拾万元整 alongside ¥100,000.00; both
     must agree
   - Confirm date order (YYYY年MM月DD日 → do not silently reorder to MM/DD)
   - List anything you could not fully verify in the Uncertain items block below

6. **PDF Generation**:
   - Create a Python script using PIL and reportlab libraries
   - Page 1: Display the rotated original image, centered and scaled to fit A4 page
   - Page 2: Display the English translation with proper formatting:
     - Title centered and bold
     - Content left-aligned with appropriate spacing
     - Professional layout suitable for official documents
   - Add this footer as plain text (it goes through reportlab, not a markdown
     renderer — do not emit literal `>` or `**`). Reproduce the wording verbatim
     and never substitute anything that asserts certification, accreditation, or
     attestation:

     ```
     UNCERTIFIED DRAFT TRANSLATION
     Machine-assisted translation of the attached original, prepared for review.
     This is not a certified translation: no translator has verified it, and it
     carries no signature, seal, credentials, or affidavit. Check the receiving
     authority's certification requirements before submitting.
     ```

   - If the verification pass left anything unresolved, add an "Uncertain items"
     list under the footer naming each field and why (illegible stamp, ambiguous
     handwriting, cropped edge). An empty list is fine; a silent omission is not.
   - Execute the script to generate the PDF

7. **Output**: Create a PDF file named `<original_filename>_Draft_Translation.pdf`
   in the same directory. The filename carries the disclaimer even when the PDF
   is forwarded without its cover note — do not shorten it to `_Translated`.

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
- Run the verification pass on numbers, dates and names — never skip it
- **Always emit the uncertified-draft footer verbatim**, plus the Uncertain items
  list if anything could not be verified. Never write any wording that asserts
  certification, accreditation, or attestation
- Name the output `_Draft_Translation.pdf`, not `_Translated.pdf`
- Use clean, professional formatting
- Complete the entire process and report the final PDF location, and say plainly
  that a human still has to certify it before filing

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
3. Re-verify every number, date, and name against the image
4. Generate `<filename>_Draft_Translation.pdf` with:
   - Page 1: Original document image
   - Page 2: English translation, the uncertified-draft footer, and any
     uncertain items

Gives the applicant and their translator an accurate starting point for
submissions to Australia, USA, Canada, the UK and elsewhere. A person still has
to review and certify it under the receiving authority's rule — see the top of
this file. This output does not meet the requirement on its own.
