import re
from datetime import date, datetime
import hashlib

from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .database import (
    create_user, get_user_by_username, get_user_by_id, update_user, delete_user,
    get_active_alerts, get_alert_history, acknowledge_alert, resolve_alert, get_alert_by_id,
    get_alert_thresholds, create_alert_threshold, update_alert_threshold, delete_alert_threshold,
    get_predictions, create_prediction, update_prediction, delete_prediction, analyze_predictions,
    get_alert_threshold
)

# Serializers
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, required=True)
    role = serializers.ChoiceField(choices=[('public', 'Public'), ('user', 'User'), ('admin', 'Admin')], default='user')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(required=True)

class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=10)
    created_at = serializers.DateTimeField(read_only=True)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Use serializer for validation
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        username = validated_data['username']
        email = validated_data.get('email', '')
        password = validated_data['password']
        role = validated_data.get('role', 'user')

        # Check if user already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Hash password
        hashed_password = make_password(password)

        # Create user using Supabase
        user = create_user(username, email, hashed_password, role)
        if user:
            # Return serialized user data
            response_serializer = CustomUserSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Use serializer for validation
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = get_user_by_username(username)
        if user and check_password(password, user['password']):
            class MockUser:
                def __init__(self, user_data):
                    self.id = user_data['id']
                    self.username = user_data['username']
                    self.email = user_data.get('email', '')
                    self.is_active = True
                    self.is_staff = user_data.get('role') == 'admin'
                    self.is_superuser = user_data.get('role') == 'admin'
                    self._user_data = user_data

                @property
                def pk(self):
                    return self.id

            mock_user = MockUser(user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(mock_user)
            access_token = refresh.access_token

            # Add custom claims to the access token
            access_token['user_id'] = user['id']
            access_token['username'] = user['username']
            access_token['role'] = user['role']
            access_token['email'] = user.get('email', '')

            # Serialize user data (without password)
            user_serializer = CustomUserSerializer(user)

            return Response({
                'user': user_serializer.data,
                'access': str(access_token),
                'refresh': str(refresh),
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class AlertListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = get_active_alerts()
        return Response(alerts)

class AlertHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = get_alert_history()
        return Response(alerts)

class AlertAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        alert = acknowledge_alert(pk)
        if alert:
            return Response(alert)
        else:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AlertResolveView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        alert = resolve_alert(pk)
        if alert:
            return Response(alert)
        else:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        user = get_user_by_id(pk)
        if user:
            # Remove password from response
            user_data = {k: v for k, v in user.items() if k != 'password'}
            return Response(user_data)
        else:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        user = get_user_by_id(pk)
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Hash password if provided
        update_data = request.data.copy()
        if 'password' in update_data:
            update_data['password'] = make_password(update_data['password'])

        updated_user = update_user(pk, update_data)
        if updated_user:
            # Remove password from response
            user_data = {k: v for k, v in updated_user.items() if k != 'password'}
            return Response(user_data)
        else:
            return Response(
                {'error': 'Failed to update user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        success = delete_user(pk)
        if success:
            return Response({'message': 'User deleted successfully'})
        else:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AlertThresholdViewSet(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        thresholds = get_alert_thresholds()
        return Response(thresholds)

    def post(self, request):
        threshold_type = request.data.get('type')
        value = request.data.get('value')
        zone = request.data.get('zone')

        if not threshold_type or value is None:
            return Response(
                {'error': 'Type and value are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        threshold = create_alert_threshold(threshold_type, value, zone)
        if threshold:
            return Response(threshold, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create threshold'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AlertThresholdDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        threshold = update_alert_threshold(pk, request.data)
        if threshold:
            return Response(threshold)
        else:
            return Response(
                {'error': 'Threshold not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        success = delete_alert_threshold(pk)
        if success:
            return Response({'message': 'Threshold deleted successfully'})
        else:
            return Response(
                {'error': 'Threshold not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PredictionViewSet(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        predictions = get_predictions()
        return Response(predictions)

    def post(self, request):
        pred_type = request.data.get('type')
        value = request.data.get('value')
        date = request.data.get('date')
        zone = request.data.get('zone')

        if not pred_type or value is None or not date:
            return Response(
                {'error': 'Type, value, and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prediction = create_prediction(pred_type, value, date, zone)
        if prediction:
            return Response(prediction, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to create prediction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PredictionDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        prediction = update_prediction(pk, request.data)
        if prediction:
            return Response(prediction)
        else:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        success = delete_prediction(pk)
        if success:
            return Response({'message': 'Prediction deleted successfully'})
        else:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PredictionAnalyzeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        result = analyze_predictions()
        return Response({'status': result})