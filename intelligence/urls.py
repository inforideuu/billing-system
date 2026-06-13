from django.urls import path
from . import views

urlpatterns = [
    path('insights/', views.insights, name='smart_insights'),
    path('batches/', views.batches_list, name='batches_list'),
    path('batches/add/', views.add_batch, name='add_batch'),
    path('batches/delete/<int:batch_id>/', views.delete_batch, name='delete_batch'),
    path('settings/', views.edit_settings, name='intelligence_settings'),
    path('trigger-alerts/', views.trigger_notifications, name='trigger_alerts'),
    path('chat/sessions/', views.chat_sessions_list, name='chat_sessions_list'),
    path('chat/sessions/<int:session_id>/messages/', views.chat_session_messages, name='chat_session_messages'),
    path('chat/message/', views.post_chat_message, name='post_chat_message'),
    path('api/notifications/', views.api_get_notifications, name='api_get_notifications'),
]
