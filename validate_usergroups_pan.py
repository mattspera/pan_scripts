import re
import argparse
import sys
from getpass import getpass

import xmltodict
from pandevice.firewall import Firewall
from pandevice.panorama import Panorama, DeviceGroup
from pandevice.policies import PreRulebase, SecurityRule
from pandevice.errors import PanDeviceError

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panorama', help='hostname or ip of panorama', required=True)
    parser.add_argument('--master_device', help='hostname or ip of firewall to retrieve group-mappings', required=True)
    parser.add_argument('--dg', help='device group of the pre-rulebase that contain user-group-based policies', required=True)
    args = parser.parse_args()

    try:
        panorama = Panorama(args.panorama, input('Panorama username: '), getpass('Panorama password: '))
    except PanDeviceError as e:
        print(e.message)

    cmd = 'show devices connected'
    try:
        res = panorama.op(cmd, xml=True)
    except PanDeviceError as e:
        print(e.message)
        sys.exit(1)

    devs_connected = xmltodict.parse(res)['response']['result']['devices']['entry']

    firewall = None

    for dev in devs_connected:
        if dev['hostname'] == args.master_device or dev['ip-address'] == args.master_device:
            firewall = Firewall(serial=dev['serial'])
            break

    if firewall is not None:
        try:
            panorama.add(firewall)
        except PanDeviceError as e:
            print(e.message)
    else:
        print('Master device (firewall) is not managed by Panorama. Attempting direct connection to firewall...')
        try:
            firewall = Firewall(args.master_device, input('Firewall username: '), getpass('Firewall password: '))
        except PanDeviceError as e:
            print(e.message)

    print('Retrieving user-group-mappings on master device: "{}"...'.format(args.master_device))

    cmd = 'show user group list'
    try:
        res = firewall.op(cmd, xml=True)
    except PanDeviceError as e:
        print(e.message)

    user_group_data = xmltodict.parse(res)['response']['result']
    user_group_list = re.findall(r'cn=.*?dc=com', user_group_data)

    print('Number of mapped user-groups found: {}\n'.format(len(user_group_list)))
    print('Currently mapped user-groups: ')
    for user_group in user_group_list: print('"{}"'.format(user_group))
    print('\n')

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

    print('Retrieving user-based security policy from device-group: "{}"...'.format(args.dg))

    user_based_rules = []
    for rule in dg_pre_rules:
        if not 'any' in rule.source_user:
            user_based_rules.append(rule)

    print('Number of user-based security rules found: {}\n'.format(len(user_based_rules)))

    for rule in user_based_rules:
        print('Validating user-based security rule: "{}"...'.format(rule.name))
        for user in rule.source_user:
            if not user in user_group_list:
                print('Invalid user-group: "{}"'.format(user))
        print('\n')

if __name__ == "__main__":
    main()