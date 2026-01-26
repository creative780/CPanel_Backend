from django.urls import path
from .views import LoginView, RegisterView, MeView, LogoutView, UsersListView, UserSuspendReactivateView, MatrixConfigView, chat_users_list, users_by_role


urlpatterns = [
    path('login', LoginView.as_view(), name='auth-login'),
    path('logout', LogoutView.as_view(), name='auth-logout'),
    path('register', RegisterView.as_view(), name='auth-register'),
    path('me', MeView.as_view(), name='auth-me'),
    path('matrix-config/', MatrixConfigView.as_view(), name='matrix-config'),
    path('users', UsersListView.as_view(), name='users-list'),
    path('users/<int:id>/suspend-reactivate/', UserSuspendReactivateView.as_view(), name='user-suspend-reactivate'),
    # Chat users endpoint (moved from chat app for Matrix integration)
    path('chat/users/', chat_users_list, name='chat-users-list'),
    path('users/by-role/', users_by_role, name='users-by-role'),
]

