"""Direct M-ABSA directory implementation of SeedSourcePort (optional CLI override)."""

from pathlib import Path

from ...domain.ports.seeding import SeedBundle
from .mabsa_parser import build_curated_seed_bundle


class MabsaDirectorySeedSource:
    """Loads curated seed data directly from a local M-ABSA data folder."""

    def __init__(
        self,
        mabsa_root: Path,
        domains: tuple[str, ...] = ("phone", "laptop"),
        include_accessories: bool = True,
        include_vi_samples: bool = True,
    ) -> None:
        self._mabsa_root = mabsa_root
        self._domains = domains
        self._include_accessories = include_accessories
        self._include_vi_samples = include_vi_samples

    def load(self) -> SeedBundle:
        return build_curated_seed_bundle(
            mabsa_root=self._mabsa_root,
            domains=self._domains,
            include_accessories=self._include_accessories,
            include_vi_samples=self._include_vi_samples,
        )
