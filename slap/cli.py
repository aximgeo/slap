#!/usr/bin/env python

import argparse
import slap


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username",
                        required=True,
                        help="Portal or AGS username (ex: --username john)")
    parser.add_argument("-p", "--password",
                        required=True,
                        help="Portal or AGS password (ex: --password myPassword)")
    parser.add_argument("-c", "--config",
                        required=True,
                        help="full path to config file (ex: --config c:/configs/int_config.json)")
    parser.add_argument("-i", "--inputs",
                        action="append",
                        help="one or more inputs to publish (ex: -i mxd/bar.mxd -i mxd/foo.mxd")
    parser.add_argument("-a", "--all",
                        action="store_true",
                        help="publish all entries in config")
    parser.add_argument("-g", "--git",
                        help="publish all mxd files that have changed between HEAD and this commit "
                             "(ex: -g b45e095834af1bc8f4c348bb4aad66bddcadeab4")
    args = parser.parse_args()

    if not args.username:
        parser.error("username is required")

    if not args.password:
        parser.error("password is required")

    if not args.config:
        parser.error("Full path to config file is required")

    if not slap.publisher.only_one([args.git, args.inputs, args.all]):
        parser.error("Specify only one of --git, --all, or --inputs")

    if not args.all and not args.inputs and not args.git:
        parser.error("Specify one of --git, --all, or --inputs")

    return args


def main():
    args = get_args()
    publisher = slap.publisher.Publisher()
    print "Loading config..."
    publisher.load_config(args.config)
    publisher.create_server_connection_file(args.username, args.password)
    publisher.init_api(
        ags_url=publisher.config['agsUrl'],
        token_url=publisher.config['tokenUrl'] if 'tokenUrl' in publisher.config else None,
        portal_url=publisher.config['portalUrl'] if 'portalUrl' in publisher.config else None,
        certs=publisher.config['certs'] if 'certs' in publisher.config else True,
        username=args.username,
        password=args.password
    )
    if args.inputs:
        for i in args.inputs:
            publisher.publish_input(i)
    elif args.git:
        print "Getting changes from git..."
        changed_files = slap.git.get_changed_mxds(args.git)
        print changed_files
        for i in changed_files:
            publisher.publish_input(i)
    elif args.all:
        publisher.publish_all()

if __name__ == "__main__":
    main()
