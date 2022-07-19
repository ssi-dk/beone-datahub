from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    # return render(request, 'polls/index.html', context)
    return render(request, 'main/base.html')