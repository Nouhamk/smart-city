from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Alert, AlertThreshold, Prediction, CustomUser
from .serializers import AlertSerializer, AlertThresholdSerializer, PredictionSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.decorators import action

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

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class AlertThresholdViewSet(viewsets.ModelViewSet):
    queryset = AlertThreshold.objects.all()
    serializer_class = AlertThresholdSerializer
    permission_classes = [permissions.IsAdminUser]

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def analyze(self, request):
        for pred in self.get_queryset():
            try:
                threshold = AlertThreshold.objects.get(type=pred.type, zone=pred.zone).value
            except AlertThreshold.DoesNotExist:
                continue
            if pred.value > threshold:
                Alert.objects.create(
                    type=pred.type,
                    message=f"Prédiction : {pred.value} dépasse le seuil {threshold}",
                    level='warning',
                    status='active',
                    data={'prediction_id': pred.id, 'value': pred.value, 'threshold': threshold}
                )
        return Response({'status': 'Analyse terminée'}) 