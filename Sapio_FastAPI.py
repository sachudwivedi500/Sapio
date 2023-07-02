from fastapi import FastAPI, UploadFile
from transformers import BartTokenizer, BartForConditionalGeneration
from docx import Document
from fastapi import FastAPI, UploadFile, File
from io import BytesIO


app = FastAPI()

model_name = 'facebook/bart-large-cnn'
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

def summarize_document(document):
    paragraphs = document.split('\n')

    long_paragraphs = [p for p in paragraphs if len(p.split()) > 25]

    summaries = []

    for paragraph in long_paragraphs:
        inputs = tokenizer.encode(paragraph, return_tensors='pt')
        summary_ids = model.generate(inputs, max_length=100, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)

    return summaries

@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    document_bytes = await file.read()
    document = Document(BytesIO(document_bytes))
    text = [paragraph.text for paragraph in document.paragraphs]
    data = '\n'.join(text)
    summaries = summarize_document(data)
    return {"summaries": summaries}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


