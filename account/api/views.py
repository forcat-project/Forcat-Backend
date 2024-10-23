from rest_framework import viewsets
from account.models import Cat
from account.api.serializers import CatSerializer

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer