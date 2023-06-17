from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import serializers
from django.shortcuts import render
import openai
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
import boto3
import os
from botocore.exceptions import NoCredentialsError

from .forms import ImagePromptForm


@login_required
def home(request):
    return TemplateResponse(
        request,
        "openai_example/openai_home.html",
        {
            "active_tab": "openai",
        },
    )




@login_required
def image_demo(request):
    openai.api_key = settings.OPENAI_API_KEY
    image_urls = []
    if request.method == "POST":
        form = ImagePromptForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data["prompt"]
            openai_response = openai.Image.create(prompt=prompt, n=6, size="256x256")
            # import pdb; pdb.set_trace()
            print(openai_response)
            image_urls = [data["url"] for data in openai_response.data]
    else:
        form = ImagePromptForm()
    return TemplateResponse(
        request,
        "openai_example/image_home.html",
        {
            "active_tab": "openai",
            "form": form,
            "image_urls": image_urls,
        },
    )

@login_required
def upload_file(request):
    print("upload_file called")
    return Response(serializers())
    # if request.method == 'POST' and request.FILES['file']:
    #     file = request.FILES['file']
    #     bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name

    #     # Save the file in the local "public" folder
    #     file_path = os.path.join('public', file.name)
    #     with open(file_path, 'wb+') as destination:
    #         for chunk in file.chunks():
    #             destination.write(chunk)

