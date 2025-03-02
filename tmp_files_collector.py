#!/usr/bin/env python3
import os
import time
import tarfile
import argparse
import datetime
import glob
import logging
import sys

class TmpFileCollector:
    def __init__(self, base_dir: str):
        """
        :param base_dir: Directory where 'tmp' folder and archives (files.tar.gz) will be stored.
        """
        self.base_dir = os.path.abspath(base_dir)
        self.tmp_folder = os.path.join(self.base_dir, "tmp")

        logging.debug(f"Initializing FileCollector with base_dir={self.base_dir}")

        if not os.path.exists(self.base_dir):
            logging.debug(f"Base directory {self.base_dir} does not exist. Creating...")
            os.makedirs(self.base_dir)

        if not os.path.exists(self.tmp_folder):
            logging.debug(f"Creating tmp folder at {self.tmp_folder}...")
            os.makedirs(self.tmp_folder)

    @staticmethod
    def is_swap_or_hidden_file(filename: str) -> bool:
        """
        Returns True if the file is either hidden (starts with a '.')
        or matches a common swap file extension (.swp, .swo, .swx, etc.).
        """
        # Hidden file: starts with '.'
        if filename.startswith('.'):
            return True

        # Swap file checks
        swap_extensions = (".swp", ".swo", ".swx")
        if any(filename.endswith(ext) for ext in swap_extensions):
            return True

        return False

    def rename_old_archive(self):
        """
        If an existing 'files.tar.gz' is present, rename it with a timestamp.
        """
        logging.debug(f"Checking for existing 'files.tar.gz' in {self.base_dir} ...")

        live_archive_path = os.path.join(self.base_dir, "files.tar.gz")
        if os.path.exists(live_archive_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = os.path.join(self.base_dir, f"files_{timestamp}.tar.gz")
            logging.debug(f"Renaming existing 'files.tar.gz' to '{os.path.basename(new_name)}'.")
            os.rename(live_archive_path, new_name)
        else:
            logging.debug("No existing 'files.tar.gz' found; no rename needed.")

    def run(self):
        """
        Main loop:
          1. Repeatedly count files in <base_dir>/tmp (ignoring swap & hidden files).
          2. Once 10 non-swap/hidden files appear:
             - rename any old archive
             - create 'files.tar.gz'
             - remove those files
             - print 'files collected'
             - then exit.
        """
        logging.debug("Entering main loop. Waiting until we have at least 10 valid files...")

        while True:
            all_items = os.listdir(self.tmp_folder)
            valid_files = []

            for f in all_items:
                full_path = os.path.join(self.tmp_folder, f)
                if os.path.isfile(full_path) and not self.is_swap_or_hidden_file(f):
                    valid_files.append(f)

            file_count = len(valid_files)
            logging.debug(
                f"Found {file_count} non-swap/hidden file(s) in {self.tmp_folder} "
                f"(total items: {len(all_items)})."
            )

            if file_count >= 10:
                logging.debug(f"Reached threshold with {file_count} files. Preparing to archive...")
                self.rename_old_archive()

                # Create new archive with the (>=10) files
                live_archive_path = os.path.join(self.base_dir, "files.tar.gz")
                logging.debug(f"Creating new archive {live_archive_path} with these files: {valid_files}")
                with tarfile.open(live_archive_path, "w:gz") as tar:
                    for f in valid_files:
                        tar.add(os.path.join(self.tmp_folder, f), arcname=f)

                # Remove the original files
                logging.debug("Removing original files from tmp folder...")
                for f in valid_files:
                    os.remove(os.path.join(self.tmp_folder, f))

                logging.debug("All files archived and removed from tmp.")
                print("files collected")
                break

            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Collect and archive files once 10 appear.")
    parser.add_argument("--base-dir", default=".", help="Base directory where tmp folder and archives live.")
    parser.add_argument("--log-level", default="ERROR", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    # Configure logging (adjust level/format as needed)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout
    )

    # Catch any unhandled exceptions in one place:
    try:
        collector = TmpFileCollector(base_dir=args.base_dir, )
        collector.run()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Exit with a non-zero status to indicate an error
        sys.exit(1)


if __name__ == "__main__":
    main()
