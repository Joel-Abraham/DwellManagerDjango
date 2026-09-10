from rest_framework import serializers
from .models import Flat, Resident, MaintenanceRequest, Visitor, Payment


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = "__all__"


class ResidentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Resident
        fields = [
            "id",
            "flat",
            "username",
            "password",
            "full_name",
            "contact_number",
            "email",
            "role",
            "status",
            "move_in_date",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = Resident(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = "__all__"


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
