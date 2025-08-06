from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from config import settings

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # # Приложения
    # path('attendance/', include('attendance.urls', namespace='attendance')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)