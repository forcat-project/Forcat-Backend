from rest_framework import serializers
from account.models import Cat
from datetime import date


class CatSerializer(serializers.ModelSerializer):
    days_since_birth = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = [
            "name",
            "cat_breed",
            "birth_date",
            "gender",
            "is_neutered",
            "weight",
            "user",
            "days_since_birth",
        ]

    def get_days_since_birth(self, obj):
        if obj.birth_date:
            delta = date.today() - obj.birth_date
            return delta.days
        return None
