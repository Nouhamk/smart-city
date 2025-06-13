from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Alert
from .serializers import AlertSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.filter(status='active')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

class AlertHistoryView(generics.ListAPIView):
    queryset = Alert.objects.exclude(status='active')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

class AlertAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.status = 'acknowledged'
            alert.acknowledged_at = timezone.now()
            alert.save()
            return Response(AlertSerializer(alert).data)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

class AlertResolveView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.save()
            return Response(AlertSerializer(alert).data)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND) 