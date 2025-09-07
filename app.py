import gradio as gr
from deep_translator import GoogleTranslator
from docx import Document
from pdf2docx import Converter
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import os

# Translate text
def translate_text(text, target_lang="hi"):
    return GoogleTranslator(source='auto', target=target_lang).translate(text)

# Translate DOCX
def translate_docx(input_docx_path, output_docx_path):
    doc = Document(input_docx_path)
    for para in doc.paragraphs:
        if para.text.strip():
            para.text = translate_text(para.text)
    doc.save(output_docx_path)
    return output_docx_path

# Main function for Gradio
def translate_file(file):
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name

    # DOCX
    if tmp_path.endswith(".docx"):
        output_file = translate_docx(tmp_path, output_file)

    # PDF
    elif tmp_path.endswith(".pdf"):
        try:
            # Try direct PDF→DOCX conversion
            cv = Converter(tmp_path)
            docx_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
            cv.convert(docx_file, start=0, end=None)
            cv.close()
            output_file = translate_docx(docx_file, output_file)
        except:
            # Fallback: OCR images from PDF
            images = convert_from_path(tmp_path)
            doc = Document()
            for img in images:
                text = pytesseract.image_to_string(img)
                if text.strip():
                    doc.add_paragraph(translate_text(text))
            doc.save(output_file)

    # Images
    elif tmp_path.lower().endswith(("jpg", "jpeg", "png")):
        img = Image.open(tmp_path)
        text = pytesseract.image_to_string(img)
        doc = Document()
        doc.add_paragraph(translate_text(text))
        doc.save(output_file)

    return output_file

# Gradio interface
iface = gr.Interface(
    fn=translate_file,
    inputs=gr.File(label="Upload PDF, DOCX, or Image"),
    outputs=gr.File(label="Download Translated DOCX"),
    title="📄 English → Hindi Translator",
    description="Upload a PDF, Word, or Image file, and download the Hindi translation."
)

# Launch for Render deployment
iface.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))
