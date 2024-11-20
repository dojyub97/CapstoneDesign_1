from django.urls import path
from .views import upload_pdf, query_chatbot, index
from . import views 

urlpatterns = [
    #path("upload/", upload_pdf, name="upload_pdf"),
    path("upload/", index, name="index"),
    path("query/", query_chatbot, name="query_chatbot"),
    path('fetch-result-content/', views.fetch_result_content, name='fetch_result_content'),
]
