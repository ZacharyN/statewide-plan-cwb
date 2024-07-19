from django.shortcuts import render
import logging
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm, PasswordResetForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login
from .models import AppUser


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        logging.info(f'User {user.email} must reset password: {user.must_reset_password}')
        if user.must_reset_password:
            logging.info('Redirecting to password reset')
            # Set a session variable to allow access to the password reset page
            self.request.session['reset_password_user_id'] = user.id
            return redirect('password_reset')
        return super().form_valid(form)


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        user_id = self.request.session.get('reset_password_user_id')
        if not user_id:
            print("No user ID in session, redirecting to login.")
            return redirect('login')
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.request.session.get('reset_password_user_id')
        if user_id:
            user = AppUser.objects.get(id=user_id)
            kwargs['user'] = user
        print(f"Form kwargs: {kwargs}")
        return kwargs

    def form_valid(self, form):
        user_id = self.request.session.get('reset_password_user_id')
        if not user_id:
            print("No user ID in session during form validation, redirecting to login.")
            return redirect('login')

        user = AppUser.objects.get(id=user_id)
        form.save()  # This should save the new password

        # Debugging logs to verify password change
        print(f"Password for user {user.email} before saving: {user.password}")

        user.must_reset_password = False
        user.save()

        # Debugging logs to verify password change
        print(f"Password for user {user.email} after saving: {user.password}")

        # Log the user in
        login(self.request, user)

        # Clear the session variable
        del self.request.session['reset_password_user_id']

        print(f'Password reset complete for user {user.email}')
        return super().form_valid(form)


