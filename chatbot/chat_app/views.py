from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def chatbot_view(request):
    user=request.user
    return render(request, 'chat_app/index.html')