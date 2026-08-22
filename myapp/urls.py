from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('trip/<int:id>/', views.trip_details, name='trip_details'),
    path('book/<int:trip_id>/', views.book_trip, name='book_trip'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("manage-trips/", views.manage_trips, name="manage_trips"),
    path('add-trip/', views.add_trip, name='add_trip'),
    path("edit-trip/<int:id>/", views.edit_trip, name="edit_trip"),
    path("delete-trip/<int:id>/", views.delete_trip, name="delete_trip"),
    path("admin-bookings/", views.admin_bookings, name="admin_bookings"),
    path('update-status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('cancel-booking/<int:id>/', views.cancel_booking, name='cancel_booking'),


]

    
    