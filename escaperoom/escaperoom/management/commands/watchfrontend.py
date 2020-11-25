from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):

    help = 'Build frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            help='App label to watch frontend for.'
        )
        parser.add_argument('--log', action='store_true',
                            help='Show building details')

    def handle(self, *app_labels, **options):
        import subprocess

        app_label = options['app_label']

        try:
            apps.get_app_config(app_label)
        except LookupError as err:
            raise CommandError(str(err))

        try:
            path = settings.BASE_DIR / app_label / 'frontend'
            self.stdout.write(f'Installing requirements for "{app_label}"')
            subprocess.run(
                ['yarn', '--cwd', path, 'install'],
                check=True, capture_output=not options['log']
            )

            self.stdout.write(f'Watching frontend for "{app_label}"')
            subprocess.run(
                ['yarn', '--cwd', path, 'watch'],
                check=True, capture_output=not options['log']
            )
        except subprocess.CalledProcessError as e:
            raise CommandError('Could not generate code:', repr(e))
