from satpy import Scene
import numpy as np
from glob import glob
from pandas import DataFrame
from os import path, mkdir


class CtthNwcsafExporter:
    def __init__(self, filename):
        self.filename = filename

    def load_image(self):
        """
        By using satpy Scene(), an image is loaded as a scene and 
        gives the user the capability to select a number of available
        channels.
        """

        scene = Scene(reader='nwcsaf-geo',filenames=glob(self.filename))
        channels = ["ctth_alti", "ctth_tempe", "ctth_pres"]
        scene.load(channels)
        
        return scene, channels

    def get_resolution(self, scene, channels):
        """
        Returns number of rows and columns from the scene.
        """

        rows, cols = scene[channels[0]].shape
        return rows, cols

    def data_dict(self, scene, x_pixel, y_pixel, list_of_channels):
        """
        Taking resolution of image and the selected channels 
        and returns a dictionary with the following keys and 
        values: x, y, latitude, longitude and the selected channels 
        """

        # Initialization
        data_dict = {
            'x': [],
            'y': [],
            'lat_km': [],
            'lon_km': [],
            'lat_deg': [],
            'lon_deg': []
        }

        keys_list = []
        lat = list(scene[list_of_channels[0]].y.values)
        lon = list(scene[list_of_channels[0]].x.values)
        
        # Creating keys of dictionary
        for key, i in zip(list_of_channels, range(len(list_of_channels))):
            data_dict[f'{key}'] = []
            exec(f"{key}_name = []")
            # Load values in key names from the scene
            key_name = scene[list_of_channels[i]].values
            keys_list.append(key_name)
        
        # Exporting values from the channels
        for i in range(x_pixel):
            for j in range(y_pixel):
                data_dict['x'].append(i)
                data_dict['y'].append(j)
                data_dict['lat_km'].append(lat[i])
                data_dict['lon_km'].append(lon[j])
                
                coord_conv = coordConvertion()
                lat_deg, lon_deg = coord_conv.pixcoord2geocoord(j, i)
                
                data_dict['lat_deg'].append(lat_deg)
                data_dict['lon_deg'].append(lon_deg)
                
                # key -> key of data_dict, keys -> value for indexing keys_list 
                for key, keys in zip(list_of_channels, range(len(keys_list))):
                    data_dict[key].append((keys_list[keys])[i][j])      # type: ignore

        return data_dict

    def export_data(self, scene, data_in_dict, channels, output_dir):
        """
        Exports image in a csv file, a png image and GeoTiff
        """
        
        scene.save_datasets(filename="{name}.tif",
                            datasets=channels,
                            writer='geotiff', 
                            base_dir=f"{output_dir}/ctth_{self.filename[-19:-3:]}/GeoTIFF", 
                            compute=False)
        
        
        scene.save_datasets(filename="{name}.jpg",
                            datasets=channels, 
                            writer='simple_image', 
                            base_dir=f"{output_dir}/ctth_{self.filename[-19:-3:]}/image",
                            compute=False)
        

        if not path.exists(f"{output_dir}/ctth_{self.filename[-19:-3:]}/ASCII"):
            mkdir(f"{output_dir}/ctth_{self.filename[-19:-3:]}/ASCII")

        df = DataFrame(data_in_dict)
        df.to_csv(f"{output_dir}/ctth_{self.filename[-19:-3:]}/ASCII/ctth_{self.filename[-19:-3:]}.txt")
       
        
    def slice_data(self, data_dict ,lon1, lon2, lat1, lat2):

        #  Initialization
        index = 0

        # Lists in order to get initial and final pixel
        x = []
        y = []

        # List of keys from the dictionary of data of whole image
        keys_list = list(data_dict.keys())
        keys_list = keys_list[4::]

        sliced_data_dict = {
            'x': [],
            'y': [],
            'lat_km': [],
            'lon_km': [],
            'lat_deg': [],
            'lon_deg': []
        }

        coord_conv = coordConvertion()

        if lon1 > lon2:
            lon1, lon2 = lon2, lon1
        
        if lat1 < lat2:
            lat1, lat2 = lat2, lat1

        column1, line1 = coord_conv.geocoord2pixcoord(lat1, lon1)
        column2, line2 = coord_conv.geocoord2pixcoord(lat2, lon2)

        for i, j in zip(data_dict['x'], data_dict['y']):
            if i >= line1 and i <= line2:
                if j >= column1 and j <= column2:
                    x.append(data_dict['x'][index])
                    y.append(data_dict['y'][index])
                    sliced_data_dict['lat_km'].append(data_dict['lat_km'][index])
                    sliced_data_dict['lon_km'].append(data_dict['lon_km'][index])                

                    for key in keys_list:
                        if key in sliced_data_dict:
                            sliced_data_dict[key].append((data_dict[key])[index])      # type: ignore
                        else:
                            sliced_data_dict[key] = []
                            sliced_data_dict[key].append((data_dict[key])[index])      # type: ignore
            index += 1
        
        for i in range( (x[-1] - x[0]) + 1 ):
            for j in range( (y[-1] - y[0]) + 1 ):
                sliced_data_dict['x'].append(i+line1)
                sliced_data_dict['y'].append(j+column1)

        return sliced_data_dict
    

class coordConvertion:

    CFAC = -np.rad2deg(13642337) # = -781648343
    LFAC = -np.rad2deg(13642337) # = -781648343
    COFF = 1149
    LOFF = 1857
    R_POL = 6356.7523142451792 # km
    R_EQ = 6378.137 # km
    SAT_HEIGHT = 42164 # km
    SUB_LON = 0

    def pixcoord2geocoord(self, column, line):
        """
        Convert pixel coordinates (column, line) to geographical coordinates (latitude, longtitude)
        """
        
        x = (1 / (2**(-16))) * (column - self.COFF) / self.CFAC
        y = (1 / (2**(-16))) * (line - self.LOFF) / self.LFAC

        sd = np.sqrt(abs((self.SAT_HEIGHT * np.cos(x) * np.cos(y))**2 - (np.cos(y)**2 + 1.006803 *np.sin(y)**2) * 1737121856))
        sn = (self.SAT_HEIGHT * np.cos(x) * np.cos(y) - sd) / (np.cos(y)**2 + 1.006803 * np.sin(y)**2)

        s1 = 42164 - sn * np.cos(x) * np.cos(y)
        s2 = sn * np.sin(x) * np.cos(y)
        s3 = -sn * np.sin(y) 
        sxy = np.sqrt(s1**2 + s2**2)

        lon_rad = np.arctan(s2 / s1) + self.SUB_LON
        lat_rad = np.arctan(1.006803 * s3 / sxy)

        lat_deg = (lat_rad * 180) / np.pi
        lon_deg = (lon_rad * 180) / np.pi

        return -lat_deg, -lon_deg # Line, Column


    def geocoord2pixcoord(self, lat_deg, lon_deg):
        """
        Convert geographical coordinates (latitude, longtitude) to pixel coordinates (column, line)
        """
        
        lat_rad = (lat_deg * np.pi) / 180
        lon_rad = (lon_deg * np.pi) / 180
        
        c_lat = np.arctan(0.993243 * np.tan(lat_rad))

        x1 = 0.00675701 * np.cos(c_lat)**2
        rl = self.R_POL / np.sqrt(1 - x1)

        r1 = self.SAT_HEIGHT - rl * np.cos(c_lat) * np.cos(lon_rad - self.SUB_LON)
        r2 = -rl * np.cos(c_lat) * np.sin(lon_rad - self.SUB_LON)
        r3 = rl * np.sin(c_lat)

        rn = np.sqrt(r1 * r1 + r2 * r2 + r3 * r3)
        
        xx = np.arctan(-r2 / r1)
        yy = np.arcsin(-r3 / rn)

        column = self.COFF + int(xx * 2**(-16) * -self.CFAC)
        line = self.LOFF + int(yy * 2**(-16) * -self.LFAC)

        return column, line