import difflib
# from codeapp.utils import handle_c_file, handle_java_file, handle_sql_file, handle_bash_file

from django.shortcuts import render
import os
import subprocess
from .forms import CodeUploadForm

def normalize_code(code):
    return ''.join(line.strip() for line in code.splitlines() if line.strip())
def check_plagiarism(new_code, folder_path, current_file):
    plagiarism_results = []
    for fname in os.listdir(folder_path):
        if fname == os.path.basename(current_file):
            continue
        if fname.endswith(('.c', '.java', '.sql', '.sh')):
            existing_path = os.path.join(folder_path, fname)
            with open(existing_path, "r") as f:
                existing_code = normalize_code(f.read())
                similarity = difflib.SequenceMatcher(None, new_code, existing_code).ratio()
                if similarity > 0.7:
                    plagiarism_results.append((fname, round(similarity * 100, 2)))
    return plagiarism_results

# def upload_code(request):
#     result = None
#     error = None
#
#     if request.method == 'POST':
#         form = CodeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             code_file = request.FILES['code_file']
#             media_dir = 'media'
#             if not os.path.exists(media_dir):
#                 os.makedirs(media_dir)
#
#             file_path = os.path.join(media_dir, code_file.name)
#
#             # Save file first
#             with open(file_path, 'wb+') as destination:
#                 for chunk in code_file.chunks():
#                     destination.write(chunk)
#
#             if code_file.name.endswith('.c'):
#                 print("code is C")
#                 compile_cmd = f"gcc {file_path} -o {media_dir}/output.out"
#                 try:
#                     process = subprocess.Popen(compile_cmd.split(), stderr=subprocess.PIPE)
#                     _, stderr = process.communicate()
#                     if stderr:
#                         error = stderr.decode()
#                     else:
#                         # If no error, run the program
#                         run_cmd = f"./{media_dir}/output.out"
#                         run_process = subprocess.Popen(run_cmd.split(), stdout=subprocess.PIPE)
#                         output, _ = run_process.communicate()
#                         result = output.decode()
#                 except Exception as e:
#                     error = str(e)
#
#             elif code_file.name.endswith('.java'):
#                 print("code is Java")
#
#                 result, error = handle_java_file(file_path)
#
#             elif code_file.name.endswith('.sql'):
#                 result, error = handle_sql_file(file_path)
#
#             elif code_file.name.endswith('.sh'):
#                 result, error = handle_bash_file(file_path)
#
#
#
#
#                 # TODO: elif file endswith .sh / .sql — add other language handlers
#
#     else:
#         form = CodeUploadForm()
#
#     return render(request, 'upload.html', {'form': form, 'result': result, 'error': error})


# def upload_code(request):
#     result = None
#     error = None
#     plagiarism_report = []
#
#     if request.method == 'POST':
#         form = CodeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             code_file = request.FILES['code_file']
#
#             media_dir = 'media'
#             os.makedirs(media_dir, exist_ok=True)
#
#             file_path = os.path.join(media_dir, code_file.name)
#             with open(file_path, 'wb+') as destination:
#                 for chunk in code_file.chunks():
#                     destination.write(chunk)
#
#             if code_file.name.endswith('.c'):
#                 with open(file_path, 'r') as f:
#                     new_code = normalize_code(f.read())
#                 plagiarism_report = check_plagiarism(new_code, media_dir, file_path)
#
#                 # Compile and run
#                 compile_cmd = f"gcc {file_path} -o media/output.out"
#                 try:
#                     process = subprocess.Popen(compile_cmd.split(), stderr=subprocess.PIPE)
#                     _, stderr = process.communicate()
#                     if stderr:
#                         error = stderr.decode()
#                     else:
#                         run_cmd = "./media/output.out"
#                         run_process = subprocess.Popen(run_cmd.split(), stdout=subprocess.PIPE)
#                         output, _ = run_process.communicate()
#                         result = output.decode()
#                 except Exception as e:
#                     error = str(e)
#
#     else:
#         form = CodeUploadForm()
#
#     return render(request, 'upload.html', {
#         'form': form,
#         'result': result,
#         'error': error,
#         'plagiarism': plagiarism_report
#     })


def upload_code(request):
    result = None
    error = None
    plagiarism_report = None

    if request.method == 'POST':
        form = CodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            code_file = request.FILES['code_file']
            file_name = code_file.name
            media_dir = 'media'
            os.makedirs(media_dir, exist_ok=True)

            file_path = os.path.join(media_dir, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in code_file.chunks():
                    destination.write(chunk)

            with open(file_path, 'r') as f:
                new_code = normalize_code(f.read())

            # Determine file type
            if file_name.endswith('.c'):
                result, error = handle_c_file(file_path)
                plagiarism_report = check_plagiarism(new_code, media_dir, file_path)

            elif file_name.endswith('.java'):
                result, error = handle_java_file(file_path)
                plagiarism_report = check_plagiarism(new_code, media_dir, file_path)

            elif file_name.endswith('.sql'):
                result, error = handle_sql_file(file_path)
                plagiarism_report = check_plagiarism(new_code, media_dir, file_path)

            elif file_name.endswith('.sh'):
                result, error = handle_bash_file(file_path)
                plagiarism_report = check_plagiarism(new_code, media_dir, file_path)

    else:
        form = CodeUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'result': result,
        'error': error,
        'plagiarism': plagiarism_report,
    })


def handle_java_file(file_path):
    dir_path = os.path.dirname(file_path)
    class_name = os.path.basename(file_path).replace(".java", "")

    try:
        compile = subprocess.run(['javac', file_path], stderr=subprocess.PIPE)
        if compile.returncode != 0:
            return "", compile.stderr.decode()

        run = subprocess.run(['java', '-cp', dir_path, class_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return run.stdout.decode(), run.stderr.decode()
    except Exception as e:
        return "", str(e)


import sqlite3

# def handle_sql_file(file_path):
#     try:
#         run = subprocess.run(['sqlite3', ':memory:', f".read {file_path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         return run.stdout, run.stderr
#     except Exception as e:
#         return "", str(e)

def handle_sql_file(file_path):
    try:
        # Build a command to run the `.read` inside sqlite3 with input
        file_path = file_path.replace("\\", "/")
        command = f".read {file_path}"
        run = subprocess.run(
            ['sqlite3', ':memory:'],
            input=command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return run.stdout, run.stderr
    except Exception as e:
        return "", str(e)


def handle_c_file(file_path):
    try:
        compile_cmd = ["gcc", file_path, "-o", "media/output.out"]
        compile = subprocess.run(compile_cmd, stderr=subprocess.PIPE)
        if compile.returncode != 0:
            return "", compile.stderr.decode()
        run = subprocess.run(["./media/output.out"], stdout=subprocess.PIPE)
        return run.stdout.decode(), ""
    except Exception as e:
        return "", str(e)


def handle_bash_file(file_path):
    try:
        os.chmod(file_path, 0o755)  # Ensure executable
        run = subprocess.run(['bash', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return run.stdout, run.stderr
    except Exception as e:
        return "", str(e)



import zipfile
import tempfile
# from .utils import handle_c_file, handle_java_file, handle_sql_file, handle_bash_file

def upload_zip(request):
    result = []
    if request.method == 'POST' and request.FILES.get('zip_file'):
        zip_file = request.FILES['zip_file']

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]
            normalized_codes = {}

            # Process each file
            for file_path in files:
                name = os.path.basename(file_path)
                error = ""
                output = ""
                lang = "unknown"
                status = "OK"

                try:
                    # with open(file_path, 'r') as f:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:

                        content = f.read()
                        normalized_codes[name] = normalize_code(content)

                    if name.endswith('.c'):
                        lang = "C"
                        output, error = handle_c_file(file_path)
                    elif name.endswith('.java'):
                        lang = "Java"
                        output, error = handle_java_file(file_path)
                    elif name.endswith('.sql'):
                        lang = "SQL"
                        output, error = handle_sql_file(file_path)
                    elif name.endswith('.sh'):
                        lang = "Bash"
                        output, error = handle_bash_file(file_path)

                    if error:
                        status = "Error"

                except Exception as e:
                    status = "Error"
                    error = str(e)

                result.append({
                    'filename': name,
                    'language': lang,
                    'status': status,
                    'error': error,
                    'output': output,
                    'content': content  # Include code content here

                })

            # Check Plagiarism
            for file_data in result:
                sim_results = []
                code1 = normalized_codes[file_data['filename']]
                for other_name, code2 in normalized_codes.items():
                    if file_data['filename'] != other_name:
                        similarity = difflib.SequenceMatcher(None, code1, code2).ratio()
                        if similarity > 0.7:
                            sim_results.append((other_name, round(similarity * 100, 2)))
                file_data['plagiarism'] = sim_results

    else:
        result = None

    return render(request, 'bulk_upload.html', {'results': result})

def index(request):
    return render(request, 'index.html')
def upload_page(request):
    return render(request, 'upload.html')


