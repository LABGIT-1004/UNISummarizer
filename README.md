# Information Summarizer

A Django web application for summarizing information from text, PDF files, YouTube videos, and web URLs using a T5 transformer model.

## Features
- Summarize plain text
- Summarize PDF documents
- Summarize YouTube video transcripts
- Summarize content from web URLs
- User authentication (login/register)

## Requirements
- Python 3.13+
- Django
- transformers
- torch
- pdfplumber
- youtube_transcript_api
- requests
- beautifulsoup4
- sentencepiece

## Setup Instructions

1. **Clone the repository**
   ```powershell
   git clone <your-repo-url>
   cd Information_Summarizer/Information_Summarizer
   ```

2. **Create and activate a virtual environment**
   ```powershell
   python -m venv info_summarizer/.venv
   info_summarizer/.venv/Scripts/activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```powershell
   info_summarizer/.venv/Scripts/python.exe manage.py migrate
   ```

5. **Start the development server**
   ```powershell
   info_summarizer/.venv/Scripts/python.exe manage.py runserver
   ```

6. **Access the app**
   Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Project Structure
```
Information_Summarizer/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── info_summarizer/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── wsgi.py
│   └── ...
├── summarizer/
│   ├── model/
│   │   └── t5_cnn_model/
│   │   └── t5_cnn_tokenizer/
│   ├── templates/
│   └── ...
├── pdfs/
├── transcripts/
└── ...
```

## Model Files
- Place your T5 model and tokenizer files in `summarizer/model/t5_cnn_model` and `summarizer/model/t5_cnn_tokenizer` respectively.

## License
MIT
