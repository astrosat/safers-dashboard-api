import os

from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand, CommandError

from safers.core.models import SiteProfile


def load_fixture(app_config, fixture_name):
    fixture_path = os.path.join(app_config.path, "fixtures", fixture_name)
    management.call_command("loaddata", fixture_path)


class Command(BaseCommand):
    """
    Sets up initial configuration for safers-dashbaord-api.
    This includes loading fixtures and setting a unique site_code.
    """

    help = f"Setup initial configuration for {settings.PROJECT_NAME}."

    def add_arguments(self, parser):

        parser.add_argument(
            "--site_code",
            dest="site_code",
            help=
            "A unique code associated w/ this site to use when generating routing_keys (to distinguish it from other sites)."
        )

        parser.add_argument(
            "--skip-aois",
            dest="load_aois",
            action="store_false",
            help="Whether or not to skip the AOI fixtures.",
        )

        parser.add_argument(
            "--skip-cameras",
            dest="load_cameras",
            action="store_false",
            help="Whether or not to skip the Camera fixtures.",
        )

        parser.add_argument(
            "--skip-chatbot-report-categories",
            dest="load_chatbot_report_categories",
            action="store_false",
            help="Whether or not to skip the chatbot.ReportCategory fixtures.",
        )

        parser.add_argument(
            "--skip-countries",
            dest="load_countries",
            action="store_false",
            help="Whether or not to skip the Country fixtures.",
        )

        parser.add_argument(
            "--skip-data",
            dest="load_data",
            action="store_false",
            help="Whether or not to skip the DataType fixtures.",
        )

    def handle(self, *args, **options):

        try:

            site_code = options["site_code"]
            if site_code:
                current_site = get_current_site(None)
                if not current_site:
                    raise CommandError(
                        "Unable to assign site_code as there is no current site instance."
                    )
                current_site_profile, _ = SiteProfile.objects.get_or_create(site=current_site)
                current_site_profile.code = site_code
                current_site_profile.save()
                self.stdout.write("updated site_profile code")

            if options["load_aois"]:
                load_fixture(
                    apps.get_app_config("aois"),
                    "aois_fixture.json",
                )

            if options["load_cameras"]:
                load_fixture(
                    apps.get_app_config("cameras"),
                    "cameras_fixture.json",
                )

            if options["load_chatbot_report_categories"]:
                load_fixture(
                    apps.get_app_config("chatbot"),
                    "chatbot_report_categories_fixture.json",
                )

            if options["load_countries"]:
                load_fixture(
                    apps.get_app_config("core"),
                    "countries_fixture.json",
                )

            if options["load_data"]:
                load_fixture(
                    apps.get_app_config("data"),
                    "datatypes_fixture.json",
                )

        except Exception as e:
            raise CommandError(e)
