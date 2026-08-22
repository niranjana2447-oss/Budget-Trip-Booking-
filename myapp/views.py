from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import Count
from .models import Trip, Booking



# -----------------------
# HOME
# -----------------------
def home(request):
    return render(request, "home.html")


# -----------------------
# REGISTER
# -----------------------
def register(request):
    print("REGISTER VIEW HIT")
    print(request.POST)
    if request.method == "POST":
        print("POST DATA:",request.POST)
        fullname = request.POST.get("Fullname")
        email = request.POST.get("Email")
        password = request.POST.get("Password")
        confirm_password = request.POST.get("Confirm_password")

        # basic validation
        if not fullname:
            messages.error(request, "Full name is required")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

    
        username = fullname.replace(" ", "_")
        print("Username:",username)
        print("User Exists:",User.objects.filter(username=username).exists())

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print("User Created Successfully")
        print(user.username)


        messages.success(request, "Registered successfully")
        return redirect("login")

    return render(request, "register.html")
# -----------------------
# LOGIN
# -----------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")
            else:
                return redirect("customer_dashboard")

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


# -----------------------
# LOGOUT
# -----------------------
def logout_view(request):
    logout(request)
    return redirect("login")



def landing_page(request):
    trips = Trip.objects.all()[:6]  # featured 6 trips

    return render(request, "customer/landing.html", {
        "trips": trips
    })


# -----------------------
# CUSTOMER DASHBOARD
# -----------------------
@login_required(login_url="login")
def customer_dashboard(request):
    trips = Trip.objects.all()

    search = request.GET.get("search")
    budget = request.GET.get("budget")

    if search:
        trips = trips.filter(place_name__icontains=search)

    if budget:
        trips = trips.filter(price__lte=budget)

    return render(request, "customer/dashboard.html", {
        "trips": trips
    })

# -----------------------
# TRIP DETAILS
# -----------------------
@login_required(login_url="login")
def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id)
    return render(request, "customer/trip_details.html", {"trip": trip})


@login_required(login_url="login")
def book_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if not trip.is_active:
        messages.error(request, "This trip is not available!")
        return redirect("customer_dashboard")



    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        persons = int(request.POST.get("persons"))
        travel_date = request.POST.get("travel_date")

        total_amount = trip.price * persons

        booking = Booking.objects.create(
            user=request.user,
            trip=trip,
            name=name,
            email=email,
            phone=phone,
            persons=persons,
            travel_date=travel_date,
            total_amount=total_amount,
            payment_status="Pending"
        )
        return redirect("payment_page", booking_id=booking.id)
    return render(request, "customer/booking.html", {"trip": trip})


@login_required(login_url="login")
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.payment_status = "Paid"
        booking.save()

        return redirect("booking_success")

    return render(request, "customer/payment.html", {
        "booking": booking
    })

@login_required(login_url="login")
def booking_success(request):
    return render(request, "customer/booking_success.html")

@login_required(login_url="login")
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)

    return render(request, "customer/my_bookings.html", {
        "bookings": bookings
    })

  


# -----------------------
# ADMIN DASHBOARD
# -----------------------
@login_required(login_url="login")
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    total_trips = Trip.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(payment_status="Paid").aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    pending_bookings = Booking.objects.filter(payment_status="Pending").count()

    paid_bookings = Booking.objects.filter(payment_status="Paid").count()
    cancelled_bookings = Booking.objects.filter(payment_status="Cancelled").count()
    
    
    recent_bookings = Booking.objects.order_by("-id")[:5]

    top_trips = (
    Booking.objects
    .values("trip__place_name")
    .annotate(total=Count("id"))
    .order_by("-total")[:5]
    )


    return render(request, "admin/dashboard.html", {
    "total_trips": total_trips,
    "total_bookings": total_bookings,
    "total_revenue": total_revenue,
    "pending_bookings": pending_bookings,
    "paid_bookings": paid_bookings,
    "cancelled_bookings": cancelled_bookings,
    "recent_bookings": recent_bookings,
    "top_trips": top_trips,
    
})


@login_required(login_url="login")
def manage_trips(request):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    trips = Trip.objects.all()

    return render(request, "admin/manage_trips.html", {
        "trips": trips
    })


@login_required(login_url="login")
def add_trip(request):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    if request.method == "POST":
        Trip.objects.create(
            place_name=request.POST.get("place_name"),
            state_or_country=request.POST.get("state_or_country"),
            price=request.POST.get("price"),
            duration=request.POST.get("duration"),
            best_time=request.POST.get("best_time"),
            places_covered=request.POST.get("places_covered"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
        )

        return redirect("manage_trips")

    return render(request, "admin/add_trip.html")

    

@login_required(login_url="login")
def edit_trip(request, id):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    trip = get_object_or_404(Trip, id=id)

    if request.method == "POST":
        trip.place_name = request.POST.get("place_name")
        trip.state_or_country = request.POST.get("state_or_country")
        trip.price = request.POST.get("price")
        trip.duration = request.POST.get("duration")
        trip.best_time = request.POST.get("best_time")
        trip.places_covered = request.POST.get("places_covered")
        trip.description = request.POST.get("description")

        trip.is_active = "is_active" in request.POST


        if request.FILES.get("image"):
            trip.image = request.FILES["image"]

        trip.save()
        return redirect("manage_trips")

    return render(request, "admin/edit_trip.html", {
        "trip": trip
    })


@login_required(login_url="login")
def delete_trip(request, id):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    trip = get_object_or_404(Trip, id=id)
    trip.delete()

    return redirect("manage_trips")


@login_required(login_url="login")
def admin_bookings(request):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    bookings = Booking.objects.select_related("trip", "user").all().order_by("-id")

    return render(request, "admin/bookings.html", {"bookings": bookings})


@login_required(login_url="login")
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("trip").order_by("-id")

    print("CURRENT USER:", request.user)
    print("BOOKINGS FOUND:", bookings)

    return render(request, "customer/my_bookings.html", {
        "bookings": bookings
    })

@login_required(login_url="login")
def update_status(request, id, status):
    if not request.user.is_superuser:
        return redirect("customer_dashboard")

    booking = get_object_or_404(Booking, id=id)
    booking.payment_status = status
    booking.save()

    return redirect("admin_bookings")


@login_required(login_url="login")
def cancel_booking(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)

    booking.payment_status = "Cancelled"
    booking.save()

    return redirect("my_bookings")




