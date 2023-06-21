from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from docx import Document
import re
from transformers import BartForConditionalGeneration, BartTokenizer
from io import BytesIO

app = FastAPI()

class DocumentRequest(BaseModel):
    document: UploadFile

class DocumentResponse(BaseModel):
    data: str
    identified_paragraphs: list[str]
    summaries: list[str]

def generate_summary(paragraphs):
    # Load the BART model and tokenizer
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

    summaries = []
    for paragraph in paragraphs:
        # Encode the input text
        inputs = tokenizer.encode(paragraph, return_tensors='pt')

        # Generate the summary
        summary_ids = model.generate(inputs, num_beams=4, max_length=100, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        summaries.append(summary)

    return summaries

@app.post("/process_document")
async def process_document(request: DocumentRequest) -> DocumentResponse:
    # Read the uploaded DOCX file
    content = await request.document.read()

    # Create a temporary in-memory file from the uploaded document content
    temp_file = BytesIO(content)

    # Open the temporary file as a DOCX document
    doc = Document(temp_file)

    # Extract the text from paragraphs in the document
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)

    # Join the extracted text into a single string
    data = '\n'.join(text)

    # Split the document into paragraphs using a regex pattern
    paragraphs = re.split(r'\n\s*\n', data)

    # Remove extra whitespace and special characters from each paragraph
    paragraphs = [re.sub(r'\s+', ' ', paragraph.strip()) for paragraph in paragraphs]

    # Generate summaries
    summaries = generate_summary(paragraphs)

    return DocumentResponse(
        data=data,
        identified_paragraphs=paragraphs,
        summaries=summaries
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
