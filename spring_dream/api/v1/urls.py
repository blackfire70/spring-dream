from rest_framework.routers import DefaultRouter
from api.v1.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = router.urls