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

# drf-spectacular imports
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample,
    OpenApiResponse, inline_serializer
)
from drf_spectacular.types import OpenApiTypes

from .database import (
    create_user, get_user_by_username, get_user_by_id, update_user, delete_user,
    get_active_alerts, get_alert_history, acknowledge_alert, resolve_alert, get_alert_by_id,
    get_alert_thresholds, create_alert_threshold, update_alert_threshold, delete_alert_threshold,
    get_predictions, create_prediction, update_prediction, delete_prediction, analyze_predictions,
    get_alert_threshold
)

# ===== SERIALIZERS =====

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, help_text="Unique username")
    email = serializers.EmailField(required=False, allow_blank=True, help_text="User email address")
    password = serializers.CharField(min_length=8, required=True, help_text="Password (minimum 8 characters)")
    role = serializers.ChoiceField(
        choices=[('public', 'Public'), ('user', 'User'), ('admin', 'Admin')],
        default='user',
        help_text="User role"
    )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, help_text="Username")
    password = serializers.CharField(required=True, help_text="Password")

class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=10)
    created_at = serializers.DateTimeField(read_only=True)

class LoginResponseSerializer(serializers.Serializer):
    user = CustomUserSerializer()
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    message = serializers.CharField()

class AlertSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=[('rain', 'Rain'), ('heatwave', 'Heatwave'), ('wind', 'Wind'), ('custom', 'Custom')])
    message = serializers.CharField()
    level = serializers.CharField()
    status = serializers.ChoiceField(choices=[('active', 'Active'), ('acknowledged', 'Acknowledged'), ('resolved', 'Resolved'), ('archived', 'Archived')])
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    acknowledged_at = serializers.DateTimeField(allow_null=True)
    resolved_at = serializers.DateTimeField(allow_null=True)
    data = serializers.JSONField(allow_null=True)

class AlertThresholdSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(help_text="Threshold type (rain, heatwave, pollution, etc.)")
    value = serializers.FloatField(help_text="Threshold value")
    zone = serializers.CharField(allow_null=True, help_text="Geographic zone (optional)")

class AlertThresholdRequestSerializer(serializers.Serializer):
    type = serializers.CharField(help_text="Threshold type")
    value = serializers.FloatField(help_text="Threshold value")
    zone = serializers.CharField(required=False, allow_null=True, help_text="Geographic zone (optional)")

class PredictionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(help_text="Prediction type (pollution, rain, etc.)")
    value = serializers.FloatField(help_text="Predicted value")
    date = serializers.DateTimeField(help_text="Prediction date/time")
    zone = serializers.CharField(allow_null=True, help_text="Geographic zone")
    created_at = serializers.DateTimeField(read_only=True)

class PredictionRequestSerializer(serializers.Serializer):
    type = serializers.CharField(help_text="Prediction type")
    value = serializers.FloatField(help_text="Predicted value")
    date = serializers.DateTimeField(help_text="Prediction date/time")
    zone = serializers.CharField(required=False, allow_null=True, help_text="Geographic zone (optional)")

class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=8, required=False)
    role = serializers.ChoiceField(choices=[('public', 'Public'), ('user', 'User'), ('admin', 'Admin')], required=False)

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    details = serializers.JSONField(required=False)

# ===== VIEWS =====

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        description='Create a new user account with username, email, and password',
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=CustomUserSerializer,
                description='User created successfully'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Validation error or username already exists',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        value={'error': 'Validation failed', 'details': {'username': ['This field is required.']}}
                    ),
                    OpenApiExample(
                        'Username Exists',
                        value={'error': 'Username already exists'}
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                'User Registration',
                summary='Regular user registration',
                request_only=True,
                value={
                    'username': 'johndoe',
                    'email': 'john@example.com',
                    'password': 'securepassword123',
                    'role': 'user'
                }
            ),
            OpenApiExample(
                'Admin Registration',
                summary='Admin user registration',
                request_only=True,
                value={
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'password': 'adminpassword123',
                    'role': 'admin'
                }
            ),
        ]
    )
)
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

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='User login',
        description='Authenticate user and receive JWT tokens',
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description='Login successful'
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Invalid credentials'
            )
        },
        examples=[
            OpenApiExample(
                'Login Example',
                request_only=True,
                value={
                    'username': 'johndoe',
                    'password': 'securepassword123'
                }
            )
        ]
    )
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

@extend_schema_view(
    get=extend_schema(
        tags=['Alerts'],
        summary='Get active alerts',
        description='Retrieve all currently active alerts',
        responses={
            200: OpenApiResponse(
                response=AlertSerializer(many=True),
                description='Active alerts retrieved successfully'
            )
        }
    )
)
class AlertListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = get_active_alerts()
        return Response(alerts)

@extend_schema_view(
    get=extend_schema(
        tags=['Alerts'],
        summary='Get alert history',
        description='Retrieve non-active alerts (acknowledged, resolved, archived)',
        responses={
            200: OpenApiResponse(
                response=AlertSerializer(many=True),
                description='Alert history retrieved successfully'
            )
        }
    )
)
class AlertHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = get_alert_history()
        return Response(alerts)

@extend_schema_view(
    put=extend_schema(
        tags=['Alerts'],
        summary='Acknowledge an alert',
        description='Mark an alert as acknowledged',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Alert ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=AlertSerializer,
                description='Alert acknowledged successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Alert not found'
            )
        }
    )
)
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

@extend_schema_view(
    put=extend_schema(
        tags=['Alerts'],
        summary='Resolve an alert',
        description='Mark an alert as resolved',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Alert ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=AlertSerializer,
                description='Alert resolved successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Alert not found'
            )
        }
    )
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

@extend_schema_view(
    get=extend_schema(
        tags=['Users'],
        summary='Get user details',
        description='Retrieve user information by ID (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='User ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer,
                description='User details retrieved successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='User not found'
            )
        }
    ),
    put=extend_schema(
        tags=['Users'],
        summary='Update user',
        description='Update user information (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='User ID'
            )
        ],
        request=UserUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer,
                description='User updated successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='User not found'
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Failed to update user'
            )
        }
    )
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

@extend_schema_view(
    delete=extend_schema(
        tags=['Users'],
        summary='Delete user',
        description='Delete a user account (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='User ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='DeleteResponse',
                    fields={'message': serializers.CharField()}
                ),
                description='User deleted successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='User not found'
            )
        }
    )
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

@extend_schema_view(
    get=extend_schema(
        tags=['Alert Thresholds'],
        summary='Get all alert thresholds',
        description='Retrieve all configured alert thresholds (admin only)',
        responses={
            200: OpenApiResponse(
                response=AlertThresholdSerializer(many=True),
                description='Thresholds retrieved successfully'
            )
        }
    ),
    post=extend_schema(
        tags=['Alert Thresholds'],
        summary='Create alert threshold',
        description='Create a new alert threshold (admin only)',
        request=AlertThresholdRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=AlertThresholdSerializer,
                description='Threshold created successfully'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Invalid request data'
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Admin access required'
            )
        },
        examples=[
            OpenApiExample(
                'Rain Threshold',
                request_only=True,
                value={
                    'type': 'rain',
                    'value': 50.0,
                    'zone': 'paris'
                }
            ),
            OpenApiExample(
                'Global Temperature Threshold',
                request_only=True,
                value={
                    'type': 'temperature',
                    'value': 35.0,
                    'zone': None
                }
            )
        ]
    )
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

@extend_schema_view(
    put=extend_schema(
        tags=['Alert Thresholds'],
        summary='Update alert threshold',
        description='Update an existing alert threshold (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Threshold ID'
            )
        ],
        request=AlertThresholdRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=AlertThresholdSerializer,
                description='Threshold updated successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Threshold not found'
            )
        }
    ),
    delete=extend_schema(
        tags=['Alert Thresholds'],
        summary='Delete alert threshold',
        description='Delete an alert threshold (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Threshold ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='ThresholdDeleteResponse',
                    fields={'message': serializers.CharField()}
                ),
                description='Threshold deleted successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Threshold not found'
            )
        }
    )
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

@extend_schema_view(
    get=extend_schema(
        tags=['Predictions'],
        summary='Get all predictions',
        description='Retrieve all weather/environmental predictions (admin only)',
        responses={
            200: OpenApiResponse(
                response=PredictionSerializer(many=True),
                description='Predictions retrieved successfully'
            )
        }
    ),
    post=extend_schema(
        tags=['Predictions'],
        summary='Create prediction',
        description='Create a new prediction (admin only)',
        request=PredictionRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=PredictionSerializer,
                description='Prediction created successfully'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Invalid request data'
            )
        },
        examples=[
            OpenApiExample(
                'Pollution Prediction',
                request_only=True,
                value={
                    'type': 'pollution',
                    'value': 75.5,
                    'date': '2025-07-15T10:00:00Z',
                    'zone': 'lyon'
                }
            ),
            OpenApiExample(
                'Rain Prediction',
                request_only=True,
                value={
                    'type': 'rain',
                    'value': 12.3,
                    'date': '2025-07-16T14:00:00Z',
                    'zone': 'paris'
                }
            )
        ]
    )
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

@extend_schema_view(
    put=extend_schema(
        tags=['Predictions'],
        summary='Update prediction',
        description='Update an existing prediction (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Prediction ID'
            )
        ],
        request=PredictionRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=PredictionSerializer,
                description='Prediction updated successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Prediction not found'
            )
        }
    ),
    delete=extend_schema(
        tags=['Predictions'],
        summary='Delete prediction',
        description='Delete a prediction (admin only)',
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Prediction ID'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='PredictionDeleteResponse',
                    fields={'message': serializers.CharField()}
                ),
                description='Prediction deleted successfully'
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Prediction not found'
            )
        }
    )
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

@extend_schema_view(
    post=extend_schema(
        tags=['Predictions'],
        summary='Analyze predictions',
        description='Analyze all predictions against thresholds and create alerts if values exceed thresholds (admin only)',
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='AnalysisResponse',
                    fields={'status': serializers.CharField()}
                ),
                description='Analysis completed successfully'
            )
        }
    )
)
class PredictionAnalyzeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        result = analyze_predictions()
        return Response({'status': result})