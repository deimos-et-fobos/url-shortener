from django.urls import path
from .views import RegisterView, LogoutView, CustomTokenObtainPairView, CustomTokenRefreshView

app_name = "accounts.api"
urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),    
    path('logout/', LogoutView.as_view(), name='logout'),   
    path('token-refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),  
    path('register/', RegisterView.as_view(), name='register'), 
]