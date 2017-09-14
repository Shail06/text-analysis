import os
from django.http import HttpResponse
from django.shortcuts import render
from .forms import DocumentUploadForm
from incidents.algo.execution import ExecuteScenario

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.core.files.storage import FileSystemStorage
import time
import json


def index(request):
    home_title = "Incident Analysis"
    message_upload = "uploaded successfully!"
    context = {'home_title': home_title}
    exec_scenario = ExecuteScenario()  # Object reinitilize

    # import pdb;
    # pdb.set_trace();

    if(request.method == 'POST'):
        if ('upload' in request.POST):
            form = DocumentUploadForm(request.POST, request.FILES)
            if(form.is_valid()):
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

                context['upload_success'] = upFile.name + ' ' + message_upload
                df_cols = exec_scenario.get_column_headers(filename)
                context['all_columns'] = df_cols
                request.session['all_columns'] = df_cols

        elif('start' in request.POST):
            incid_col = request.POST['incident_id']
            desc_col = request.POST.getlist('description')
            request.session['desc_cols'] = desc_col
            context['desc_cols'] = desc_col
            context['all_columns'] = request.session['all_columns']
            df_cols = exec_scenario.get_column_headers(
                request.session["prev_files"][0])
            df_output = exec_scenario.get_predicted_dataframe(desc_col)

            paginator = Paginator(df_output.values.tolist(), 1)
            page = request.GET.get('page')
            try:
                output_detail = paginator.page(page)
            except PageNotAnInteger:
                output_detail = paginator.page(1)
            except EmptyPage:
                output_detail = paginator.page(paginator.num_pages)
            context['output_detail'] = output_detail
            context['predictions'] = json.loads(output_detail[0][5])

    elif('page' in request.GET):
        context['all_columns'] = request.session['all_columns']
        desc_col = request.session['desc_cols']
        context['desc_cols'] = desc_col
        df_cols = exec_scenario.get_column_headers(
            request.session["prev_files"][0])
        df_output = exec_scenario.get_predicted_dataframe(desc_col)
        paginator = Paginator(df_output.values.tolist(), 1)
        page = request.GET.get('page')
        try:
            output_detail = paginator.page(page)
        except PageNotAnInteger:
            output_detail = paginator.page(1)
        except EmptyPage:
            output_detail = paginator.page(paginator.num_pages)
        context['output_detail'] = output_detail
        context['predictions'] = json.loads(output_detail[0][5])
    else:
        form = DocumentUploadForm()

    return render(request, 'incidents/index.html', context)
