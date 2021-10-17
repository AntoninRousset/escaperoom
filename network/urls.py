from network import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'node', views.NodeViewSet, basename='node')
router.register(r'module', views.ModuleViewSet, basename='module')

urlpatterns = router.urls
