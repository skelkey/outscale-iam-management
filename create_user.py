#!/usr/bin/env python2

import csv
import smtplib
import argparse

from email.mime.text import MIMEText
from osc_cloud_builder import OCBase

def extract_users(file, delimiter=";"):
    """
        Open a csv file and return the content of the third column as list.

        This function open and read all the line of the CSV file and return the
        content of the third column as a list. The first line of the CSV file
        are ignored.

        :param file: The path for the file to read
        :type file: str
        :param delimiter: The delimiter used in the CSV file
        :type delimiter: str
        :return: A list of strings
        :rtype: list

        :Example:

        >>> extract_users("/tmp/listing.csv")
        ["toto", "tata", "tutu"]
    """
    with open(file) as csvfile:
        rows = csv.reader(csvfile, delimiter=delimiter)
        return [row[3] for row in rows][1:]

def create_user(username):
    """
        Create an IAM user with the username in paramater.

        This function creates an IAM user inside the cloud account with access
        key and return it inside a dictionnary.

        :param username: The username for the IAM user
        :type username: str
        :return: Information about the created user
        :rtype: dict

        :Example:

        >>> create_user("toto")
        {'username': 'toto', 'sk': '...secret...', 'ak': '...'}
    """
    ocb = OCBase.OCBase()
    user = ocb.eim.create_user(username)
    aksk = ocb.eim.create_access_key(username)

    return {'username': user.create_user_response.create_user_result.user_name,
            'ak': aksk.create_access_key_response.create_access_key_result.access_key_id,
            'sk': aksk.create_access_key_response.create_access_key_result.secret_access_key}

def associate_policy(group_name, username):
    """
        Associate an IAM user to a group policy.

        This function associate an IAM user to an existing group policy inside
        the cloud account.

        :param group_name: The group policy to associate with the user
        :type group_name: str
        :param username: The username of the IAM user to add in the group policy
        :type username: str
        :return: True if all works fine else False
        :rtype: bool

        :Example:

        >>> associate_policy("students", "toto")
        True
    """
    ocb = OCBase.OCBase()
    return ocb.eim.add_user_to_group(group_name=group_name, user_name=username)

def send_mail(gmail_user, gmail_password, user, ak, sk, region="eu-west-2"):
    """
         Send a mail to a user with information needed for cloud connection.

         This function use a gmail account to send a mail to the user containing
         the access key, the secret key and region for the user connection.

         :param gmail_user: The gmail user to use to send the mail
         :type gmail_user: str
         :param gmail_password: The password for the gmail account to use
         :type gmail_password: str
         :param user: The mail address to use for the recipient of credentials.
         :type user: str
         :param ak: The access key to send
         :type ak: str
         :param sk: The secret key to send
         :type sk: str
         :param region: Region to use for user connection (default: eu-west-2)
         :type region: str
         :return: A dictionnary with delivery information
         :rtype: dict

         :Example:
         >>> send_mail("toto@gmail.com", "...secret...", "test@example.net", "...", "...secret...")
         {'reason': 'true', 'result': True}
    """
    subject = "Your access key for Outscale cloud"
    body = """\
Hi,

Please find in this mail your access key for Outscale cloud.

Access key : {}
Secret key : {}
Region     : {}

This credentials are personal. Please keep it secret and don't provide it to another person !

Best regards,
Edouard Camoin
""".format(ak, sk, region)

    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = user
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, user, msg.as_string())
        server.close()
        return {'result':True,
                'reason':'true'}
    except Exception as e:
        return {'result':False,
                'reason':str(e)}

def delete_user(user):
    """
        Delete an IAM user with all access key and remove it from students group.

        This function delete an IAM user with all its access keys and remove it
        from the existing group `students`.

        :param user: The username of the IAM user to remove
        :type user: str

        :Example:
        >>> delete_user("toto")
    """
    ocb = OCBase.OCBase()
    aks = ocb.eim.get_all_access_keys(user)
    for ak in aks['list_access_keys_response']['list_access_keys_result']['access_key_metadata']:
        ocb.eim.delete_access_key(ak['access_key_id'], user)
    ocb.eim.remove_user_from_group("students", user)
    ocb.eim.delete_user(user)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A simple tool to create IAM user from CSV")
    parser.add_argument("--gmail-user", help="The GMAIL account to use", type=str, required=True)
    parser.add_argument("--gmail-password", help="The GMAIL password to use", type=str, required=True)
    parser.add_argument("--csv-source", help="The source of emails in CSV format", type=str, required=True)
    parser.add_argument("--iam-policy-group", help="The group policy to use", type=str, default="students")
    args = parser.parse_args()

    for elem in extract_users(args.csv_source):
        try:
            user = create_user(elem)
            print "User {} created !".format(user['username'])
            result = associate_policy(args.iam_policy_group, user['username'])
            if result == True:
                print "User {} added in policy {}".format(user['username'], args.iam_policy_group)
            result = send_mail(args.gmail_user, args.gmail_password, user['username'], user['ak'], user['sk'])
            if result['result'] == True:
                print "Email sent to {} !".format(user['username'])
            else:
                print result['reason']
                print "An error occured for user creation : {}".format(user['username'])
                delete_user(user['username'])
        except Exception as e:
            print "An error occured for user creation : {}".format(elem)
            print "Reason : {}".format(str(e))
            try:
                delete_user(elem)
                print "User {} deleted !".format(elem)
            except:
                print "User {} deletion failed !".format(elem)
