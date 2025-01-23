"""
This script:
  1. Clones different datasets from data.neuro.polymtl.ca and spineimage.ca
  2. Checkout the specific commit ID of the datasets
  3. Gets the git commit ID of the datasets and saves it to git_branch_commit.log
  4. Downloads relevant nii files from git-annex -- for now, only T2w images are downloaded to save space. If the flag
    '--no-download' is provided, this step is skipped.

Examples:
    python download_data.py -ofolder <PATH_TO_FOLDER_WHERE_DATA_WILL_BE_DOWNLOADED>
    python download_data.py -ofolder <PATH_TO_FOLDER_WHERE_DATA_WILL_BE_DOWNLOADED> --no-download

Author: Jan Valosek
"""

import os
import subprocess
import argparse
from datetime import datetime

from utils import get_git_branch_and_commit

SITES_CONFIG = {
    # "neuropoly": {
    #     "base_url": "git@data.neuro.polymtl.ca:datasets",
    #     "datasets": [
    #         ("sci-zurich", "3ba898e0"),
    #         ("dcm-zurich-lesions", "d214e06"),
    #         ("dcm-zurich-lesions-20231115", "28a70d9"),
    #         ("sci-colorado", "558303f"),
    #         ("sci-paris", "0a0d252")
    #     ]
    # },
    "spineimage": {
        "base_url": "gitea@spineimage.ca",
        "datasets": {
            "TOH": ("site_03", "master"),
            "MON": ("site_006", "main"),
            "VGH": ("site_007", "main"),
            "SAI": ("site_009", "main"),
            "NSHA": ("site_012", "master"),
            "HGH": ("site_013", "master"),
            "HEJ": ("site_014", "master"),
        }
    }
}

def download_dataset(site_url, dataset, skip_download=False):

    dataset_name = dataset[0]
    dataset_commit = dataset[1]

    # Clone the dataset if it does not exist
    if not os.path.exists(dataset_name):
        clone_url = f"{site_url}/{dataset_name}.git"
        subprocess.run(["git", "clone", clone_url], check=True)
        os.chdir(dataset_name)
        subprocess.run(["git", "annex", "dead", "here"])
    else:
        print(f"Dataset {dataset_name} already exists, skipping 'git clone'")
        os.chdir(dataset_name)

    # Checkout the commit or branch
    subprocess.run(["git", "checkout", dataset_commit])

    # Get the git commit ID of the dataset
    dataset_path = os.getcwd()
    branch, commit = get_git_branch_and_commit(dataset_path)
    with open(LOG_FILENAME, "a") as log_file:
        log_file.write(f"{dataset_name}: git-{branch}-{commit}\n")

    # Download nii files from git-annex
    if not skip_download:
        files_t2 = subprocess.run(["find", ".", "-name", "*T2w*.nii.gz"],
                                  capture_output=True, text=True).stdout.splitlines()
        files_t2 = [file for file in files_t2 if "STIR" not in file]
        if files_t2:
            subprocess.run(["git", "annex", "get"] + files_t2)
        else:
            print(f"No T2w files found in dataset {dataset_name}")

    os.chdir("..")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download datasets from data.neuro.polymtl.ca and spineimage.ca")
    parser.add_argument("-ofolder",
                        metavar='DIR_NAME',
                        required=True,
                        type=str,
                        help="Path to the folder where data will be downloaded")
    parser.add_argument("--no-download",
                        action="store_true",
                        help="Skip the 'git annex get' step and only clone the repositories and checkout to the "
                             "specified commit or branch")
    args = parser.parse_args()

    PATH_DATA = os.path.abspath(os.path.expanduser(args.ofolder))
    os.makedirs(PATH_DATA, exist_ok=True)
    os.chdir(PATH_DATA)

    LOG_FILENAME = f"{PATH_DATA}/git_branch_commit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # data.neuro.polymtl.ca
    if "neuropoly" in SITES_CONFIG:
        for dataset in SITES_CONFIG["neuropoly"]["datasets"]:
            download_dataset(SITES_CONFIG["neuropoly"]["base_url"], dataset, args.no_download)

    # spineimage.ca
    if "spineimage" in SITES_CONFIG:
        for site, dataset in SITES_CONFIG["spineimage"]["datasets"].items():
            site_url = f"{SITES_CONFIG['spineimage']['base_url']}:{site}"
            download_dataset(site_url, dataset, args.no_download)

    print(f"Log file with git branch and commit IDs saved to {LOG_FILENAME}")