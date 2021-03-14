from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = 'Build frontend'

    def add_arguments(self, parser):
        parser.add_argument('--watch', action='store_true',
                            help='Watch frontend for change')

    def handle(self, *app_labels, **options):
        import subprocess

        try:
            self.stdout.write('Installing requirements')
            subprocess.run(
                ['npm', 'install'], check=True, capture_output=False
            )

            command = ['npx', 'webpack']
            if options['watch']:
                command.append('--watch')

            self.stdout.write('Building frontend')
            subprocess.run(
                command, check=True, capture_output=False
            )
        except subprocess.CalledProcessError as e:
            raise CommandError('Could not generate code:', repr(e))
