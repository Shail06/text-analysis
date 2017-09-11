from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm

def index(request):
	message_home   = "Incident Analysis"
	context        = {'home_title': message_home}
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			handle_uploaded_file(request.FILES['file'])
			return HttpResponseRedirect('/training/')
	else:
		form = UploadFileForm()
	return render(request, 'incidents/index.html', context)


def training(request):
	train_steps = " 1) Ask for Upload File\n\n 2) Select Relevant Columns (esp Descriptions) \n\n 3) Push Start button \n\n 4) Run Algorithm and generate Summary \n\n 5) Run Predictions algorithm to show predictions along with Accept buttons"
	context      = {'training_steps': train_steps}
	return render(request, 'incidents/training.html', context)


def using(request):
	use_steps = " 1) Ask for Upload File 2) Select Relevant Columns (esp Incident ID, Descriptions) 3) Ask to Save File As.... 4) Push Start Button 5) Run Predictions algorithm 6) Show the Chart!"
	context  = {'categorize_steps': use_steps}
	return render(request, 'incidents/categorize.html', context)
