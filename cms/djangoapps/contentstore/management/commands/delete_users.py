"""
Command to delete users in bulk
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cms.djangoapps.course_creators.models import CourseCreator
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    """
    Delete users in bulk, with option to exclude specifc users
    """
    help = 'Delete users in bulk, with option to exclude specifc users'

    def add_arguments(self, parser):
        parser.add_argument('--exclude', nargs='+', type=str, help="Add usernames of users to be excluded from deletion")
        parser.add_argument('--only', nargs='+', type=str, help="Add usernames of users to be deleted")

    def handle(self, *args, **options):
        def delete_users (users):
            if not users:
                print('=' * 30)
                print("No users to delete")
            else:
                print("Found {} users to delete.".format(len(users)))
                for user in users:
                    course_creator = CourseCreator.objects.filter(user_id=user.id).first()
                    print("Deleting user: {}".format(user))
                    if course_creator: course_creator.delete()
                    user.delete()

                print('=' * 30)
                print("Completed, Following users were deleted")
                deleted_users = [user.username for user in users]

                print(deleted_users)

        """
        Execute the command
        """
        users_to_exclude=['audit','discovery_worker','ecommerce_worker','edx','enterprise_worker','honor', 'login_service_user','retirement_service_worker', 'staff', 'verified']

        if options['exclude']:
            exclude_users=options['exclude']
            users_to_exclude = users_to_exclude + exclude_users
            print('=' * 30)
            print("Following users are being excluded")
            print(exclude_users)
            print('=' * 30)
            print("Deleting Users")
            all_users=User.objects.all().exclude(username__in=users_to_exclude)
            delete_users(all_users)

        elif options['only']:
            selected_users = options['only']
            filtered_users = User.objects.filter(username__in=selected_users)
            print('=' * 30)
            print("Deleting Users")
            delete_users(filtered_users)
