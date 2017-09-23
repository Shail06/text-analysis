import os
from django.http import HttpResponse
from django.shortcuts import render
from .forms import DocumentUploadForm
from incidents.algo.execution import ExecuteScenario

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .db_populate import PopulateDB

from django.core.files.storage import FileSystemStorage
import time
import json


def index(request):
    home_title = "Incident Analysis"
    message_upload = "uploaded successfully!"
    context = {'home_title': home_title}
    exec_scenario = ExecuteScenario()
    db_object   = PopulateDB()
    request.session.flush()
    #print("inside index")
    # import pdb;
    # pdb.set_trace();

    if(request.method == 'POST'):
        if ('upload' in request.POST):
            form = DocumentUploadForm(request.POST, request.FILES)
            if(form.is_valid()):
                upFile = request.FILES['docfile']
                name, extension = os.path.splitext(upFile.name)
                upFilename = name + time.strftime("%Y%m%d-%H%M%S") + extension
                request.session["file_name"] = upFilename
                fs = FileSystemStorage()
                filename = fs.save('uploads/' + upFilename, upFile)

                if not 'prev_files' in request.session or not request.session['prev_files']:
                    request.session["prev_files"] = []

                if len(request.session["prev_files"]) > 0:
                    try:
                        for x in request.session["prev_files"]:
                            os.remove(x)
                    except IOError:
                        pass

                    request.session["prev_files"] = []

                if filename:
                    request.session["prev_files"].append(filename)

                context['upload_success'] = upFile.name
                request.session['upload_success'] = context['upload_success']
                df_cols = exec_scenario.get_column_headers(filename)
                context['all_columns'] = df_cols
                request.session['all_columns'] = df_cols

        elif('start' in request.POST):
            incid_col = request.POST['incident_id']
            desc_col = request.POST.getlist('description')
            perf_action = request.POST['perform_action']

            request.session['incid_col'] = incid_col
            request.session['desc_cols'] = desc_col
            request.session['perform_action'] = perf_action

            context['upload_success'] = request.session['upload_success']
            context['incid_col'] = incid_col
            context['perform_action'] = perf_action
            context['desc_cols'] = desc_col
            context['all_columns'] = request.session['all_columns']
            df_cols = exec_scenario.get_column_headers(
                request.session["prev_files"][0])
            # import pdb;
            # pdb.set_trace()
            temp_file = "output/temp/" + request.session["file_name"]

            if( not 'knowledge_altered' in request.session):
                request.session["knowledge_altered"] = "no"

            if(request.session["knowledge_altered"] == "no" and os.path.isfile(temp_file)):
                df_output = exec_scenario.get_input_dataframe(temp_file)
            else:
                start_time = time.time()
                df_output = exec_scenario.get_predicted_dataframe(desc_col)
                end_time = time.time()
                print(end_time - start_time)
                request.session["knowledge_altered"] = "no"

            df_output_single = df_output[
                [incid_col, 'combined_desc', 'summary', 'Predictions Detail']]
            paginator = Paginator(df_output_single.values.tolist(), 1)
            page = request.GET.get('page')
            try:
                output_detail = paginator.page(page)
            except PageNotAnInteger:
                output_detail = paginator.page(1)
            except EmptyPage:
                output_detail = paginator.page(paginator.num_pages)
            context['output_detail'] = output_detail
            context['predictions'] = json.loads(output_detail[0][-1])

            # For Performing whole document prediction
            c_stats, pred_stat_list = exec_scenario.get_prediction_statistics(
                df_output, incid_col)
            context["stats"] = pred_stat_list
            context["LABELS"] = c_stats.index.values.tolist()
            context["LABEL_COUNTS"] = c_stats.values.tolist()
            df_output_multiple = df_output.drop(
                ['combined_desc', 'summary', 'Predictions Detail'], axis=1)

            op_name = request.session["file_name"]
            #df_output['combined_desc'] = df_output.combined_desc.str.replace(r'\n', ' <br/> ')
            #exec_scenario.save_output(df_output, 'output/temp/' + op_name)  ## CREATE A DATABASE TABLE AND SAVE THE DATAFRAME
            db_object.fill_table(df_output, op_name)
            exec_scenario.save_output(df_output_multiple, 'output/' + op_name)
            context["download_file"] = "output/" + op_name
            request.session["prev_files"].append("output/" + op_name)
            #request.session["prev_files"].append("output/temp/" + op_name)

    elif('page' in request.GET):
        context['upload_success'] = request.session['upload_success']
        context['all_columns'] = request.session['all_columns']
        context['incid_col'] = request.session['incid_col']
        context['desc_cols'] = request.session['desc_cols']
        context['perform_action'] = request.session['perform_action']

        desc_col = request.session['desc_cols']
        incid_col = request.session['incid_col']
        df_cols = exec_scenario.get_column_headers(request.session["prev_files"][
            0])  # Necessary step for next step
        file_name = request.session["file_name"]
        df_output = exec_scenario.get_input_dataframe(
            "output/temp/" + file_name)
        df_output_single = df_output[
            [incid_col, 'combined_desc', 'summary', 'Predictions Detail']]

        paginator = Paginator(df_output_single.values.tolist(), 1)
        page = request.GET.get('page')
        try:
            output_detail = paginator.page(page)
        except PageNotAnInteger:
            output_detail = paginator.page(1)
        except EmptyPage:
            output_detail = paginator.page(paginator.num_pages)
        context['output_detail'] = output_detail
        context['predictions'] = json.loads(output_detail[0][-1])

    else:
        form = DocumentUploadForm()

    return render(request, 'incidents/index.html', context)


import os
from django.http import HttpResponse


def download(request):
    file_path = "output/" + request.session["file_name"]
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    raise Http404


from django.views.generic.base import TemplateView


class ajax_view(TemplateView):

    def post(self, request, *args, **kwargs):
        exec_scenario = ExecuteScenario()
        print("inside ajax view")
        incident_summary = request.POST.get('incident_summary')
        predicted_label = request.POST.get('predicted_label')
        print(incident_summary)
        print(predicted_label)
        exec_scenario.save_to_knowledge(incident_summary, predicted_label)
        request.session["knowledge_altered"] = "yes"
        return HttpResponse({"incident_summary": incident_summary}, content_type='application/json')
