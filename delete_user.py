#!/usr/bin/env python2

import csv
import argparse

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

def delete_user(user):
    """
        Delete an IAM user with all access key and remove it from  groups.

        This function delete an IAM user with all its access keys and remove it
        from all groups attached to its.

        :param user: The username of the IAM user to remove
        :type user: str

        :Example:
        >>> delete_user("toto")
    """
    ocb = OCBase.OCBase()
    aks = ocb.eim.get_all_access_keys(user)
    for ak in aks['list_access_keys_response']['list_access_keys_result']['access_key_metadata']:
        ocb.eim.delete_access_key(ak['access_key_id'], user)
    groups = ocb.eim.get_groups_for_user(user)
    for group in groups['list_groups_for_user_response']['list_groups_for_user_result']['groups']:
        ocb.eim.remove_user_from_group(group['group_name'], user)
    ocb.eim.delete_user(user)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--csv-source", help="The source of users to destroy in CSV format", type=str)
    group.add_argument("--teardown", help="Remove all users inside the account", action="store_true")
    args = parser.parse_args()

    if args.teardown == True:
        ocb = OCBase.OCBase()
        users = ocb.eim.get_all_users()
        for user in users['list_users_response']['list_users_result']['users']:
            try:
                delete_user(user['user_name'])
                print "User {} deleted !".format(user['user_name'])
            except Exception as e:
                print "User {} deletion failed !".format(user['user_name'])
                print "Reason: {}".format(str(e))
    else:
        for elem in extract_users(args.csv_source):
            try:
                delete_user(elem)
                print "User {} deleted !".format(elem)
            except Exception as e:
                print "User {} deletion failed !".format(elem)
                print "Reason: {}".format(str(e))

