from ast import Return

# from ssl import _PasswordType
from django.db.models import Avg,Max,Min,Sum,Count,StdDev,Variance
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from adminapp.models import *
from userapp.models import *
from django.core.paginator import Paginator

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "admin" and password == "admin":
            messages.success(request, "Logged In Successfully.")
            return redirect('admin_index')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('admin_login')
    return render(request, "admin/admin-login.html")

def admin_index(request):
    pend = UserdetailsModel.objects.filter(user_status="pending").count()
    all = UserdetailsModel.objects.all().count()
    ques = QuestionModel.objects.all().count()
    ans = AnswerModel.objects.all().count()
    return render(request,"admin/admin-index.html",{'ques':ques,'all':all,'ans':ans,'pend':pend})

def admin_pending(request):
    pending=UserdetailsModel.objects.filter(user_status="pending")
    paginator = Paginator(pending,5)
    page_no = request.GET.get('page')
    page = paginator.get_page(page_no)
    return render(request,"admin/admin-pending.html",{'pend':page})

def admin_all(request):
    all=UserdetailsModel.objects.all() 
    paginator = Paginator(all,5)
    page_no = request.GET.get('page')
    page = paginator.get_page(page_no)
    return render(request,"admin/admin-all.html",{'all':page})



def admin_add_subject(request):
    sub =  SubjectModel.objects.all()
    if request.method == "POST" and request.FILES['photo']:
        subject = request.POST.get('subject')
        photo = request.FILES['photo']

        try:
            SubjectModel.objects.get(subject = subject.lower())
            
            messages.error(request,"This subject already exists, Try another subject")
            return redirect('admin_add_subject')
        except:
            SubjectModel.objects.create(subject = subject.lower(),subject_image = photo)
            messages.success(request,subject+" subject added successfully")
            return redirect('admin_add_subject')
    return render(request,"admin/admin-add-subject.html",{'sub':sub})


def admin_add_question(request):
    sub = SubjectModel.objects.all()
    print(sub,'sub model')
    if request.method == "POST":
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        subject = request.POST.get('subject')
        if QuestionModel.objects.filter(subject = subject).count() <= 4:
            
            QuestionModel.objects.create(question = question,answer = answer,subject = subject)
            messages.success(request,"Question added successfully")
            return redirect('admin_add_question')
        else:
            messages.info(request,"Limit reached for question in "+subject+", Remove some question to add new question")
            return redirect('admin_add_question')
    return render(request,"admin/admin-add-question.html",{'sub':sub})

def admin_manage_question(request):
    ques = QuestionModel.objects.all()
    paginator = Paginator(ques,5)
    page_no = request.GET.get('page')
    page = paginator.get_page(page_no)
    return render(request,"admin/admin-manage-question.html",{'ques':page})

def admin_results(request):
    result = AnswerModel.objects.all()
    paginator = Paginator(result,5)
    page_no = request.GET.get('page')
    page = paginator.get_page(page_no)
    return render(request,"admin/admin-results.html",{'result':page})

def admin_analysis_graph(request):
    f = AnswerModel.objects.filter(grade = 'F').count()
    c = AnswerModel.objects.filter(grade = 'C').count()
    b = AnswerModel.objects.filter(grade = 'B').count()
    a = AnswerModel.objects.filter(grade = 'A').count()

    return render(request,"admin/admin-analysis-graph.html",{'a':a,'b':b,'c':c,'f':f,})

def accept_user(request,user_id):
    accept = get_object_or_404(UserdetailsModel,user_id=user_id)
    accept.user_status = "accepted"
    accept.save(update_fields=["user_status"])
    accept.save()
    if accept:
        messages.success(request,"User Added Successfully")

    return redirect('admin_pending')

def decline_user(request,user_id):
    decline = get_object_or_404(UserdetailsModel,user_id=user_id)
    decline.user_status = "declined"
    decline.save(update_fields=["user_status"])
    decline.save()
    if decline:
        messages.success(request,"Rejected Successfully")

    return redirect('admin_pending',user_id)

def remove_questions(request,question_id):
    remove = get_object_or_404(QuestionModel,question_id=question_id).delete()

    if remove:
        messages.success(request,"Question Removed Successfully")
    return redirect('admin_manage_question')


def remove_subject(request,subject_id):
    remove = get_object_or_404(SubjectModel,subject_id=subject_id).delete()
    if remove:
        messages.success(request,"Subject Removed Successfully")
    return redirect('admin_add_subject')