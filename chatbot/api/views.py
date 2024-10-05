from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import UserSerializer
from .models import User
# Create your views here.

# Create your views here.
@api_view(['GET','POST'])
def getUser(request):
    if request.method == 'GET':
        query = User.objects.all()
        serializer = UserSerializer(query,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        user = UserSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def getUserForId(request,id):
    try:
        query = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error' : {
        'code' : 404,
        'message' : "Article not found!"
    }}, status = status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(query)
        return Response(serializer.data)
    elif request.method=='PUT':
        user = UserSerializer(query,data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='DELETE':
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)