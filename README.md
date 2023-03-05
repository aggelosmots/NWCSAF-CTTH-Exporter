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

## Output

In the output directory, three new folders will show up:

1) A log.csv file shows up with the history of previously executed files in order to not export them again