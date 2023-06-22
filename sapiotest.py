# -*- coding: utf-8 -*-
"""Sapiotest.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FCgXOit4eXnpuuXSjLH2WyhpZPU3Lc9m
"""

! pip install transformers

! pip install python-docx
! pip install torch

! pip install sentencepiece

from transformers import BartTokenizer, BartForConditionalGeneration
import torch

# Load the BART model and tokenizer
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

import docx

from docx import Document

# Open the Word document
doc = docx.Document("/content/Company1-IT-2023.docx")

# Extract the text
text = []
for paragraph in doc.paragraphs:
    text.append(paragraph.text)

# Join the extracted text
data = '\n'.join(text)

print(data)

summaries = summarize_document(data)
for i, summary in enumerate(summaries):
    print("{summary}")

