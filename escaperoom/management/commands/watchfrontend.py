import subprocess
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from tempfile import NamedTemporaryFile

DEFAULT_FRONTEND_FOLDER = 'frontend'
DEFAULT_CLIENT_COMMAND = 'generate-client'
DEFAULT_CLIENT_NAME = 'client'


class Command(BaseCommand):

    help = 'Watch frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            help='App label of an application to watch frontend for.',
        )
        parser.add_argument(
            '--no-install', dest='install', action='store_false',
            help='Do not install requirements.',
        )
        parser.add_argument(
            '--no-client', dest='client', action='store_false',
            help='Generate API client.',
        )
        parser.add_argument(
            '--mode', default='development',
            help='Building mode (default: development).',
        )
        parser.add_argument(
            '--frontend-folder', default=DEFAULT_FRONTEND_FOLDER,
            help='Name of the frontend folder to look for (default: frontend)',
        )
        parser.add_argument(
            '--client-command', default=DEFAULT_CLIENT_COMMAND,
            help=(
                'npm command to run in order to generate client'
                ' (default: generate-client)'
            ),
        )
        parser.add_argument(
            '--client-name', default=DEFAULT_CLIENT_NAME,
            help='Output name of the client (default: client)'
        )

    def _install_requirements(self, app_config, frontend_path, **options):
        app_name = app_config.name
        self.stdout.write(f'Installing requirements for {app_name}')
        try:
            subprocess.run(
                ['npm', 'install', '--prefix', str(frontend_path)],
                check=True, capture_output=False
            )
        except subprocess.CalledProcessError:
            raise CommandError(
                f'Could not install requirements for {app_name}'
            )

    def _generate_client(self, app_config, frontend_path, **options):
        app_name = app_config.name
        self.stdout.write(f'Building client for {app_name}')
        with NamedTemporaryFile(mode='w') as schema_file:
            call_command('spectacular', stdout=schema_file)
            client_path = frontend_path / options['client_name']
            try:
                subprocess.run(
                    ['npm', 'run', '--prefix', str(frontend_path),
                     options['client_command'], '--', '-i',
                     schema_file.name, '-o', str(client_path)],
                    check=True, capture_output=False
                )
                subprocess.run(
                    ['npm', 'install', '--prefix', str(client_path)],
                    check=True, capture_output=False
                )
            except subprocess.CalledProcessError:
                raise CommandError(
                    f'Could not generate client for {app_name}'
                )
            package_path = client_path.relative_to(settings.BASE_DIR)
            try:
                subprocess.run(
                    ['npm', 'install', '--prefix', str(frontend_path),
                     f'./{package_path}'], check=True, capture_output=False
                )
            except subprocess.CalledProcessError:
                raise CommandError(
                    f'Could not install generated client for {app_name}'
                )

    def _watch_frontend(self, app_config, frontend_path, **options):
        app_name = app_config.name
        self.stdout.write(f'Packing frontend for {app_name}')
        try:
            subprocess.run(
                ['npm', 'run', '--prefix', str(frontend_path), 'dev', '--',
                 '--mode', options['mode']], check=True, capture_output=False
            )
        except subprocess.CalledProcessError:
            raise CommandError(f'Could not pack frontend for {app_name}')

    def handle(self, *args, **options):
        try:
            app_config = apps.get_app_config(options['app_label'])
        except LookupError as err:
            raise CommandError(str(err))

        frontend_path = Path(app_config.path) / options['frontend_folder']
        if not frontend_path.exists():
            raise CommandError(
                f'Application {app_config.name} has no frontend'
            )

        if options['install']:
            self._install_requirements(
                app_config, frontend_path, **options
            )
        if options['client']:
            self._generate_client(app_config, frontend_path, **options)
        self._watch_frontend(app_config, frontend_path, **options)
