import os
from django.http import HttpResponse
from django.shortcuts import render
from .forms import DocumentUploadForm
from .models import Document
from incidents.algo.initialization import Initialize

def index(request):
	home_title       = "Incident Analysis"
	message_upload   = "uploaded successfully!"
	context        	 = {'home_title': home_title}
	ini_object		 = Initialize()

	if(request.method == 'POST'):
		if ('upload' in request.POST):
			form = DocumentUploadForm(request.POST, request.FILES)
			if(form.is_valid()):
				newdoc		= Document(docfile=request.FILES['docfile'])
				newdoc.save()
				filename	= request.FILES['docfile'].name
				context['upload_success'] = filename + ' ' + message_upload
				df_input 	= ini_object.load_input('uploads/'+filename)
				df_cols  	= list(df_input.columns)
				context['all_columns'] = df_cols
		elif('start' in request.POST):
			pass

	else:
		form = DocumentUploadForm()
	return render(request, 'incidents/index.html', context)







def training(request):
	train_steps = " 1) Ask for Upload File\n\n 2) Select Relevant Columns (esp Descriptions) \n\n 3) Push Start button \n\n 4) Run Algorithm and generate Summary \n\n 5) Run Predictions algorithm to show predictions along with Accept buttons"
	context      = {'training_steps': train_steps}
	return render(request, 'incidents/training.html', context)


def using(request):
	use_steps = " 1) Ask for Upload File 2) Select Relevant Columns (esp Incident ID, Descriptions) 3) Ask to Save File As.... 4) Push Start Button 5) Run Predictions algorithm 6) Show the Chart!"
	context  = {'categorize_steps': use_steps}
	return render(request, 'incidents/categorize.html', context)
