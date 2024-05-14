from typing import List

from aionowplaying.backend import BaseNowPlayingBackend


class MacOSNowPlayingBackend(BaseNowPlayingBackend):
    @staticmethod
    def target_platforms() -> List[str]:
        return ['darwin']

    def run(self):
        pass

    def destroy(self):
        pass
