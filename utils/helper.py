# initialization
from os.path import exists
from pandas import DataFrame
from scipy import signal


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
def downsample(f_downsample, fs_v, filt_volt, voltage, fs_c, filt_cur, current):
    # f_downsample - downsampling freq
    # fs_v - sampling rate of voltage
    # filt_volt - list of filtered voltage
    # voltage - raw voltage
    # fs_c - sampling rate of current
    # filt_cur - list of filtered current
    # current - raw current

    fs_vd = int(fs_v)/f_downsample
    fs_cd = int(fs_c)/f_downsample

    # downsampling the voltage
    filt_volt_df = DataFrame(filt_volt)
    filt_volt_df.insert(0, 'time', voltage.iloc[:,0])
    filt_volt_df.rename(columns={0:'filt_volt'}, inplace=True)
    d_filt_volt_df = filt_volt_df.iloc[::int(fs_vd)]

    # downsampling the current
    filt_cur_df = DataFrame(filt_cur)
    filt_cur_df.insert(0, 'time', current.iloc[:,0])
    filt_cur_df.rename(columns={0:'filt_cur'}, inplace=True)
    d_filt_cur_df = filt_cur_df.iloc[::int(fs_cd)]

    return d_filt_volt_df, d_filt_cur_df


# get valid string input
def get_valid_str(prompt):

    while True:
        user_input = input(prompt)
        if user_input == "":
            print("Invalid path! Please enter non-empty string.")

        else:
            return user_input
        
# get valid integer input
def get_valid_int(prompt):

    while True:
        try:
            user_input = input(prompt)
            value = int(user_input)
            if value == 0:
                print("Invalid input! Please enter an non-zero integer.")
            else:
                return value
        
        except ValueError:
            print("Invalid input! Please enter an integer.")


# get valid float input
def get_valid_float(prompt):

    while True:
        try:
            user_input = input(prompt)
            value = float(user_input)
            return value
        
        except ValueError:
            print("Invalid input! Please enter an float number.")


# overwrite query when the filename already exists
def get_filename(path, prefix, fn, extension):
    while True:
        filename = f'{prefix}{fn}.{extension}'
        if exists(filename):
            overwrite = input(f"{filename} file already exists. Do you want to overwrite it? (y/n) ")
            if overwrite in ['y','yes','YES', 'Yes', 'Y']:
                return filename
            else:
                new_fn = input("Enter new filename w/o extension: ")
                new_filename = f'{new_fn}.{extension}'
                return new_filename
            
        else:
            return filename


