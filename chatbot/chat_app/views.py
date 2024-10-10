from django.shortcuts import render

# Create your views here.
def chatbot_view(request):
    user=request.user
    return render(request, 'chat_app/index.html')