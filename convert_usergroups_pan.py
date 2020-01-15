import argparse
import sys
import csv
from getpass import getpass

from pandevice.panorama import Panorama, DeviceGroup
from pandevice.policies import PreRulebase, SecurityRule
from pandevice.errors import PanDeviceError

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panorama', help='hostname or ip of panorama', required=True)
    parser.add_argument('--user', help='username for auth to panorama', required=True)
    parser.add_argument('--dg', help='device group of the pre-rulebase that contain user-group-based policies', required=True)
    parser.add_argument('--group_mapping', help='legacy to PAN LDAP group mappings csv file', required=True)
    args = parser.parse_args()

    try:
        panorama = Panorama(args.panorama, args.user, getpass())
    except PanDeviceError as e:
        print(e.message)

    print('Retrieving user-based security policy from device-group: "{}"...'.format(args.dg))

    try:
        DeviceGroup.refreshall(panorama)
        target_dg = panorama.find(args.dg, DeviceGroup)

        if target_dg is None:
            print('Device group "{}" not found on Panorama device. Aborting...'.format(args.dg))
            sys.exit()

        prb = PreRulebase()
        target_dg.add(prb)

        dg_pre_rules = SecurityRule.refreshall(prb)
    except PanDeviceError as e:
        print(e.message)

    with open(args.group_mapping, newline='') as csvfile:
        reader = csv.reader(csvfile)

        group_map_dict = {}
        for row in reader:
            group_map_dict[row[0]] = row[1]

    changed = None
    for rule in dg_pre_rules:
        if not 'any' in rule.source_user:
            print(rule.name)
            for k, v in group_map_dict.items():
                for user in rule.source_user:
                    if user == k:
                        print('{0} -> {1}'.format(user, v))
                        if not v in rule.source_user:
                            rule.source_user.append(v)
                        rule.source_user.remove(k)
                        changed = True

        if changed:
            try:
                rule.apply()
                changed = False
            except PanDeviceError as e:
                print(e.message)

if __name__ == "__main__":
    main()