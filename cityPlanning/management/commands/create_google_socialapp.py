from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os

class Command(BaseCommand):
    help = "Create or update the Google SocialApp"

    def handle(self, *args, **kwargs):
        site_domain = "https://sky-tracker-99371ce36fbe.herokuapp.com/"  # Heroku app domain
        site, _ = Site.objects.get_or_create(domain=site_domain, defaults={"name": "Heroku App"})

        google_app, created = SocialApp.objects.get_or_create(
            provider="google",
            defaults={
                "name": "Google Login",
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            },
        )
        if not created:
            google_app.sites.clear()
            google_app.sites.add(site)
            self.stdout.write("Google SocialApp updated successfully!")
        else:
            google_app.sites.add(site)
            self.stdout.write("Google SocialApp created successfully!")
