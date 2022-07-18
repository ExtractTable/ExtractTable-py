VERSION = (2, 4, 0)
PRERELEASE = None  # "alpha", "beta" or "rc"
REVISION = None


def generate_version():
    version_parts = [".".join(map(str, VERSION))]
    if PRERELEASE is not None:
        version_parts.append("-{}".format(PRERELEASE))
    if REVISION is not None:
        version_parts.append(".{}".format(REVISION))
    return "".join(version_parts)


__title__ = "ExtractTable"
__description__ = "Extract table data from images and scanned PDFs. Easily convert image to excel, convert pdf to table"
__url__ = "https://github.com/ExtractTable/ExtractTable-py"
__version__ = generate_version()
__author__ = "Saradhi"
__author_email__ = "saradhi@extracttable.com"
__license__ = "Apache License 2.0"
