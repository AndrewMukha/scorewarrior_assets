#! /usr/bin/env python3

import argparse
import shutil
from pathlib import Path

from toolbox.assets import AbstractAsset, Bundle, SoloImage
from toolbox.image_processor import AbstractImageProcessor, PillowImageProcessor
from toolbox.vcs import AbstractVcs, Git
from toolbox.zip_service import AbstractZipService, SevenZipService, ZipService


def _get_zip_service() -> AbstractZipService:
    if shutil.which("7z"):
        return SevenZipService()
    else:
        return ZipService()


def _get_assets(
    assets_dir: Path, image_processor: AbstractImageProcessor
) -> set[AbstractAsset]:
    files = list(assets_dir.rglob("*"))
    image_files = [f for f in files if f.suffix in {".png", ".jpg"}]
    json_files = {f.stem: f for f in files if f.suffix == ".json"}

    assets = {
        Bundle(image_file, json_files.get(image_file.stem), image_processor)
        if image_file.stem in json_files
        else SoloImage(image_file)
        for image_file in image_files
    }

    return assets


def _get_modified_assets_sources(assets_dir: Path, revision: str, vcs: AbstractVcs) -> tuple[set[Path], set [Path]]:
    changed_files = vcs.get_changed_files(revision=revision)
    assets_dir_name = assets_dir.name
    assets_parent = assets_dir.parent

    changed_assets = [
        assets_parent / f
        for f in changed_files
        if f.startswith(assets_dir_name)
    ]

    modified_assets = set()
    deleted_assets = set()

    for asset in changed_assets:
        if asset.exists():
            modified_assets.add(asset)
        else:
            deleted_assets.add(asset)

    return modified_assets, deleted_assets


def _write_not_changed_assets(
    result_dir: Path, assets_dir: Path, all_assets: set[AbstractAsset]
) -> None:
    with open(result_dir / "unchanged.txt", "w") as file:
        asset_paths = [
            f.relative_to(assets_dir)
            for asset in all_assets
            for f in asset.get_files()
        ]
        for path in sorted(asset_paths):
            file.write(f"{path}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build game assets")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        required=True,
        help="Path to assets directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Path to output directory",
    )
    parser.add_argument(
        "--revision",
        required=True,
        help="Path to output directory",
    )
    args = parser.parse_args()

    image_processor = PillowImageProcessor()
    zip_service = _get_zip_service()
    git = Git()

    all_assets = _get_assets(args.assets_dir, image_processor)

    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)

    revision_dir = args.output_dir / args.revision[:6]
    result_dir = revision_dir / "result"
    result_dir.mkdir(parents=True)

    modified_assets_sources, deleted_assets_sources = _get_modified_assets_sources(args.assets_dir, args.revision, git)
    modified_assets = set()
    for asset in all_assets:
        if any(a.samefile(c) for a in modified_assets_sources for c in asset.get_files()):
            asset.build(result_dir, zip_service)
            modified_assets.add(asset)

    for source in deleted_assets_sources:
        print(f"Asset source {source} was deleted")

    not_modified_assets = all_assets - modified_assets
    _write_not_changed_assets(result_dir, args.assets_dir, not_modified_assets)
    git.write_changes(revision_dir / "change")


if __name__ == "__main__":
    main()
