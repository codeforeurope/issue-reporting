from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'feedbacks', views.FeedbackViewSet, 'Feedback')