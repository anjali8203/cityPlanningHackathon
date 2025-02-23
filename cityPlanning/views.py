import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import ProjectForm, MessageForm
from allauth.account.views import SignupView
from django.contrib.auth import authenticate, login
from allauth.account.views import LoginView
from .models import UserProfile, Project
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import logout, get_backends
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

logger = logging.getLogger(__name__)


class CustomSignUpView(SignupView):
    def form_valid(self, form):
        # Save the new user
        user = form.save(self.request)

        # Manually set the backend to avoid multiple backend issues
        backend = get_backends()[0]  # Assuming the first backend is the correct one
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        # Log the user in automatically
        login(self.request, user, backend=user.backend)

        # Redirect to the profile creation page
        return redirect("create_user_profile")


@login_required
def create_user_profile(request):
    if request.method == "POST":
        real_name = request.POST.get("real_name")
        interests = request.POST.get("interests")
        description = request.POST.get("description")

            # Validation: Ensure all required fields are filled
        if not real_name:
            return render(
                request,
                "create_user_profile.html",
                {
                    "user": request.user,
                    "error": "Name is required.",
                },
            )

        # so we can use this later instead of the "username" which is just the email
        request.user.first_name = real_name
        request.user.save()

        # Create the user profile instance and save to the database
        user_profile = UserProfile.objects.create(
            user=request.user,
            real_name=real_name,
            email=request.user.email,
            date_joined=timezone.now(),
            interests=interests,
            description=description,
        )
        user_profile.save()

        return redirect(
            "user_dashboard"
        )  # Redirect to user dashboard after profile creation

    return render(request, "create_user_profile.html", {"user": request.user})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

@login_required
def user_dashboard(request):
    return render(request, "user_dashboard.html", {"is_pma": False})


@login_required
def user_dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.real_name.strip():  # Check if `real_name` is blank
            return redirect('create_user_profile')
    except UserProfile.DoesNotExist:
        return redirect('create_user_profile')
    # Query projects where the current user is the owner
    owned_projects = Project.objects.filter(owner=request.user)

    # prob also need to show projects where the user is a member
    member_projects = Project.objects.filter(members=request.user).distinct()

    # Prepare the context with both sets of projects
    context = {
        'owned_projects': owned_projects,
        'member_projects': member_projects,
        'real_name': user_profile.real_name, 
    }

    return render(request, "user_dashboard.html", context)


@login_required
def login_redirect(request):
    is_user = request.POST.get("user_checkbox", False)


# Custom Login View to handle both checkboxes: PMA and User
class CustomLoginView(LoginView):
    def form_valid(self, form):
        # Log in the user
        login(self.request, form.user)

        # Check if the user has a profile
        try:
            user_profile = UserProfile.objects.get(user=form.user)
        except UserProfile.DoesNotExist:
            # Redirect to profile creation if the profile does not exist
            return redirect('create_user_profile')

        # If 'next' parameter exists, respect it
        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        
        return redirect("user_dashboard")

@login_required
def view_profile(request):
    try:
        # Retrieve the user's profile
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If profile does not exist, redirect to profile creation
        return redirect("create_user_profile")

    return render(request, "view_profile.html", {"profile": user_profile})

@login_required
def your_projects(request):
    """
    View to display projects that the user owns or authored.
    """
    # Fetch projects owned by the user
    projects = Project.objects.filter(owner=request.user)
    # user_votes = Vote.objects.filter(user=request.user)
    # vote_dict = {vote.project.id: vote.vote_type for vote in user_votes}

    # # apparently this 'user_vote' is a temporary field
    # for project in projects:
    #     project.user_vote = vote_dict.get(project.id, None)

    return render(request, "your_projects.html", {"projects": projects})

def landing_page(request):
    # if request.user.is_authenticated:  # Check if the user is logged in
    #     return redirect("user_dashboard")  # Redirect to the user dashboard
    return render(request, "landing_page.html")

@csrf_exempt
@login_required
def update_points(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        city = data.get('city')
        points = data.get('points')

        # Update the user's points for the city (example logic)
        user_profile = request.user.profile
        user_profile.points[city] = user_profile.points.get(city, 0) + points
        user_profile.save()

        return JsonResponse({'success': True, 'total_points': user_profile.points[city]})
    return JsonResponse({'success': False})

def city_landmarks(request, city_name):
    landmarks_dict = {
        "charlottesville": [
            {"name": "The Rotunda", "description": "A historic building at UVA.", "points": 5},
            {"name": "Bodo's Bagels", "description": "A popular bagel shop in Charlottesville.", "points": 3},
            {"name": "Downtown Mall", "description": "A vibrant pedestrian mall.", "points": 4},
        ],
        "madrid": [
            {"name": "Royal Palace of Madrid", "description": "The official residence of the Spanish royal family.", "points": 7},
            {"name": "Plaza Mayor", "description": "A major public square in the heart of Madrid.", "points": 6},
            {"name": "Retiro Park", "description": "A large and beautiful park in Madrid.", "points": 5},
            {"name": "Prado Museum", "description": "One of the world's premier art museums.", "points": 8},
        ],
    }

    landmarks = landmarks_dict.get(city_name.lower(), [])

    local_businesses = [
        {
            "name": "Bodo's Bagels",
            "location": "Charlottesville",
            "city": "charlottesville",
            "points_required": 20,
            "reward": "$5 off your order",
            "website": "https://www.bodosbagels.com/",
        },
        {
            "name": "Mudhouse Coffee",
            "location": "Charlottesville",
            "city": "charlottesville",
            "points_required": 30,
            "reward": "Free medium coffee",
            "website": "https://mudhouse.com/?srsltid=AfmBOoohuZvPm9fhHaV4IvqHm1IaXaMQw3-ZEGHAdUL9vY-7Nia4K2M3",
        },
        {
            "name": "Royal Palace Cafe",
            "location": "Madrid",
            "city": "madrid",
            "points_required": 25,
            "reward": "Free dessert with any meal",
            "website": "https://cafedeoriente.es/en/",
        },
        {
            "name": "Retiro Park Cafe",
            "location": "Madrid",
            "city": "madrid",
            "points_required": 15,
            "reward": "Free coffee with any pastry",
            "website": "https://www.esmadrid.com/en/tourist-information/parque-del-retiro",
        },
    ]

    # Filter businesses by the selected city
    filtered_businesses = [business for business in local_businesses if business["city"].lower() == city_name.lower()]

    context = {
        "city_name": city_name,
        "landmarks": landmarks,
        "local_businesses": filtered_businesses,
    }
    return render(request, "landmarks.html", context)

def logout_view(request):
    logout(request)  # This logs the user out
    # Redirect to home page or render a custom template
    return render(request, 'account/sign_out.html')

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.owner = request.user  # Set the owner to the current user
            new_project.city = form.cleaned_data['city']  # Save the selected city
            new_project.save()
            form.save_m2m()  # Save many-to-many relationships if applicable
            return redirect('user_dashboard')  # Redirect to dashboard or project detail
        else:
            return render(request, 'create_project.html', {'form': form})
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_details.html', {'project': project})

@login_required
def post_project_message(request, project_id):
    # if is_pma_administrator(request.user):
    #     messages.error(request, "PMA Administrators cannot post messages.")
    #     return redirect('project_detail', project_id=project_id)
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.author = request.user
            new_message.project = project
            new_message.save()
            messages.success(request, "Message posted successfully.")
            return redirect('project_detail', project_id=project_id)
    else:
        form = MessageForm()
    return render(request, 'post_message.html', {'form': form, 'project': project})


# def project_list(request):
#     projects = Project.objects.all()
#     return render(request, 'projects_list.html', {'projects': projects})

# @require_POST
# def vote(request):
#     try:
#         data = json.loads(request.body)
#         project_id = data.get("project_id")
#         vote_type = data.get("vote_type")
#         project = get_object_or_404(Project, id=project_id)


#         if vote_type == 'up' or vote_type == 'clear_down_up':
#             Vote.objects.update_or_create(**{"user": request.user, "project": project}, defaults={"vote_type": 1})
#         elif vote_type == 'down' or vote_type == 'clear_up_down':
#             Vote.objects.update_or_create(**{"user": request.user, "project": project}, defaults={"vote_type": -1})
#         else:
#             Vote.objects.update_or_create(**{"user": request.user, "project": project}, defaults={"vote_type": 0})

#         # have to redo these conditions since one button can be pressed while the other is still 'active'
#         if vote_type == 'up' or vote_type == 'clear_down':
#             project.votes += 1  
#         elif vote_type == 'down' or vote_type == 'clear_up':
#             project.votes -= 1
#         elif vote_type == 'clear_down_up':
#             project.votes += 2
#         elif vote_type == 'clear_up_down':
#             project.votes -= 2
#         project.save()  


#         return JsonResponse({'success': True, 'votes': project.votes}) 
#     except Exception as e:
#         return JsonResponse({'success': False}) 

@login_required
def delete_project(request, project_id): 
    # Fetch the project object
    project = get_object_or_404(Project, id=project_id)
        # Delete the project
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect('user_dashboard')

    # # Render a confirmation page before deletion
    # return render(request, "deleteProjectConfirm.html", {"project": project})

# @login_required
# def request_to_join(request, project_id):
#     # if is_pma_administrator(request.user):
#     #     messages.error(request, "PMA Administrators cannot join projects.")
#     #     return redirect('explore_projects')
    
#     project = get_object_or_404(Project, id=project_id)
    
#     # Check if the user is already a member or has already requested
#     if project.members.filter(id=request.user.id).exists():
#         messages.warning(request, "You are already a member of this project.")
#     elif JoinRequest.objects.filter(project=project, user=request.user).exists():
#         messages.warning(request, "You have already requested to join this project.")
#     else:
#         # Create a join request
#         JoinRequest.objects.create(project=project, user=request.user)
#         messages.success(request, "Your request to join has been sent.")
    
#     return redirect('explore_projects')

@login_required
def leave_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure the user is a member
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, "You are not a member of this project.")
    else:
        project.members.remove(request.user)
        messages.success(request, "You have left the project.")

    return redirect('user_dashboard')  # Redirect to the user's dashboard or profile