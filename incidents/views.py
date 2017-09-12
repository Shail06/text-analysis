import os
from django.http import HttpResponse
from django.shortcuts import render
from .forms import DocumentUploadForm
from .models import Document
from incidents.algo.initialization import Initialize

from django.core.files.storage import FileSystemStorage
import time


def index(request):
    home_title = "Incident Analysis"
    message_upload = "uploaded successfully!"
    context = {'home_title': home_title}
    ini_object = Initialize()

    # import pdb;
    # pdb.set_trace();
    if(request.method == 'POST'):
        if ('upload' in request.POST):
            form = DocumentUploadForm(request.POST, request.FILES)
            if(form.is_valid()):
                # newdoc		= Document(docfile=request.FILES['docfile'])
                # newdoc.save()
                upFile = request.FILES['docfile']
                name, extension = os.path.splitext(upFile.name)
                upFilename = name + time.strftime("%Y%m%d-%H%M%S") + extension
                fs = FileSystemStorage()
                filename = fs.save('uploads/' + upFilename, upFile)

                if not 'prev_files' in request.session or not request.session['prev_files']:
                    request.session["prev_files"] = []

                if len(request.session["prev_files"]) > 0:
                	try:
                		os.remove(request.session["prev_files"][0])
                	except IOError:
                		pass

                	request.session["prev_files"] = []

                if filename:
                    request.session["prev_files"].append(filename)

                # uploaded_file	= request.FILES['docfile'].name
                context['upload_success'] = upFile.name + ' ' + message_upload
                df_input = ini_object.load_input('uploads/' + upFilename)
                df_cols = list(df_input.columns)
                context['all_columns'] = df_cols
                request.session['all_columns'] = df_cols

        elif('start' in request.POST):
            incident_id = request.POST['incident_id']
            descriptions = request.POST.getlist('description')
            context['all_columns'] = request.session['all_columns']
            # Values in incident_id and decriptions should be string, and list
            # respectively
            context['inc_id'] = incident_id
            context['desc'] = descriptions

    else:
        form = DocumentUploadForm()
    return render(request, 'incidents/index.html', context)


def training(request):
    train_steps = " 1) Ask for Upload File\n\n 2) Select Relevant Columns (esp Descriptions) \n\n 3) Push Start button \n\n 4) Run Algorithm and generate Summary \n\n 5) Run Predictions algorithm to show predictions along with Accept buttons"
    context = {'training_steps': train_steps}
    return render(request, 'incidents/training.html', context)


def using(request):
    use_steps = " 1) Ask for Upload File 2) Select Relevant Columns (esp Incident ID, Descriptions) 3) Ask to Save File As.... 4) Push Start Button 5) Run Predictions algorithm 6) Show the Chart!"
    context = {'categorize_steps': use_steps}
    return render(request, 'incidents/categorize.html', context)
