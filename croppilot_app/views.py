from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User

from .decorators import role_required

# ================= ML MODULES =================
from .ml_models.random_disease import random_disease_predict
from .ml_models.soil_ai import predict_soil_ai

# ================= MODELS =================
from .models import (
    Profile,
    Farmer,
    AgricultureOfficer,
    Crop,
    DiseaseReport,
    FarmerQuery,
    MarketPrice,
    Feedback,
    SoilRecommendation,
    FertilizerRecommendation
)

# =====================================================
# HOME
# =====================================================
def home(request):
    return render(request, 'home.html')


# =====================================================
# AUTHENTICATION
# =====================================================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('/adminpanel/dashboard/')

            role = user.profile.role
            if role == 'admin':
                return redirect('/adminpanel/dashboard/')
            elif role == 'officer':
                return redirect('/officer/dashboard/')
            else:
                return redirect('/farmer/dashboard/')

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


# =====================================================
# FARMER REGISTRATION
# =====================================================
def farmer_register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'farmer/register.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.profile.role = 'farmer'
        user.profile.save()

        Farmer.objects.create(
            user=user,
            phone=request.POST['phone'],
            region=request.POST['region']
        )

        return redirect('/login/')

    return render(request, 'farmer/register.html')


# =====================================================
# FARMER MODULE
# =====================================================
@role_required(allowed_roles=['farmer'])
def farmer_dashboard(request):
    return render(request, 'farmer/dashboard.html', {
        'prices': MarketPrice.objects.all()[:5],
        'reports': DiseaseReport.objects.filter(farmer__user=request.user)
    })


@role_required(allowed_roles=['farmer'])
def disease_detection(request):
    if request.method == "POST":
        fs = FileSystemStorage()
        filename = fs.save(request.FILES['image'].name, request.FILES['image'])

        predictions = random_disease_predict()

        DiseaseReport.objects.create(
            farmer=Farmer.objects.get(user=request.user),
            crop_name=request.POST['crop_name'],
            image=filename,
            detected_disease=predictions[0]['disease'],
            verified_by_officer=False
        )

        return render(request, 'farmer/disease_result.html', {
            'predictions': predictions
        })

    return render(request, 'farmer/disease_upload.html')


@role_required(allowed_roles=['farmer'])
def send_query(request):
    if request.method == "POST":
        FarmerQuery.objects.create(
            farmer=Farmer.objects.get(user=request.user),
            question=request.POST['question']
        )
        return redirect('/farmer/dashboard/')

    return render(request, 'farmer/send_query.html')


@role_required(allowed_roles=['farmer'])
def submit_feedback(request):
    if request.method == "POST":
        Feedback.objects.create(
            farmer=Farmer.objects.get(user=request.user),
            message=request.POST['message']
        )
        return redirect('/farmer/dashboard/')

    return render(request, 'farmer/feedback.html')


@role_required(allowed_roles=['farmer'])
def farmer_queries(request):
    return render(request, 'farmer/view_replies.html', {
        'queries': FarmerQuery.objects.filter(
            farmer=Farmer.objects.get(user=request.user)
        )
    })


@role_required(allowed_roles=['farmer'])
def farmer_crops(request):
    return render(request, 'farmer/view_crops.html', {
        'crops': Crop.objects.all()
    })


@role_required(allowed_roles=['farmer'])
def farmer_market_prices(request):
    return render(request, 'farmer/market_prices.html', {
        'prices': MarketPrice.objects.all()
    })


@role_required(allowed_roles=['farmer'])
def smart_soil_recommendation(request):
    soil = fertilizer = ai_soil = None

    if request.method == "POST":
        crop_id = request.POST['crop']
        weather = request.POST['weather']
        farmer = Farmer.objects.get(user=request.user)

        ai_soil = predict_soil_ai(farmer.region, weather)
        soil = SoilRecommendation.objects.filter(crop_id=crop_id).first()
        fertilizer = FertilizerRecommendation.objects.filter(crop_id=crop_id).first()

    return render(request, 'farmer/smart_soil.html', {
        'crops': Crop.objects.all(),
        'soil': soil,
        'fertilizer': fertilizer,
        'ai_soil': ai_soil
    })


# =====================================================
# OFFICER MODULE
# =====================================================
@role_required(allowed_roles=['officer'])
def officer_dashboard(request):
    return render(request, 'officer/dashboard.html', {
        'reports': DiseaseReport.objects.all(),
        'queries': FarmerQuery.objects.all(),
        'feedbacks': Feedback.objects.all()
    })


@role_required(allowed_roles=['officer'])
def officer_verify_disease(request, report_id):
    report = DiseaseReport.objects.get(id=report_id)

    if request.method == "POST":
        report.treatment = request.POST['treatment']
        report.verified_by_officer = True
        report.save()
        return redirect('/officer/dashboard/')

    return render(request, 'officer/verify_disease.html', {'report': report})


@role_required(allowed_roles=['officer'])
def reply_query(request, query_id):
    query = FarmerQuery.objects.get(id=query_id)

    if request.method == "POST":
        query.reply = request.POST['reply']
        query.replied = True
        query.save()
        return redirect('/officer/dashboard/')

    return render(request, 'officer/reply_query.html', {'query': query})


# =====================================================
# ADMIN MODULE
# =====================================================
@role_required(allowed_roles=['admin'])
def admin_dashboard(request):
    return render(request, 'adminpanel/dashboard.html', {
        'farmer_count': Farmer.objects.count(),
        'officer_count': AgricultureOfficer.objects.count(),
        'crop_count': Crop.objects.count(),
        'report_count': DiseaseReport.objects.count()
    })


@role_required(allowed_roles=['admin'])
def manage_farmers(request):
    return render(request, 'adminpanel/farmers.html', {
        'farmers': Farmer.objects.all()
    })


@role_required(allowed_roles=['admin'])
def manage_officers(request):
    return render(request, 'adminpanel/officers.html', {
        'officers': AgricultureOfficer.objects.all()
    })


@role_required(allowed_roles=['admin'])
def manage_crops(request):
    if request.method == "POST":
        Crop.objects.create(
            name=request.POST['name'],
            suitable_soil=request.POST['suitable_soil'],
            season=request.POST['season']
        )
        return redirect('/adminpanel/crops/')

    return render(request, 'adminpanel/crops.html', {
        'crops': Crop.objects.all()
    })


@role_required(allowed_roles=['admin'])
def manage_market_prices(request):
    if request.method == "POST":
        MarketPrice.objects.create(
            crop=Crop.objects.get(id=request.POST['crop']),
            price=request.POST['price'],
            date=request.POST['date']
        )
        return redirect('/adminpanel/market-prices/')

    return render(request, 'adminpanel/market_prices.html', {
        'prices': MarketPrice.objects.all(),
        'crops': Crop.objects.all()
    })


@role_required(allowed_roles=['admin'])
def add_officer(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        user.profile.role = 'officer'
        user.profile.save()

        AgricultureOfficer.objects.create(
            user=user,
            region=request.POST['region'],
            qualification=request.POST['qualification']
        )

        return redirect('/adminpanel/officers/')

    return render(request, 'adminpanel/add_officer.html')


@role_required(allowed_roles=['admin'])
def edit_officer(request, officer_id):
    officer = AgricultureOfficer.objects.get(id=officer_id)

    if request.method == "POST":
        officer.user.username = request.POST['username']
        officer.region = request.POST['region']
        officer.qualification = request.POST['qualification']

        if request.POST.get('password'):
            officer.user.set_password(request.POST['password'])

        officer.user.save()
        officer.save()
        return redirect('/adminpanel/officers/')

    return render(request, 'adminpanel/edit_officer.html', {'officer': officer})


@role_required(allowed_roles=['admin'])
def delete_officer(request, officer_id):
    officer = AgricultureOfficer.objects.get(id=officer_id)
    officer.user.delete()
    officer.delete()
    return redirect('/adminpanel/officers/')
