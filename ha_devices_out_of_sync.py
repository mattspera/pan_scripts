import argparse
import sys
from getpass import getpass

import xmltodict
from pandevice.firewall import Firewall
from pandevice.panorama import Panorama
from pandevice.errors import PanDeviceError

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panorama', help='hostname or ip of panorama', required=True)
    parser.add_argument('--user', help='username for auth to panorama', required=True)
    args = parser.parse_args()

    try:
        panorama = Panorama(args.panorama, args.user, getpass())
    except PanDeviceError as e:
        print(e.message)

    cmd = 'show devices connected'
    try:
        res = panorama.op(cmd, xml=True)
    except PanDeviceError as e:
        print(e.message)
        sys.exit(1)

    devs_connected = xmltodict.parse(res)['response']['result']['devices']['entry']

    ha_devices_out_of_sync = []

    for dev in devs_connected:
        firewall = Firewall(serial=dev['serial'])
        panorama.add(firewall)

        cmd = 'show high-availability state'
        ha_state = xmltodict.parse(firewall.op(cmd, xml=True))['response']['result']
        if ha_state['enabled'] == 'yes':
            if ha_state['group']['running-sync'] != 'synchronized':
                ha_devices_out_of_sync.append(dev['hostname'])

    if ha_devices_out_of_sync:
        for dev in ha_devices_out_of_sync:
            print(dev)
    else:
        print('All HA devices configuration in sync!')

if __name__ == "__main__":
    main()