from django.shortcuts import render
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os
import pdfplumber
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import render, redirect
import json
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import T5Tokenizer, T5ForConditionalGeneration
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError

# Load your trained model and tokenizer from the model folder
model_path = r'E:/Information_Summarizer/Information_Summarizer/info_summarizer/summarizer/model/t5_cnn_model'
tokenizer_path = r'E:/Information_Summarizer/Information_Summarizer/info_summarizer/summarizer/model/t5_cnn_tokenizer'
model = T5ForConditionalGeneration.from_pretrained(model_path)
tokenizer = T5Tokenizer.from_pretrained(tokenizer_path)

def homepage(request):
    return render(request, 'index.html')

def upload_text(request):
    return render(request, 'upload.html')

def summarize_text(request):
    if request.method == 'POST':
        input_text = request.POST['textInput']
        # Call the summarization function
        summary = summarize(input_text)
        # Render the result template with the summary
        return render(request, 'result.html', {'summary': summary})  
    return render(request, 'upload.html')

def summarize(input_text):
    inputs = tokenizer.encode("summarize: " + input_text, return_tensors="pt", max_length=512, truncation=True)
    input_length = len(inputs[0])
    if input_length > 400:
        # For longer inputs
        max_length = int(input_length * 0.5)  # Summary length is 50% of the input length
        min_length = int(input_length * 0.20)  # Minimum length is 20% of the input length
    else:
        # For shorter inputs
        max_length = min(150, int(input_length * 0.8))  
        min_length = min(50, int(input_length * 0.4))  
    summary_ids = model.generate(
        inputs,
        max_length=max_length,  
        min_length=min_length,  
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    summary = '. '.join(sentence.capitalize() for sentence in summary.split('. '))

    return summary

def upload_pdf(request):
    return render(request, 'upload_pdf.html')

def get_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Save the uploaded PDF file
        file_path = default_storage.save('pdfs/' + pdf_file.name, pdf_file)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # Extract the main content from the PDF file
        extracted_text = pdf_extractor(full_file_path)

        # Summarize the extracted text
        summary = summarize(extracted_text)

        # Store the summary in session and redirect to the result page
        request.session['pdf_summary'] = summary

        return redirect('pdf_result')  # Redirect to 'pdf-result' after processing
    
    return render(request, 'upload_pdf.html')


def pdf_result(request):
    # Get the summary from session
    summary = request.session.get('pdf_summary', "No summary available")
    
    # Render the result template with the summary
    return render(request, 'result-pdf.html', {'summary': summary})

def pdf_extractor(pdf_path):
    main_text = []

    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through each page
        for page in pdf.pages:
            # Extract raw text
            raw_text = page.extract_text()

            # Extract tables and discard them
            tables = page.extract_tables()

            # If tables are present, remove their text from raw_text
            if tables:
                for table in tables:
                    for row in table:
                        for cell in row:
                            if cell and cell in raw_text:
                                raw_text = raw_text.replace(cell, '')

            # Append the cleaned-up text to the main_text list
            main_text.append(raw_text.strip())

    # Join all pages' main text into a single string
    return '\n'.join(main_text)

# Video upload and transcript extraction
def upload_video(request):
    return render(request, 'upload_video.html')

def get_transcript(request):
    if request.method == 'POST':
        video_url_or_id = request.POST['videoId']
        
        # Define the output directory
        output_directory = 'transcripts/transcript.json'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Define the output file path
        output_file = os.path.join(output_directory, "transcript.json")

        # Call the extract_transcript function to save the transcript
        extract_transcript(video_url_or_id, output_file)

        # Check if the output file was created successfully
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                transcript_data = json.load(f)

            cleaned_transcript = transcript_data["transcript"]
            summary = summarize(cleaned_transcript)  # Summarize the cleaned transcript

            # Render the summary directly
            return render(request, 'video_result.html', {
                'summary': summary,
            })
        else:
            return render(request, 'upload_video.html', {'error': 'Transcript file not created.'})

    return render(request, 'upload_video.html')

def extract_transcript(video_url_or_id, output_file):
    # Check if input is a full URL or just a video ID
    if "youtube.com" in video_url_or_id or "youtu.be" in video_url_or_id:
        if "youtu.be" in video_url_or_id:
            video_id = video_url_or_id.split('/')[-1].split('?')[0]
    else:
        video_id = video_url_or_id.split('v=')[-1].split('&')[0]
else:
    video_id = video_url_or_id

    # Fetch transcript data
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    combined_text = " ".join([item["text"] for item in transcript])
    cleaned_text = combined_text.replace('\n', ' ').replace('\t', ' ').strip()

    transcript_json = {"transcript": cleaned_text}
    
    with open(output_file, 'w') as f:
        json.dump(transcript_json, f, indent=4)
    
    print(f"Transcript saved to {output_file} in JSON format")
except Exception as e:
    print(f"Error: {str(e)}")

def upload_url(request):
    return render(request, 'upload_url.html')

def extract_main_content(soup):
    paragraphs = soup.find_all('p')
    if paragraphs:
        return ' '.join(map(str, [p.get_text() for p in paragraphs]))
    else:
        return ' '.join(map(str, soup.stripped_strings))

def summarize_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for unwanted in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        unwanted.extract()
    
    text = extract_main_content(soup)
    text_length = len(text.split())

    max_length = int(0.5 * text_length)
    min_length = min(100,int(0.25 * text_length))

    input_ids = tokenizer.encode(text, return_tensors='pt', max_length=1024, truncation=True)
    
    summary_ids = model.generate(
        input_ids,
        max_length=max_length,
        min_length=min_length,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    summary = '. '.join(sentence.capitalize() for sentence in summary.split('. '))
    
    return summary

def summarize_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_page = response.text
            
            summary = summarize_html_content(html_page)
            return render(request, 'result-web.html', {'summary': summary})

        except requests.exceptions.RequestException as e:
            return render(request, 'upload_url.html', {'error': f"An error occurred: {e}"})

    return render(request, 'upload_url.html')