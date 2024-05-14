from typing import List

from aionowplaying.backend import BaseNowPlayingBackend


class WindowsNowPlayingBackend(BaseNowPlayingBackend):
    @staticmethod
    def target_platforms() -> List[str]:
        return ['win32', 'cygwin']

    def run(self):
        pass

    def destroy(self):
        pass
