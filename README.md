# outscale-iam-management
Create and remove IAM user inside your account for Outscale Cloud provider

I wrote this tool to manage IAM user for my student in my class.

## create_user

The create_user.py script create IAM users from a CSV with 4 columns (first name, last name, student personal mail and student school mail). The user is affected to a group passed in parameter of the script ("students" by default), so the group policy must exist before the creation.

When the user is created, a mail is send to the student (using student school mail field) containing information needed using a gmail account. Username and password of the gmail account must be passed in parameter of the script

## delete_user

The delete_user.py script delete IAM users inside the account (removing user from all groups, deleting access keys) by using a CSV file with the same column than the create_user.py needed script. This script can also make a complete teardown of the users inside the account (use it carefully ;))

