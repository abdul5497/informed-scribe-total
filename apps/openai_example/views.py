import uuid
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import serializers
from django.shortcuts import render
from django.urls import reverse
import openai
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
import boto3
import os
from botocore.exceptions import NoCredentialsError
import stripe

from django.http import JsonResponse, HttpResponseBadRequest

from djstripe.models import Price, Subscription
from djstripe.settings import djstripe_settings
from djstripe.utils import CURRENCY_SIGILS
from stripe.api_resources.billing_portal.session import Session as BillingPortalSession
from stripe.api_resources.checkout import Session as CheckoutSession
from stripe.error import InvalidRequestError

from apps.users.models import CustomUser
from apps.web.meta import absolute_url

from langchain.document_loaders import DirectoryLoader, PyPDFLoader, CSVLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain

from .forms import ImagePromptForm
from django.http import JsonResponse

from io import BytesIO

s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

persist_directory = 'db'
domain_url = settings.DOMAIN_URL


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
            openai_response = openai.Image.create(
                prompt=prompt, n=6, size="256x256")
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
# Upload DOCX to s3
def upload_docx_to_s3(file_contents, filename):
    print("Uploading doc")
    try:
        # Save file to the Streamlit Server
        with open(os.path.join("./docs", filename), "wb") as f:
            f.write(file_contents)

        # Upload the file to S3 bucket
        with BytesIO(file_contents) as buffer:
            s3.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME,
                              filename, ExtraArgs={'ACL': 'public-read'})

        doc_dir = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename}"

        print(doc_dir)

        # Load DOC documents from directory, generate embeddings, and persist to Chroma
        embeddings = OpenAIEmbeddings()
        doc_docs = Docx2txtLoader(os.path.join('./docs', filename)).load()
        doc_docs_list = list(doc_docs)  # Convert to list to make it iterable

        print(doc_docs)

        docDB = Chroma.from_documents(
            doc_docs_list, embeddings, persist_directory=os.path.join(persist_directory, 'medical'))
        docDB.persist()
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except NoCredentialsError:
        print("Credentials not available!")

# Upload csv to s3


def upload_csv_to_s3(file_contents, filename):
    print("Uploading csv")
    try:
        # Save file to the Streamlit Server
        with open(os.path.join("./docs", filename), "wb") as f:
            f.write(file_contents)

        # Upload the file to S3 bucket
        with BytesIO(file_contents) as buffer:
            s3.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME,
                              filename, ExtraArgs={'ACL': 'public-read'})
        csv_dir = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename}"

        print(csv_dir)

        # Load CSV documents from directory, generate embeddings, and persist to Chroma
        embeddings = OpenAIEmbeddings()
        csv_docs = CSVLoader(filename=os.path.join(
            './docs', filename), delimiter=',').load()
        csv_docs_list = list(csv_docs)  # Convert to list to make it iterable

        print(csv_docs)

        csvDB = Chroma.from_documents(
            csv_docs_list, embeddings, persist_directory=os.path.join(persist_directory, 'medical'))
        csvDB.persist()
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except NoCredentialsError:
        print("Credentials not available!")

# Upload txt to s3


def upload_txt_to_s3(file_contents, filename):
    print("Uploading txt")
    try:
        # Save file to the Streamlit Server
        with open(os.path.join("./docs", filename), "wb") as f:
            f.write(file_contents)

        # Upload the file to S3 bucket
        with BytesIO(file_contents) as buffer:
            s3.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME,
                              filename, ExtraArgs={'ACL': 'public-read'})

        txt_dir = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename}"
        print(txt_dir)

        # Load TXT documents from directory, generate embeddings, and persist to Chroma
        embeddings = OpenAIEmbeddings()
        txt_docs = TextLoader(os.path.join('./docs', filename)).load()
        txt_docs_list = list(txt_docs)  # Convert to list to make it iterable

        print(txt_docs)

        txtDB = Chroma.from_documents(
            txt_docs_list, embeddings, persist_directory=os.path.join(persist_directory, 'medical'))
        txtDB.persist()
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except NoCredentialsError:
        print("Credentials not available!")
# Upload pdf to s3


def upload_pdf_to_s3(file_contents, filename):
    print("Uploading pdf")
    try:
        # Save file to the Streamlit Server
        with open(os.path.join("./docs", filename), "wb") as f:
            f.write(file_contents)

        # Upload the file to S3 bucket
        with BytesIO(file_contents) as buffer:
            s3.upload_fileobj(buffer, settings.AWS_STORAGE_BUCKET_NAME,
                              filename, ExtraArgs={'ACL': 'public-read'})

        pdf_dir = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename}"

        print(os.path.join("./docs"))

        # Load PDF documents from directory, generate embeddings, and persist to Chroma
        embeddings = OpenAIEmbeddings()
        text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=8)

        pdf_loader = PyPDFLoader(pdf_dir)
        pdf_pages = pdf_loader.load_and_split()

        pdfDB = Chroma.from_documents(
            pdf_pages, embeddings, persist_directory=os.path.join(persist_directory, 'medical'))
        pdfDB.persist()
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except NoCredentialsError:
        print("Credentials not available!")


@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_contents = file.read()
        file_extension = os.path.splitext(file.name)[1]
        print(file_extension)

        if file_extension.lower() == '.pdf':
            upload_pdf_to_s3(file_contents, file.name)
        elif file_extension.lower() == '.csv':
            upload_csv_to_s3(file_contents, file.name)
        elif file_extension.lower() == '.txt':
            upload_txt_to_s3(file_contents, file.name)
        elif file_extension.lower() == '.docx':
            upload_docx_to_s3(file_contents, file.name)
        # Return the response as JSON with status code 200
        return JsonResponse({'status': 200, 'file_url': "file_path"})

    # Return an error response if the request method is not POST or no file was uploaded
    return JsonResponse({'status': 400, 'error': 'Invalid request'})


def get_stripe_module():
    """Gets the Stripe API module, with the API key properly populated"""
    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY
    return stripe


def create_first_mode_checkout_session(request):
    print("create_first_mode_checkout_session called")
    if request.method != 'GET':
        return HttpResponseBadRequest('Invalid request method')

    stripe = get_stripe_module()

    print(stripe)

    success_url = settings.LOGIN_REDIRECT_URL
    cancel_url = settings.LOGIN_REDIRECT_URL

    first_mode_price_id = settings.FIRST_MODE_PRICE_ID
    upfront_price_id = settings.UPFRONT_PRICE_ID

    print(upfront_price_id)

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            'accounts/login?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[
                {
                    "price": upfront_price_id,
                    "quantity": 1
                },
                {
                    "price": first_mode_price_id,
                },
            ]
        )

        print(checkout_session)

        return JsonResponse({'status': 200, 'url': checkout_session.url})

    except stripe.error.StripeError as e:
        return JsonResponse({'error': {'message': str(e)}}, status=400)

def create_second_mode_checkout_session(request):
    print("create_first_mode_checkout_session called")
    if request.method != 'GET':
        return HttpResponseBadRequest('Invalid request method')

    stripe = get_stripe_module()


    second_mode_price_id = settings.SECOND_MODE_PRICE_ID
    upfront_price_id = settings.UPFRONT_PRICE_ID

    print(upfront_price_id)

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            'accounts/login?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url,
            payment_method_types=['card'],
            mode='subscription',
            line_items=[
                {
                    "price": upfront_price_id,
                    "quantity": 1
                },
                {
                    "price": second_mode_price_id,
                },
            ]
        )

        print(checkout_session)

        return JsonResponse({'status': 200, 'url': checkout_session.url})

    except stripe.error.StripeError as e:
        return JsonResponse({'error': {'message': str(e)}}, status=400)

def check_payed_status(request):
    stripe = get_stripe_module()
    user_email = request.user.email
    customers = stripe.Customer.list(email=user_email)

    for customer in customers.data:
        customer_id = customer.id
        print(customer_id)
        subscriptions = stripe.Subscription.list(customer=customer_id, status='active')
        subscription_count = len(subscriptions.data)
        print(subscription_count)
        if subscription_count>0:
            # Payment is successful, update the database and return a success message
            return JsonResponse({'status': 200, 'message': 'Payment received'})

    # No payment found for this user
    return JsonResponse({'status': 404, 'message': 'No payment found for this user'})
   