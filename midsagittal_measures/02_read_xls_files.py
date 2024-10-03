"""
The script:
 - read XLS files (located under /results) with lesion metrics computed using sct_analyze_lesion (one XLS file per subject)
 - fetch the midsagittal slice number, midsagittal lesion length, and midsagittal lesion width
 - save the values in the dataframe and save the dataframe to a CSV file

The script needs to be run twice:
    - once for the master branch
    - once for the PR4631 branch

Note: to read XLS files, you might need to install the following packages:
    pip install openpyxl

Author: Jan Valosek
"""

import os
import sys
import re
import glob
import argparse
import logging

import numpy as np
import pandas as pd


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # default: logging.DEBUG, logging.INFO
hdlr = logging.StreamHandler(sys.stdout)
logging.root.addHandler(hdlr)

FONT_SIZE = 15


def get_parser():
    """
    parser function
    """

    parser = argparse.ArgumentParser(
        description='Read XLS files (located under /results) with lesion metrics (computed using sct_analyze_lesion),'
                    'construct a dataframe, and save the dataframe to a CSV file',
        prog=os.path.basename(__file__).strip('.py')
    )
    parser.add_argument(
        '-dir',
        required=True,
        type=str,
        help='Absolute path to the \'results\' folder with XLS files generated using \'sct_analyze_lesion. '
             'The results folders were generated using the \'01_compute_midsagittal_lesion_length_and_width.sh\' '
             'script.'
    )
    parser.add_argument(
        '-branch',
        required=True,
        type=str,
        choices=['master', 'PR4631'],
        help='Branch name (e.g., master or PR4631) with the XLS files with lesion metrics generated by '
             'SCT\'s sct_analyze_lesion'
    )
    parser.add_argument(
        '-o',
        required=False,
        default='stats',
        help='Path to the output folder where XLS table will be saved. Default: ./stats'
    )

    return parser


def fetch_subject(filename_path):
    """
    Get subject ID and session ID from the input BIDS-compatible filename or file path
    The function works both on absolute file path as well as filename
    :param filename_path: input nifti filename (e.g., sub-001_ses-01_T1w.nii.gz) or file path
    (e.g., /home/user/MRI/bids/derivatives/labels/sub-001/ses-01/anat/sub-001_ses-01_T1w.nii.gz
    :return: subject_session: subject ID (e.g., sub-001)
    :return: sessionID: session ID (e.g., ses-01)
    """

    subject = re.search('sub-(.*?)[_/]', filename_path)     # [_/] means either underscore or slash
    subjectID = subject.group(0)[:-1] if subject else ""    # [:-1] removes the last underscore or slash

    session = re.search('ses-(.*?)[_/]', filename_path)     # [_/] means either underscore or slash
    sessionID = session.group(0)[:-1] if session else ""    # [:-1] removes the last underscore or slash

    # REGEX explanation
    # . - match any character (except newline)
    # *? - match the previous element as few times as possible (zero or more times)

    return subjectID, sessionID


def get_fnames(dir_path, column_name):
    """
    Get list of XLS files with lesion metrics
    :param dir_path: list of paths to XLS files with lesion metrics
    :param column_name: branch name (e.g., master or PR4631)
    :return: pandas dataframe with the paths to the XLS files
    """

    # Get XLS files with lesion metrics
    fname_files = glob.glob(os.path.join(dir_path, '*lesion_seg_analysis_SCIsegV2.xls'))
    # remove hidden files starting with '~'
    fname_files = [f for f in fname_files if not os.path.basename(f).startswith('~')]
    # if fname_files is empty, exit
    if len(fname_files) == 0:
        print(f'ERROR: No XLS files found in {dir_path}')

    # Sort the list of file names (to make the list the same when provided the input folders in different order)
    fname_files.sort()

    # Convert fname_files_all into pandas dataframe
    df = pd.DataFrame(fname_files, columns=[column_name])

    # Add a column with participant_id and session_id
    df['participant_id'] = df[column_name].apply(lambda x: fetch_subject(x)[0])
    df['session_id'] = df[column_name].apply(lambda x: fetch_subject(x)[1])
    # Reorder the columns
    df = df[['participant_id', 'session_id', column_name]]
    print(f'Number of participants: {len(df)}')

    return df


def fetch_lesion_metrics(index, row, branch, df):
    """
    Fetch lesion metrics from the XLS file with lesion metrics generated by sct_analyze_lesion
    :param index: index of the dataframe
    :param row: row of the dataframe (one row corresponds to one participant)
    :param branch: master or PR4631
    :param df: dataframe with the paths to the XLS files for manual and predicted lesions
    :return: df: updated dataframe with the paths to the XLS files for manual and predicted lesions and lesion metrics
    """

    # Check if the XLS file with lesion metrics for manual lesion exists
    if not os.path.exists(row[branch]):
        raise ValueError(f'ERROR: {row[+branch]} does not exist.')

    # Read the XLS file with lesion metrics for lesion predicted by our 3D SCIseg nnUNet model
    df_lesion = pd.read_excel(row[branch], sheet_name='measures')
    # Get the metrics
    midsagittal_slice = str(df_lesion['midsagittal_spinal_cord_slice'].values[0])
    midsagittal_length = df_lesion['length_midsagittal_slice [mm]'].values[0]
    midsagittal_width = df_lesion['width_midsagittal_slice [mm]'].values[0]
    # Check if 'slice_' + midsagittal_slice + '_dorsal_bridge_width [mm]' is in the columns
    if 'slice_' + midsagittal_slice + '_dorsal_bridge_width [mm]' in df_lesion.columns:
        dorsal_tissue_bridge = df_lesion['slice_' + midsagittal_slice + '_dorsal_bridge_width [mm]'].values[0]
        ventral_tissue_bridge = df_lesion['slice_' + midsagittal_slice + '_ventral_bridge_width [mm]'].values[0]
    else:
        dorsal_tissue_bridge = np.nan
        ventral_tissue_bridge = np.nan

    # One lesion -- # TODO: consider also multiple lesions
    # Save the values in the currently processed df row
    df.at[index, 'midsagittal_slice'] = midsagittal_slice
    df.at[index, 'midsagittal_length'] = midsagittal_length
    df.at[index, 'midsagittal_width'] = midsagittal_width
    df.at[index, 'dorsal_tissue_bridge'] = dorsal_tissue_bridge
    df.at[index, 'ventral_tissue_bridge'] = ventral_tissue_bridge

    return df


def main():
    # Parse the command line arguments
    parser = get_parser()
    args = parser.parse_args()

    branch_name = args.branch

    # Output directory
    output_dir = os.path.join(os.getcwd(), args.o)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f'Created {output_dir}')

    # Dump log file there
    fname_log = f'log.txt'
    if os.path.exists(fname_log):
        os.remove(fname_log)
    fh = logging.FileHandler(os.path.join(os.path.abspath(output_dir), fname_log))
    logging.root.addHandler(fh)

    # Check if the input path exists
    if not os.path.exists(args.dir):
        raise ValueError(f'ERROR: {args.dir} does not exist.')

    # For each participant_id, get XLS files with lesion metrics
    df = get_fnames(args.dir, column_name=branch_name)

    # Remove sub-zh111 from the list of participants (it has multiple lesions)
    df = df[df['participant_id'] != 'sub-zh111']

    # Iterate over the rows of the dataframe and read the XLS files
    for index, row in df.iterrows():

        logger.info(f'Processing XLS files for {row["participant_id"]}')

        # Read the XLS file with lesion metrics
        df = fetch_lesion_metrics(index, row, branch_name, df)

    # remove the branch column containing the paths to the XLS files
    df.drop(columns=[branch_name], inplace=True)
    # Save the dataframe with lesion metrics to a CSV file
    df.to_csv(os.path.join(output_dir, f'lesion_metrics_{branch_name}.csv'), index=False)
    logger.info(f'Saved lesion metrics to {output_dir}/lesion_metrics_{branch_name}.csv')


if __name__ == '__main__':
    main()