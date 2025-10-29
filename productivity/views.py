from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView
from .models import ProductivityEntry, User, Section
from .forms import ProductivityEntryForm
from django.urls import reverse_lazy
from django.db.models import Q

def role_check(user, roles):
    return user.is_authenticated and (user.role in roles or user.is_superuser)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

# -----------------------------------------
# Logout View
# -----------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard(request):
    user = request.user
    if role_check(user, ['admin','manager']):
        total_entries = ProductivityEntry.objects.count()
        entries_recent = ProductivityEntry.objects.all()[:10]
        sections = Section.objects.all()
    elif role_check(user, ['lead']):
        total_entries = ProductivityEntry.objects.filter(lead=user).count()
        entries_recent = ProductivityEntry.objects.filter(lead=user)[:10]
        sections = user.sections.all()
    else:
        # employee
        total_entries = ProductivityEntry.objects.filter(section__in=user.sections.all()).count()
        entries_recent = ProductivityEntry.objects.filter(section__in=user.sections.all())[:10]
        sections = user.sections.all()
    return render(request, 'productivity/dashboard.html', {
        'total_entries': total_entries,
        'entries_recent': entries_recent,
        'sections': sections,
    })

from django.utils import timezone

@method_decorator(login_required, name='dispatch')
class EntryListView(ListView):
    model = ProductivityEntry
    template_name = 'productivity/entry_list.html'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Role-based filtering
        if role_check(user, ['admin', 'manager']):
            pass  # full access
        elif role_check(user, ['lead']):
            qs = qs.filter(lead=user)
        else:  # employee
            qs = qs.filter(section__in=user.sections.all())

        # Filters
        section = self.request.GET.get('section')
        lead = self.request.GET.get('employee')
        date = self.request.GET.get('date')

        if section:
            if section.isdigit():
                qs = qs.filter(section_id=int(section))
            else:
                qs = qs.filter(section__name__icontains=section)

        if lead:
            if lead.isdigit():
                qs = qs.filter(lead_id=int(lead))
            else:
                qs = qs.filter(lead__username__icontains=lead)

        # ✅ Default to today's date if no date is selected
        if date:
            qs = qs.filter(date=date)
        else:
            qs = qs.filter(date=timezone.localdate())

        return qs.select_related('lead', 'section')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = Section.objects.all()
        context['leads'] = User.objects.filter(role='employee')
        # ✅ Pass today's date to the template for pre-filling the date filter input
        context['today'] = timezone.localdate()
        return context


@method_decorator(login_required, name='dispatch')
class EntryCreateView(CreateView):
    model = ProductivityEntry
    form_class = ProductivityEntryForm
    template_name = 'productivity/entry_form.html'
    success_url = reverse_lazy('entry_list')

    def dispatch(self, request, *args, **kwargs):
        if not role_check(request.user, ['lead','admin','manager']):
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        init = super().get_initial()
        if self.request.user.role == 'lead':
            init['lead'] = self.request.user
        return init

from django.http import JsonResponse
from django.shortcuts import redirect

@method_decorator(login_required, name='dispatch')
class EntryUpdateView(UpdateView):
    model = ProductivityEntry
    form_class = ProductivityEntryForm
    template_name = 'productivity/entry_form.html'
    success_url = reverse_lazy('entry_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Admin & Manager can edit anything
        if role_check(request.user, ['admin', 'manager']):
            return super().dispatch(request, *args, **kwargs)
        # Lead can edit only their own entries
        if role_check(request.user, ['lead']) and obj.lead == request.user:
            return super().dispatch(request, *args, **kwargs)
        return redirect('dashboard')

    def post(self, request, *args, **kwargs):
        """Handle inline POST updates, supports AJAX."""
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            # AJAX request → return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect(self.success_url)
        # If invalid, send errors in JSON (for inline display)
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import ProductivityEntry


@login_required
@require_POST
def update_entry_field(request, pk):
    """Inline AJAX field updater for ProductivityEntry."""
    try:
        entry = ProductivityEntry.objects.get(pk=pk)
    except ProductivityEntry.DoesNotExist:
        return JsonResponse({"success": False, "error": "Entry not found."}, status=404)

    user = request.user

    # ✅ Permission check
    if not (user.role in ['admin', 'manager'] or entry.lead == user):
        return JsonResponse({"success": False, "error": "Unauthorized."}, status=403)

    # ✅ Only allow updates for productivity numeric/text fields
    allowed_fields = [
        'bundle_opening', 'sorting', 'loading',
        'sticker', 'scanning', 'put_away',
        'picking', 'remarks'
    ]

    fields_to_save = {}

    for field in allowed_fields:
        if field in request.POST:
            raw_value = request.POST[field].strip()

            # Empty value handling
            if raw_value == '':
                value = '' if field == 'remarks' else 0
            else:
                # Convert numeric fields to int safely
                if field == 'remarks':
                    value = raw_value
                else:
                    try:
                        value = int(raw_value)
                        if value < 0:
                            return JsonResponse({
                                "success": False,
                                "error": f"Negative values are not allowed for '{field}'."
                            }, status=400)
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "error": f"Invalid value for '{field}'. Please enter a number."
                        }, status=400)

            # Track updated fields
            fields_to_save[field] = value

    if not fields_to_save:
        return JsonResponse({"success": False, "error": "No valid fields to update."}, status=400)

    # ✅ Apply updates
    for field, value in fields_to_save.items():
        setattr(entry, field, value)

    try:
        # ✅ Update only the changed fields (skips unique-together validation)
        entry.save(update_fields=list(fields_to_save.keys()))
        return JsonResponse({"success": True})
    except ValidationError as e:
        # Catch Django field-level validation errors (if any)
        return JsonResponse({"success": False, "error": e.messages[0]}, status=400)
    except Exception as e:
        # Catch unexpected errors
        return JsonResponse({"success": False, "error": str(e)}, status=400)
