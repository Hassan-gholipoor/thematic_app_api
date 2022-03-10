from django.urls import path
from user import views


app_name = 'user'

urlpatterns = [
    path('create_user/', views.CreateUserView.as_view(), name='create_user'),
    path('create_author/', views.CreateAuthorView.as_view(), name='create_author'),
    path('token/', views.CreateTokenView.as_view(), name='token')
]