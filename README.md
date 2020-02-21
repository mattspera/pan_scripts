# pan_scripts

A collection of scripts that leverage the Palo Alto Networks device API to perform various management tasks.

## Version Info

- Palo Alto: Tested on PAN-OS 8.1.x
- Python: Python 3 required

## Python Library Dependencies

- pandevice
- xmltodict

## Scripts

- `ha_devices_out_of_sync.py`: A Python script that prints to screen a list of Panorama-connected firewall clusters that currently show their high-availability configuration synchronisation status as out-of-sync.
- `master_key_status.py`: A Python script that outputs to csv a report detailing the master key status/properties (e.g. time to expiry, etc.) of Panorama-connected firewall devices.
- `convert_usergroups_pan.py`: A Python script that utilises a legacy to LDAP group mapping csv as input and converts user groups found within user-based security policies in a specified Panorama device-group based on this mapping (useful for when migrating user-based security policy from one vendor to Palo Alto and the original legacy groups remain in the migrated policy output by Expedition)
- `validate_usergrous_pan.py`: A Python script that validates whether user groups found within user-based security policies in a specified Panorama device-group have a corresponding group-mapping entry on a specified firewall device (useful if verifying policy held in a Panorama instance that does not manage the intended firewall recipient of the policy - if the Panorama instance does managed the intended firewall recipient, you can set the firewall as the master device for the device group to validate user-based policies).

Run `python <script_name>.py --help` for required script input arguments.
