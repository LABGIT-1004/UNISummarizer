from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='homepage'),  # Homepage route
    path('upload/', upload_text, name='upload'),  # Upload text route
    path('summarize/', summarize_text, name='summarize'),  # Summarize text route
    path('upload-pdf/', upload_pdf, name='upload_pdf'),  # PDF upload page route
    path('pdf-summary/', get_pdf, name='pdf_summary'),  # PDF summarization route
    path('pdf-result/', pdf_result, name='pdf_result'),  # PDF result page
    path('upload-video/', upload_video, name='upload_video'),  # Upload video page
    path('get-transcript/', get_transcript, name='get_transcript'),  # Corrected to use the view name
    path('upload-url/', upload_url, name='upload_url'),  # URL input route
    path('summarize-url/', summarize_url, name='summarize_url'),  # URL summarization route
]
