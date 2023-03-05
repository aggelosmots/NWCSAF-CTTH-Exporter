# NWCSAF CTTH Exporter

<p align="center">
    <img src=ctth_exporter/nwcsaf_icon_no_background.ico>
</p>

This is a small project for exporting data of ctth files in csv, png and tif format fast and easy.

This app was developed with satpy package

## Installation

Using conda
```
conda install -c conda-forge satpy
```
or
```
pip install satpy h5netcdf netcdf4 rasterio 
```

## Execution
To run the program, simply run [MainWindow.py](ctth_exporter/MainWindow.py)

## Input

**NetCDF files** with format:

*S_NWC_CTTH_MSG4_MSG-N-VISIR_T_Z.nc*

## Output

In the output directory, those will show up:

1) A log.csv file shows up with the history of previously executed files in order to not export them again
2) The exported file will show up as a folder with the the csv, GeoTIFF and images

## Features
### **Selecting Area**
User can select a rectagle area in order to export only a Region of Intrest

### **Waiting for new files in background**
CTTH products are used in Nowcasting and new CTTH files can be received anytime in an input folder. This application is ready to export those new files whenever they show up.

### **Sleep Mode**
User can put an execution timer, putting app in sleep on the backdround