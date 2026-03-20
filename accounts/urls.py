from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("", include("accounts.public_urls")),
    path("internal/", include("accounts.internal_urls")),
]
