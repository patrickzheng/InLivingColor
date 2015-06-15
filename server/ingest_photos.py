import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--verbosity", help="increase output verbosity")
args = parser.parse_args()
if args.verbosity:
    print "verbosity turned on"


def QueueIngestion(collection, photoids, skip_already_downloaded=False):
    """

    """
