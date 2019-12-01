VERSION = (1, 2, 1)
PRERELEASE = None  # "alpha", "beta" or "rc"
REVISION = 2


def generate_version(version, prerelease=None, revision=None):
    version_parts = [".".join(map(str, version))]
    if prerelease is not None:
        version_parts.append("-{}".format(prerelease))
    if revision is not None:
        version_parts.append(".{}".format(revision))
    return "".join(version_parts)


__title__ = "ExtractTable"
__description__ = "Extract tabular data from images and scanned PDFs"
__url__ = "https://github.com/ExtractTable/ExtractTable-py"
__version__ = generate_version(VERSION, prerelease=PRERELEASE, revision=REVISION)
__author__ = "Saradhi"
__author_email__ = "saradhi@extracttable.com"
__license__ = "Apache License 2.0"
