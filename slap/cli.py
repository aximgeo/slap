import sys
import argparse
from slap.publisher import Publisher
from slap import git


def _create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    publish_parser = subparsers.add_parser('publish', help='publish services')
    _add_publish_arguments(publish_parser)

    init_parser = subparsers.add_parser('init', help='initialize config from a list of files')
    _add_init_arguments(init_parser)

    return parser


def _add_publish_arguments(parser):
    parser.set_defaults(func=publish)
    parser.add_argument("-u", "--username",
                        required=True,
                        help="Portal or AGS username (ex: --username john)")
    parser.add_argument("-p", "--password",
                        required=True,
                        help="Portal or AGS password (ex: --password myPassword)")
    parser.add_argument("-c", "--config",
                        default="config.json",
                        help="path to config file (ex: --config configs/int_config.json)")
    parser.add_argument("-s", "--site",
                        action="store_true",
                        help="create a site before publishing")
    parser.add_argument("-n", "--name",
                        help="override the hostname in config")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--input",
                       action="append",
                       help="one or more inputs to publish (ex: -i mxd/bar.mxd -i mxd/foo.mxd")
    group.add_argument("-g", "--git",
                       help="publish all mxd files that have changed between HEAD and this commit "
                            "(ex: -g b45e095834af1bc8f4c348bb4aad66bddcadeab4")


def _add_init_arguments(parser):
    parser.set_defaults(func=initialize_config)
    parser.add_argument("-i", "--input",
                        required=True,
                        help="path to a directory containing MXDs to publish (ex: --folder c:/my/maps")


def publish(args):
    publisher = Publisher(args.username, args.password, args.config, args.name)

    if args.site:
        print "Creating site..."
        if "site" in publisher.config:
            publisher.api.create_site(args.username, args.password, publisher.config["site"])
        else:
            publisher.api.create_default_site()

    print "Registering data sources..."
    publisher.register_data_sources()

    if args.input:
        for i in args.input:
            print "Publishing {}...".format(i)
            publisher.publish_input(i)
    elif args.git:
        print "Getting changes from git..."
        changed_files = git.get_changed_mxds(args.git)
        print changed_files
        for i in changed_files:
            publisher.publish_input(i)
    else:
        print "Publishing all..."
        publisher.publish_all()


def initialize_config(args):
    print "not implemented"


def main(raw_args):
    parser = _create_parser()
    args = parser.parse_args(raw_args)
    args.func(args)

if __name__ == "__main__":
    main(sys.argv[1:])
