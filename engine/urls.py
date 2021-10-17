from engine import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'state', views.StateViewSet, basename='state')
router.register(r'statetransition', views.StateTransitionViewSet,
                basename='statetransition')

urlpatterns = router.urls
