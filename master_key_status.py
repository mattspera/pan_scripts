import argparse
import csv
from getpass import getpass

import xmltodict
from pandevice.firewall import Firewall
from pandevice.panorama import Panorama
from pandevice.errors import PanDeviceError

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panorama', help='hostname or ip of panorama', required=True)
    parser.add_argument('--user', help='username for auth to panorama', required=True)
    parser.add_argument('--out_file', help='filename for output csv e.g. mkey_status_prod.csv', required=True)
    args = parser.parse_args()

    try:
        panorama = Panorama(args.panorama, args.user, getpass())
    except PanDeviceError as e:
        print(e.message)

    cmd = 'show devices connected'
    res = panorama.op(cmd, xml=True)
    devs_connected = xmltodict.parse(res)['response']['result']['devices']['entry']

    master_key_props_list = []

    for dev in devs_connected:
        firewall = Firewall(serial=dev['serial'])
        panorama.add(firewall)

        cmd = 'show system masterkey-properties'
        master_key_props = xmltodict.parse(firewall.op(cmd, xml=True))['response']['result']
        master_key_props['hostname'] = dev['hostname']

        master_key_props_list.append(master_key_props)

    with open(args.out_file, 'w', newline='') as file_obj:
        fieldnames = master_key_props_list[0].keys()
        writer_obj = csv.DictWriter(file_obj, fieldnames=fieldnames)

        writer_obj.writeheader()
        for dev_mkey_props in master_key_props_list:
            writer_obj.writerow(dev_mkey_props)

if __name__ == "__main__":
    main()