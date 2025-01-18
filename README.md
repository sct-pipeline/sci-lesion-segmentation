# SCISeg: Automatic Segmentation of T2-weighted Intramedullary Lesions in Spinal Cord Injury

[![medRxiv](https://img.shields.io/badge/medRxiv:SCIsegV1-10.1148/ryai.240005-blue.svg)](https://doi.org/10.1148/ryai.240005) [![arXiv](https://img.shields.io/badge/arXiv:SCIsegV2-2407.17265-b31b1b.svg)](https://doi.org/10.48550/arXiv.2407.17265)

This repository contains the code for deep learning-based segmentation of the spinal cord and intramedullary lesions in spinal cord injury (SCI). The code is based on the [nnUNetv2 framework](https://github.com/MIC-DKFZ/nnUNet).

## Model Overview

The model was trained on raw T2-weighted images of SCI patients from seven sites comprising traumatic (acute preoperative, intermediate, chronic) and non-traumatic (ischemic SCI and degenerative cervical myelopathy, DCM) SCI lesions. The data included images with heterogenous resolutions (axial/sagittal/isotropic) and scanner strengths (1T/1.5T/3T). To ensure uniformity across sites, all images were initially re-oriented to RPI. Given an input image, the model is able to segment *both* the lesion and the spinal cord. 

<img width="1000" alt="SCIsegV1_Fig2_Overview_of_segmentation_approach" src="https://github.com/ivadomed/model_seg_sci/assets/53445351/e7492462-18aa-4f7d-a03e-22863efaff72">

## Updates

### 2024-09-19

* We have added a new tutorial on how to use the SCIsegV2 model for lesion segmentation and tissue bridges computation. The tutorial is available [here](https://spinalcordtoolbox.com/user_section/tutorials/lesion-analysis.html).

### 2024-07-24

* We have released **SCIsegV2: A Universal Model for Intramedullary Lesion Segmentation in SCI**. The new model is trained on a larger cohort covering both traumatic and non-traumatic SCI lesions. SCIsegV2 is available as part of the SCT via the `sct_deepseg` function; see the installation instructions below.
* The computation of midsagittal tissue bridges is now fully-automated and powered by SCIsegV2. The automatic computation of tissue bridges is available via the `sct_analyze_lesion` function as part of SCT v6.4 and higher.
* We have moved away from ANIMA metrics and have started to use MetricsReloaded instead. This [wrapper script](https://github.com/ivadomed/MetricsReloaded/blob/main/compute_metrics_reloaded.py) is used to compute metrics and an internal fork of the package is maintained [here](https://github.com/ivadomed/MetricsReloaded).
* The computation of midsagittal tissue bridges is now fully-automated and powered by SCIsegV2. The automatic computation of tissue bridges is available via the `sct_analyze_lesion` function as part of SCT v6.4 and higher.

<p align="center">
	<img width="750" alt="SCIsegV2_Fig2_tissue_bridges" src="https://github.com/user-attachments/assets/dcfdf5aa-3956-4ae5-9461-9d70f6a73e5f">
</p>

## Using SCIsegV2

### Install dependencies

- [Spinal Cord Toolbox (SCT) v6.4](https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/tag/6.4) or higher -- follow the installation instructions [here](https://github.com/spinalcordtoolbox/spinalcordtoolbox?tab=readme-ov-file#installation)
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) 
- Python (v3.9)

Once the dependencies are installed, download the latest SCIseg model:

```bash
sct_deepseg -install-task seg_sc_lesion_t2w_sci
```

### Getting the lesion and spinal cord segmentation

To segment a single image, run the following command: 

```bash
sct_deepseg -i <INPUT> -task seg_sc_lesion_t2w_sci
```

For example:

```bash
sct_deepseg -i sub-001_T2w.nii.gz -task seg_sc_lesion_t2w_sci
```

The outputs will be saved in the same directory as the input image, with the suffix `_lesion_seg.nii.gz` for the lesion 
and `_sc_seg.nii.gz` for the spinal cord.


### Automatic measurements of midsagittal tissue bridges

This new functionality is available via [SCT](https://github.com/spinalcordtoolbox/spinalcordtoolbox)'s `sct_analyze_lesion`. The function computes the midsagittal tissue bridges and outputs the ventral and dorsal tissue bridges. 

```bash
sct_analyze_lesion -m <SUBJECT>_lesion_seg.nii.gz -s <SUBJECT>_sc_seg.nii.gz
```


## Citation Info

If you find this work and/or code useful for your research, please cite our papers:

```
@article {Naga Karthik2024.01.03.24300794,
	author = {Enamundram Naga Karthik* and Jan Valosek* and Andrew C. Smith and Dario Pfyffer and Simon Schading-Sassenhausen and Lynn Farner and Kenneth A. Weber II and Patrick Freund and Julien Cohen-Adad},
	title = {SCIseg: Automatic Segmentation of Intramedullary Lesions in Spinal Cord Injury on T2-weighted MRI Scans},
	year = {2025},
	doi = {10.1148/ryai.240005},
	URL = {https://doi.org/10.1148/ryai.240005},
	journal = {Radiology: Artificial Intelligence},
	note = {*Shared first authorship}
}
```

```
@article {karthik2024scisegv2universaltoolsegmentation,
      title={SCIsegV2: A Universal Tool for Segmentation of Intramedullary Lesions in Spinal Cord Injury}, 
      author={Enamundram Naga Karthik* and Jan Valošek* and Lynn Farner and Dario Pfyffer and Simon Schading-Sassenhausen and Anna Lebret and Gergely David and Andrew C. Smith and Kenneth A. Weber II and Maryam Seif and RHSCIR Network Imaging Group and Patrick Freund and Julien Cohen-Adad},
      year={2024},
      eprint={2407.17265},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2407.17265}, 
      note = {*Shared first authorship}
}
```
