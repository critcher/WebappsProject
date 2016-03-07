from django.shortcuts import render

# Create your views here.


def home(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    # in template check for user.is_authenticated
    context['user'] = request.user
    return render(request, 'main.html', context)
