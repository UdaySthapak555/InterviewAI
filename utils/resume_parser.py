from pypdf import PdfReader


# =========================
# EXTRACT TEXT FROM PDF
# =========================

def extract_text_from_pdf(
    uploaded_file
):

    reader = PdfReader(
        uploaded_file
    )

    extracted_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            extracted_text += (
                page_text
                + "\n"
            )

    return extracted_text.strip()