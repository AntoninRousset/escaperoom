import subprocess
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from tempfile import NamedTemporaryFile

DEFAULT_FRONTEND_FOLDER = 'frontend'


class Command(BaseCommand):

    help = 'Test frontends'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label', nargs='?',
            help='App label of an application to build frontend for.',
        )
        parser.add_argument(
            '--frontend-folder', default=DEFAULT_FRONTEND_FOLDER,
            help='Name of the frontend folder to look for (default: frontend)',
        )

    def _test(self, app_config, frontend_path, **options):
        app_name = app_config.name
        self.stdout.write(f'Testing frontend for {app_name}')
        try:
            subprocess.run(
                ['npm', 'run', '--prefix', str(frontend_path), 'test', '--',
                 '--passWithNoTests'],
                check=True, capture_output=False
            )
        except subprocess.CalledProcessError:
            raise CommandError(
                f'Test failed for {app_name}'
            )

    def handle(self, *args, **options):
        apps_configs = set()
        if options['app_label']:
            try:
                apps_configs.add(apps.get_app_config(options['app_label']))
            except LookupError as err:
                raise CommandError(str(err))
        else:
            apps_configs.update(apps.get_app_configs())

        frontends_paths = dict()
        for app_config in apps_configs:
            frontend_path = Path(app_config.path) / options['frontend_folder']
            if frontend_path.exists():
                frontends_paths[app_config] = frontend_path
            elif options['app_label']:
                raise CommandError(
                    f'Application {app_config.name} has no frontend'
                )

        for app_config, frontend_path in frontends_paths.items():
            self._test(app_config, frontend_path, **options)
