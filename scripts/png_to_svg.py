#!/usr/bin/env python3
"""
PNG to SVG Converter

Author: AJ Igherighe | The PseudoCodeus
"""

import os
import subprocess
from pathlib import Path
from PIL import Image
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PNGtoSVGConverter:
    """PNG to SVG converter with error handling."""

    def __init__(self, input_dir: str, output_dir: str, max_workers: int = 4):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

    def convert_single(self, png_path: Path) -> Optional[Path]:
        """Convert single PNG to SVG with multiple fallback methods."""
        try:
            svg_path = self.output_dir / f"{png_path.stem}.svg"

            success = self._convert_with_potrace(png_path, svg_path)

            if not success:
                logger.warning(
                    f"Potrace failed for {png_path.name}, trying manual conversion"
                )
                success = self._convert_manual(png_path, svg_path)

            if success:
                logger.info(f"✓ Converted: {png_path.name} -> {svg_path.name}")
                return svg_path
            else:
                logger.error(f"✗ Failed to convert: {png_path.name}")
                return None

        except Exception as e:
            logger.error(f"Error converting {png_path.name}: {str(e)}")
            logger.debug(traceback.format_exc())
            return None

    def _convert_with_potrace(self, png_path: Path, svg_path: Path) -> bool:
        """Convert using potrace (best for card images)."""
        try:
            with Image.open(png_path) as img:
                bw_img = img.convert("1")
                pbm_path = svg_path.with_suffix(".pbm")
                bw_img.save(pbm_path, format="PPM")

            cmd = [
                "potrace",
                str(pbm_path),
                "-s",
                "-o",
                str(svg_path),
                "--flat",
                "--opaque",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if pbm_path.exists():
                pbm_path.unlink()

            return result.returncode == 0 and svg_path.exists()

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.warning(f"Potrace not available or failed: {e}")
            return False

    def _convert_manual(self, png_path: Path, svg_path: Path) -> bool:
        """Manual conversion using Pillow (fallback method)."""
        try:
            from svgwrite import Drawing
            from svgwrite.image import Image as SVGImage

            with Image.open(png_path) as img:
                width, height = img.size

                dwg = Drawing(
                    filename=str(svg_path), size=(f"{width}px", f"{height}px")
                )

                import base64
                from io import BytesIO

                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                dwg.add(
                    SVGImage(
                        href=f"data:image/png;base64,{img_str}",
                        insert=(0, 0),
                        size=(f"{width}px", f"{height}px"),
                    )
                )

                dwg.save()
                return True

        except Exception as e:
            logger.error(f"Manual conversion failed: {e}")
            return False

    def convert_batch(self) -> List[Path]:
        """Convert all PNGs in directory with parallel processing."""
        png_files = list(self.input_dir.glob("*.png"))

        if not png_files:
            logger.warning(f"No PNG files found in {self.input_dir}")
            return []

        logger.info(f"Found {len(png_files)} PNG files to convert")

        successful_conversions = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.convert_single, png_file): png_file
                for png_file in png_files
            }

            for future in as_completed(future_to_file):
                png_file = future_to_file[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        successful_conversions.append(result)
                except Exception as e:
                    logger.error(f"Thread failed for {png_file.name}: {e}")

        logger.info(
            f"Successfully converted {len(successful_conversions)}/{len(png_files)} files"
        )
        return successful_conversions


def main():
    """Main entry point with command line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PNG card images to SVG for web use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cards/png/ cards/svg/
  %(prog)s cards/png/ cards/svg/ --workers 8
  %(prog)s --input cards/png/ --output cards/svg/ --verbose
        """,
    )

    parser.add_argument("input_dir", help="Directory containing PNG files")

    parser.add_argument("output_dir", help="Directory to save SVG files")

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    converter = PNGtoSVGConverter(
        input_dir=args.input_dir, output_dir=args.output_dir, max_workers=args.workers
    )

    results = converter.convert_batch()

    print(f"\n{'=' * 50}")
    print(f"CONVERSION COMPLETE")
    print(f"{'=' * 50}")
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Files processed: {len(results)}")

    if results:
        print(f"\nFirst 5 converted files:")
        for svg in results[:5]:
            print(f"  • {svg.name}")
        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")

    print(f"\nSVG files are ready for web!")
    print(f'Use in templates: <img src="/cards/{results[0].name}" />')


if __name__ == "__main__":
    main()
