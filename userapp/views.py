from django.db.models import Avg,Max,Min,Sum,Count,StdDev,Variance
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from adminapp.models import QuestionModel, SubjectModel
from userapp.models import *
from django.core.paginator import Paginator
from userapp.text_similarity import *
import json
import ast
from transformers import pipeline
from PIL import Image
import os
from kraken import pageseg, binarization
import shutil
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import time
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .decorators import custom_login_required
from django.db import connection
from rest_framework import status
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    return render(request,"user/index.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = UserdetailsModel.objects.get(user_email=username, user_password=password)
            if user.user_status == "accepted":
                # Set the session
                request.session['user_id'] = user.user_id
                # Set session expiry to 0 to expire when browser closes
                request.session.set_expiry(0)
                messages.success(request, 'Successfully Logged In')
                return redirect('user_dashboard')
            elif user.user_status == "pending":
                messages.info(request, 'Your id is pending for registration')
                return redirect('user_login')
            elif user.user_status == "blocked":
                messages.error(request, 'You Are BLOCKED From Logging In')
                return redirect('user_login')
            else:
                messages.error(request, 'You are not registered, try again after signup')
                return redirect('user_login')
            
        except UserdetailsModel.DoesNotExist:
            messages.error(request, 'Invalid login credentials')
            return redirect('user_login')
    return render(request, "user/user-login.html")


def user_register(request):
    if request.method == "POST":
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            password = request.POST.get('password')
            student_id = request.POST.get('id')
            photo = request.FILES.get('photo')

            # Debug print
            print(f"Received registration data: {name}, {email}, {contact}, {student_id}")

            # Check if email exists
            if UserdetailsModel.objects.filter(user_email=email).exists():
                messages.info(request, "Email already exists, try again with another email")
                return redirect('user_register')

            # Create new user
            user_create = UserdetailsModel.objects.create(
                user_name=name,
                user_email=email,
                user_password=password,
                user_contact=contact,
                student_id=student_id,
                user_photo=photo
            )

            if user_create:
                messages.success(request, "Successfully Registered")
                print(f"User created successfully with ID: {user_create.user_id}")
                return redirect('user_register')
            else:
                messages.error(request, "Failed to create user")
                return redirect('user_register')

        except Exception as e:
            print(f"Error during registration: {str(e)}")
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('user_register')

    return render(request, "user/user-register.html")

def user_contact(request):
    return render(request,"user/user-contact.html")



def user_dashboard(request):
    user_id=request.session['user_id']
    user=UserdetailsModel.objects.get(user_id=user_id)
    exam  = AnswerModel.objects.filter(user_id=user_id).count()
    exams  = AnswerModel.objects.filter(user_id=user_id)
    sub = []
    for i in exams:
        if i.answer_subject not in sub:
            sub.append(i.answer_subject)
    ques = AnswerModel.objects.filter(user_id=user_id).count()*4
    su = len(sub)
    return render(request,"user/user-dashboard.html",{'exams':exam,'subjects':su,'ques':ques})


def user_questions(request,subject):
    user_id=request.session['user_id']
    user=UserdetailsModel.objects.get(user_id=user_id)
    
    sub = QuestionModel.objects.filter(subject = subject)
    for i in sub:
        pass
    if request.method == 'POST':
        # Process answer sheets if uploaded
        answer_sheets = {}
        processing_errors = []
        
        # First, process all answer sheets
        for i in range(1, 6):
            answer_sheet = request.FILES.get(f'answer_sheet_{i}')
            if answer_sheet:
                try:
                    extracted_text = process_answer_sheet(answer_sheet)
                    if extracted_text:
                        answer_sheets[i] = extracted_text
                    else:
                        processing_errors.append(f"Question {i}: No text extracted from the answer sheet")
                except Exception as e:
                    print(f"Error processing answer sheet {i}: {str(e)}")
                    processing_errors.append(f"Question {i}: Error processing answer sheet - {str(e)}")
                    answer_sheets[i] = None

        # If there are processing errors, show them to the user
        if processing_errors:
            messages.error(request, "Some answer sheets could not be processed. Please try again or use text input.")
            for error in processing_errors:
                messages.warning(request, error)
            return redirect('user_questions', subject=subject)

        # Get text inputs as fallback
        q1 = request.POST.get('question1', '')
        q2 = request.POST.get('question3', '')
        q3 = request.POST.get('question4', '')
        q4 = request.POST.get('question5', '')
        q5 = request.POST.get('question6', '')

        # Use extracted text from answer sheets if available, otherwise use text input
        r1 = int((get_combined_similarity_score(answer_sheets.get(1, q1), sub[0].answer))*20)
        r2 = int((get_combined_similarity_score(answer_sheets.get(2, q2), sub[1].answer))*20)
        r3 = int((get_combined_similarity_score(answer_sheets.get(3, q3), sub[2].answer))*20)
        r4 = int((get_combined_similarity_score(answer_sheets.get(4, q4), sub[3].answer))*20)
        r5 = int((get_combined_similarity_score(answer_sheets.get(5, q5), sub[4].answer))*20)

        score = r1+r2+r3+r4+r5
        grade =''
        if score == 0 or score <= 24:
            grade='F'
        elif score >= 25 and score <= 49:
            grade = 'C'
        elif score >=50 and score <= 75:
            grade = 'B'
        elif score >= 76 and score <= 100:
            grade = 'A'

        answer = {}
        answer['question1'] ={'question':sub[0].question,'answer':answer_sheets.get(1, q1),'marks':str(r1)}
        answer['question2'] ={'question':sub[1].question,'answer':answer_sheets.get(2, q2),'marks':str(r2)}
        answer['question3'] ={'question':sub[2].question,'answer':answer_sheets.get(3, q3),'marks':str(r3)}
        answer['question4'] ={'question':sub[3].question,'answer':answer_sheets.get(4, q4),'marks':str(r4)}
        answer['question5'] ={'question':sub[4].question,'answer':answer_sheets.get(5, q5),'marks':str(r5)}

        AnswerModel.objects.create(answer_subject = subject,answer = answer,user_id = user,score = score,grade = grade)

        messages.success(request,"Answers submitted successfully")
        return redirect("user_exam")
    try:
        return render(request,"user/user-questions.html",{'quest1':sub[0],'quest2':sub[1],'quest3':sub[2],'quest4':sub[3],'quest5':sub[4],})
    except:
        messages.error(request,"Something Went Wrong, Check with admin if questions are added and try again.")
        return redirect("user_exam")


def user_view_results(request, answer_id):
    try:
        # Clear any existing temporary results
        TempModel.objects.all().delete()
        
        # Get the answer result
        result = AnswerModel.objects.get(answer_id=answer_id)
        
        # Parse the answer string into a dictionary
        try:
            # First try to parse as JSON
            import json
            answer_dict = json.loads(result.answer.replace("'", '"'))
        except:
            try:
                # If JSON parsing fails, try eval
                answer_dict = eval(result.answer)
            except:
                # If both fail, try to parse manually
                answer_dict = {}
                import re
                # Extract question blocks
                question_blocks = re.findall(r"'question\d+':\s*({[^}]+})", result.answer)
                for block in question_blocks:
                    # Extract question details
                    question = re.search(r"'question':\s*'([^']+)'", block)
                    answer = re.search(r"'answer':\s*'([^']+)'", block)
                    marks = re.search(r"'marks':\s*'([^']+)'", block)
                    
                    if question and answer and marks:
                        answer_dict[question.group(1)] = {
                            'question': question.group(1),
                            'answer': answer.group(1),
                            'marks': marks.group(1)
                        }
        
        # Create temporary entries for each answer
        for key, value in answer_dict.items():
            if isinstance(value, dict):
                # Check if the answer contains OCR extracted text
                answer_text = value.get('answer', '')
                if answer_text.startswith("Error processing answer sheet"):
                    # If there was an error processing the answer sheet, show the error message
                    answer_text = "Error processing answer sheet. Please try again."
                elif answer_text and not answer_text.startswith("Error"):
                    # If we have valid extracted text, use it
                    pass
                else:
                    # If no extracted text, use the text input
                    answer_text = value.get('answer', '')
                
                TempModel.objects.create(
                    subject=result.answer_subject,
                    question=value.get('question', ''),
                    answer=answer_text,
                    score=value.get('marks', '0')
                )
            else:
                # If value is not a dictionary, log it and skip
                print(f"Unexpected value format for key {key}: {value}")
        
        # Get all results for display
        f_results = TempModel.objects.all()
        
        return render(request, "user/user-view-results.html", {'result': f_results})
        
    except AnswerModel.DoesNotExist:
        messages.error(request, "Answer not found")
        return redirect('user_results')
    except Exception as e:
        print(f"Error in user_view_results: {str(e)}")
        print(f"Answer string: {result.answer if 'result' in locals() else 'No result'}")
        messages.error(request, f"Error viewing results: {str(e)}")
        return redirect('user_results')







def user_results(request):
    user_id=request.session['user_id']

    result = AnswerModel.objects.filter(user_id = user_id)
    return render(request,"user/user-results.html",{'result':result})

def user_myprofile(request):
    user_id=request.session['user_id']
    user=UserdetailsModel.objects.get(user_id=user_id)

    
    if request.method=="POST":
        if len(request.FILES) ==0:
            name=request.POST.get("name")
            
            email=request.POST.get("email")
            password=request.POST.get("password")
            contact=request.POST.get("contact")
            id = request.POST.get("id")
            
            user.user_name = name
            
            user.user_email = email
            user.user_password = password
            user.user_contact = contact
            user.student_id =  id
            

            user.save()
            if user:
                messages.success(request,"Succesflly Updated")
                return redirect("user_myprofile")

            else:
                messages.error(request,"No changes detected")
                return redirect("user_myprofile")
    else:
        if request.method=="POST" and request.FILES['photo']:
            name=request.POST.get("name")
        
            email=request.POST.get("email")
            password=request.POST.get("password")
            contact=request.POST.get("contact")
            id = request.POST.get("id")
            
            photo=request.FILES["photo"]
            user.user_name = name
            
            user.user_email = email
            user.user_password = password
            user.user_contact = contact
            user.student_id =  id
            user.user_photo = photo
            
            

            user.save()
            if user:
                messages.success(request,"Succesflly Updated")
                return redirect("user_myprofile")
            

                

            else:
                messages.error(request,"No changes detected")
                return redirect("user_myprofile")
    return render(request,"user/user-myprofile.html",{'user':user})

def user_exam(request):
    sub = SubjectModel.objects.all()

    return render(request,"user/user-exam.html",{'sub':sub})

def upload_answer(request):
    if not request.session.get('user_id'):
        messages.error(request, "Please login first")
        return redirect('user_login')
        
    user_id = request.session['user_id']
    user = UserdetailsModel.objects.get(user_id=user_id)
    
    if request.method == 'GET':
        subjects = SubjectModel.objects.all()
        return render(request, 'user/upload-answer.html', {'subjects': subjects})
    
    if request.method == 'POST':
        try:
            subject = request.POST.get('subject')
            answer_text = request.POST.get('answer_text')
            question_id = request.POST.get('question')
            
            if not all([subject, answer_text, question_id]):
                messages.error(request, "Please fill all fields")
                subjects = SubjectModel.objects.all()
                try:
                    selected_question = QuestionModel.objects.get(id=question_id) if question_id else None
                except QuestionModel.DoesNotExist:
                    selected_question = None
                    
                return render(request, 'user/upload-answer.html', {
                    'subjects': subjects,
                    'selected_subject': subject,
                    'selected_question': selected_question,
                    'answer_text': answer_text
                })
                
            # Get the question and its correct answer
            question = QuestionModel.objects.get(id=question_id)
            correct_answer = question.answer
            
            # Calculate similarity score
            similarity_score = get_combined_similarity_score(answer_text, correct_answer)
            
            # Convert to percentage and round to 2 decimal places
            score_percentage = round(similarity_score * 100, 2)
            
            # Determine grade
            if score_percentage >= 90:
                grade = 'A'
            elif score_percentage >= 80:
                grade = 'B'
            elif score_percentage >= 70:
                grade = 'C'
            elif score_percentage >= 60:
                grade = 'D'
            else:
                grade = 'F'
            
            # Create answer dictionary
            answer_dict = {
                'question1': {
                    'question': question.question,
                    'answer': answer_text,
                    'marks': str(score_percentage)
                }
            }
            
            # Save the answer
            answer = AnswerModel.objects.create(
                answer_subject=subject,
                answer=answer_dict,
                user_id=user,
                score=score_percentage,
                grade=grade
            )
            
            messages.success(request, f"Answer submitted successfully! Score: {score_percentage}%, Grade: {grade}")
            return redirect('user_results')
            
        except QuestionModel.DoesNotExist:
            messages.error(request, "Invalid question selected")
            subjects = SubjectModel.objects.all()
            return render(request, 'user/upload-answer.html', {
                'subjects': subjects,
                'selected_subject': subject,
                'answer_text': answer_text
            })
        except Exception as e:
            messages.error(request, f"Error processing answer: {str(e)}")
            subjects = SubjectModel.objects.all()
            return render(request, 'user/upload-answer.html', {
                'subjects': subjects,
                'selected_subject': subject,
                'answer_text': answer_text
            })

def get_questions(request, exam_id):
    questions = QuestionModel.objects.filter(exam_id=exam_id).values('question_id', 'question')
    return JsonResponse({'questions': list(questions)})

def segment_with_kraken(image_path, output_folder="kraken_lines"):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    img = Image.open(image_path).convert('L')
    bin_img = binarization.nlbin(img)
    bounds = pageseg.segment(bin_img)

    for idx, line in enumerate(bounds.lines):
        x0, y0, x1, y1 = line.bbox
        line_img = bin_img.crop((x0, y0, x1, y1))
        line_path = os.path.join(output_folder, f"line_{idx:02d}.png")
        line_img.save(line_path)

@api_view(['POST'])
def compare_texts_api(request):
    """
    API endpoint to compare two texts and return similarity score
    """
    try:
        data = request.data
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        
        if not text1 or not text2:
            return Response({'error': 'Both text1 and text2 are required'}, status=400)
            
        similarity_score = get_combined_similarity_score(text1, text2)
        
        return Response({
            'text1': text1,
            'text2': text2,
            'similarity_score': similarity_score
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_questions_by_subject(request, subject):
    try:
        print(f"Fetching questions for subject: {subject}")
        
        # Check database connection
        try:
            connection.ensure_connection()
            print("Database connection successful")
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return JsonResponse({'error': 'Database connection error'}, status=500)
        
        # Get questions for the subject
        questions = QuestionModel.objects.filter(subject=subject).values('question_id', 'question')
        print(f"Found questions: {list(questions)}")
        
        if not questions.exists():
            print(f"No questions found for subject: {subject}")
            return JsonResponse({'error': f'No questions found for subject: {subject}'}, status=404)
            
        questions_list = list(questions)
        print(f"Returning {len(questions_list)} questions for subject: {subject}")
        
        return JsonResponse({
            'questions': questions_list
        })
    except Exception as e:
        print(f"Error in get_questions_by_subject: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': f'Error loading questions: {str(e)}',
            'details': traceback.format_exc()
        }, status=500)

def process_answer_sheet(image_file):
    try:
        # Save the uploaded file temporarily
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', image_file.name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Call the OCR API (Google Colab)
        api_url = "https://7c37-34-106-113-89.ngrok-free.app/ocr"
        with open(temp_path, 'rb') as img_file:
            response = requests.post(api_url, files={"file": img_file})
        
        # Clean up temporary file
        os.remove(temp_path)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('extracted_text', '')
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error processing answer sheet: {str(e)}")
        raise

@custom_login_required
def upload_answer_sheet(request):
    if request.method == "POST":
        try:
            subject = request.POST.get("subject")
            if not subject:
                messages.error(request, "Please select a subject")
                return redirect('upload_answer_sheet')
            
            # Get all questions for the subject
            questions = QuestionModel.objects.filter(subject=subject)
            if not questions.exists():
                messages.error(request, "No questions found for this subject")
                return redirect('upload_answer_sheet')
            
            user = UserdetailsModel.objects.get(user_id=request.session['user_id'])
            
            # Process each answer sheet
            answer_dict = {}
            total_score = 0
            
            for question in questions:
                answer_sheet = request.FILES.get(f"answer_sheet_{question.question_id}")
                if not answer_sheet:
                    continue
                
                try:
                    # Process the answer sheet through OCR
                    extracted_text = process_answer_sheet(answer_sheet)
                    print(f"Extracted text for question {question.question_id}: {extracted_text}")
                    
                    # Calculate similarity score
                    similarity_score = get_combined_similarity_score(extracted_text, question.answer)
                    score_percentage = int(round(similarity_score * 100))  # Convert to integer
                    
                    # Add to answer dictionary
                    answer_dict[f'question{question.question_id}'] = {
                        'question': question.question,
                        'answer': extracted_text,
                        'marks': str(score_percentage)  # Store as string in the dictionary
                    }
                    
                    total_score += score_percentage
                    
                except Exception as e:
                    print(f"Error processing answer sheet for question {question.question_id}: {str(e)}")
                    answer_dict[f'question{question.question_id}'] = {
                        'question': question.question,
                        'answer': f"Error processing answer: {str(e)}",
                        'marks': '0'
                    }
            
            # Calculate average score and grade
            avg_score = int(total_score / len(questions)) if questions else 0  # Convert to integer
            grade = 'A' if avg_score >= 90 else 'B' if avg_score >= 80 else 'C' if avg_score >= 70 else 'D' if avg_score >= 60 else 'F'
            
            # Save the answer
            AnswerModel.objects.create(
                answer_subject=subject,
                answer=str(answer_dict),
                user_id=user,
                score=avg_score,  # This is now an integer
                grade=grade
            )
            
            messages.success(request, "Answer sheets uploaded and processed successfully")
            return redirect('user_results')
            
        except Exception as e:
            print(f"Error in upload_answer_sheet: {str(e)}")
            messages.error(request, f"Error processing answer sheets: {str(e)}")
            return redirect('upload_answer_sheet')
    
    # GET request - show the form
    subjects = SubjectModel.objects.all()
    return render(request, "user/upload-answer-sheet.html", {'subjects': subjects})