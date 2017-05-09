from .downloader import Downloader
from .loader import Loader


def get_loader():
    return Loader()


def get_vm(parent):
    return Downloader(parent=parent).get_vm(parent.interval)
