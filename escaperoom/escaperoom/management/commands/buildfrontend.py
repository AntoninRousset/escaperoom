from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):

    help = 'Build frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
            help='Specify the app label(s) to build frontend for.',
        )
        parser.add_argument('--log', action='store_true',
                            help='Show building details')

    def handle(self, *app_labels, **options):
        import os
        import subprocess
        import sys

        if not app_labels:
            app_labels = apps.app_configs.keys()

        app_labels = set(app_labels)
        has_bad_labels = False
        for app_label in app_labels:
            try:
                apps.get_app_config(app_label)
            except LookupError as err:
                self.stderr.write(str(err))
                has_bad_labels = True
        if has_bad_labels:
            sys.exit(2)

        try:
            for app_label in app_labels:
                path = settings.BASE_DIR / app_label / 'frontend'
                if os.path.isdir(path):
                    self.stdout.write(
                        f'Installing requirements for "{app_label}"'
                    )
                    subprocess.run(
                        ['yarn', '--cwd', path, 'install'],
                        check=True, capture_output=not options['log']
                    )

                    self.stdout.write(f'Building frontend for "{app_label}"')
                    subprocess.run(
                        ['yarn', '--cwd', path, 'build'],
                        check=True, capture_output=not options['log']
                    )
        except subprocess.CalledProcessError as e:
            raise CommandError('Could not generate code:', repr(e))
