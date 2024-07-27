# initialization
import os
import pandas as pd
from scipy import signal
from matplotlib import pyplot as plt

#### Functions
# function that finds the current file that matches with the voltage file
def get_match_current(target_last_chr, list_of_files):
    # target_last_chr - this is the last characters in the voltage file
    # list_of_files - this is the list of current files that we will be looping over
    
    # returns
        # match_file - file that matches with the voltage file
        # last_chr - last characters of the current file
    
    for x in list_of_files:
        length = len(x)
        last_chr = x[2:length]
        
        if last_chr == target_last_chr:
            return x           
             
        
# get filename's last character
def get_last_chr(file):
    length = len(file)
    last_chr = file[2:(length-4)]
    
    return last_chr


# a lowpass first order butterworth filter
def LP_butter_1st(data, cutoff, fs):
    
    # data - signal you want to filter; should be a dataframe and located on 2nd column of the df
    # cutoff - desired cutoff freq of the filter
    # fs - sampling rate 
    
    b, a = signal.butter(1, int(cutoff), btype='low', output='ba', fs=fs)
    w, h = signal.freqs(b, a)                           # if you want to plot the freq response of the filter
    
    # apply the filter to the signal
    filt_sig= signal.lfilter(b, a, data.iloc[:,1])
    
    return filt_sig, w, h

# downsampling
def downsample(f_downsample, fs_v, filt_volt, fs_c, filt_cur):
    # f_downsample - downsampling freq
    # fs_v - sampling rate of voltage
    # filt_volt - list of filtered voltage
    # fs_c - sampling rate of current
    # filt_cur - list of filtered current

    fs_vd = int(fs_v)/f_downsample
    fs_cd = int(fs_c)/f_downsample

    # downsampling the voltage
    filt_volt_df = pd.DataFrame(filt_volt)
    filt_volt_df.insert(0, 'time', voltage.iloc[:,0])
    filt_volt_df.rename(columns={0:'filt_volt'}, inplace=True)
    d_filt_volt_df = filt_volt_df.iloc[::int(fs_vd)]

    # downsampling the current
    filt_cur_df = pd.DataFrame(filt_cur)
    filt_cur_df.insert(0, 'time', current.iloc[:,0])
    filt_cur_df.rename(columns={0:'filt_cur'}, inplace=True)
    d_filt_cur_df = filt_cur_df.iloc[::int(fs_cd)]

    return d_filt_volt_df, d_filt_cur_df
