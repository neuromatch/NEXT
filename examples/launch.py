"""
Usage:
    launch.py <init_filename>
    launch.py <init_filename> <zip_path> [--noS3 | --noupload]

Arguments:
    initExp_path (required) : path to a YAML file for arguments to launch experiment
    zip_path (optional) : zip file that contains the targets
                          (which are then uploaded to S3).

Options:
    -h, --help
    [--noS3, --noupload] : Do not upload targets to S3.

Example:

    > cd ~/Developer/NEXT/examples/
    > python launch.py strange_fruit_triplet/init.yaml strange_fruit_triplet/strangefruit30.zip

"""


from .docopt import docopt
import os
import sys
from collections import OrderedDict
import base64
import yaml
import requests

sys.path.append('../../next/lib')


def verify_environ():
    to_have = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BUCKET_NAME']
    error = False
    for key in to_have:
        if key not in os.environ:
            error = True
            print('Must define ' + key + ' to upload to S3')
    if 'NEXT_BACKEND_GLOBAL_HOST' not in os.environ:
        print('NEXT_BACKEND_GLOBAL_HOST is not defined, '
              'defaulting to localhost')
    return error


def launch(init_filename, targets_filename=None, upload=True):
    environ_error = verify_environ()

    with open(init_filename, 'r') as f:
        init = yaml.load(f)

    header = "data:application/{};base64,"
    args = base64.encodestring(yaml.dump(init))
    d = {'args': header.format('x-yaml') + args,
         'key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
         'secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
         'bucket_id': os.environ.get('AWS_BUCKET_NAME'),
         'upload': str(upload)}

    if upload and environ_error:
        print('Exiting early. Use --noS3 or --noupload to not upload to S3'
              ' and define AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY and '
              'AWS_BUCKET_NAME')
        raise ValueError('Define appropriate variables')

    if not upload:
        for key in ['key_id', 'secret_key', 'bucket_id']:
            d.pop(key, None)

    if targets_filename:
        with open(targets_filename, 'r') as f:
            targets = f.read()
        d['targets'] = header.format('zip') + base64.encodestring(targets)

    d = OrderedDict(d)

    host_url = os.environ.get('NEXT_BACKEND_GLOBAL_HOST', 'localhost')
    host_url = 'http://' + host_url + ':8000'

    header = ['{}:{}'.format(key, len(item)) for key, item in list(d.items())]
    header = ';'.join(header) + '\n'

    to_send = ''.join([item for _, item in list(d.items())])

    data = header + to_send

    r = requests.post(host_url + '/assistant/init/experiment', data=data)
    response = r.json()
    if not response['success']:
        print('An error occured launching the experiment:\n')
        print(response['message'])
        raise ValueError("Experiment didn't launch successfully")

    dashboard_url = host_url + '/dashboard/experiment_dashboard/{}/{}'
    dashboard_url = dashboard_url.format(response['exp_uid'], init['app_id'])
    print('Dashboard URL:\n    {}'.format(dashboard_url))
    print('\n')
    print('NEXT Home URL:\n    {}'.format(host_url + '/home'))
    return response


if __name__ == "__main__":
    args = docopt(__doc__)
    upload = True
    upload = not (args['--noS3'] or args['--noupload'])
    print(upload)

    print(args['<zip_path>'])
    if any([key in args['<zip_path>'] for key in ['csv', 'txt']]):
        upload = False
    print(upload)

    print(args, '\n')
    launch(args['<init_filename>'], targets_filename=args['<zip_path>'],
           upload=upload)
