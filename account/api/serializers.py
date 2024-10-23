from rest_framework import serializers
from account.models import Cat

class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ['name', 'cat_breed', 'birth_date', 'gender', 'is_neutered', 'weight', 'user']