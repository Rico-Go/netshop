from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.CartView.as_view()),
    url(r'^queryAll/$',views.CartListView.as_view()),
]