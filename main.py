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


#### User Input
# input parameters
folder_path = input("Input folder path: ")
voltage_file_prefix = input("Input Prefix name for Voltage: ")
current_file_prefix = input("Input Prefix name for Current: ")
power_file_prefix = input("Input Prefix name for Power: ")
f_cutoff = int(input("Input cutoff Freq of LPF: "))
f_downsample = int(input("Input Downsampling Freq: "))
smoothing_constant = float(input("Input smoothing constant: "))


#### Loading the files
path = os.chdir(folder_path)
files_in_dir= os.listdir(path)


# Identifying filename prefixes, sorting
voltage_files = []
current_files = []
power_files = []

for file in files_in_dir:
    
    prefix = file[:2]

    if prefix == voltage_file_prefix:
        voltage_files.append(file)
        
    elif prefix == current_file_prefix:
        current_files.append(file)
    
    elif prefix == power_file_prefix:
        power_files.append(file)


#### Matching the voltage and current files
current_order = []               # a container for the current files that is in the correct order as to the voltage_files
voltage_order = []               # a container for the voltage files that has a match

for file in voltage_files:       # loop into the voltage_files
    
    # get the last characters of the voltage filename
    vlen = len(file)
    v_lastchr = file[2:vlen]
    v_file = file
    
    # get the match current filename, then store it in a list
    c_file = get_match_current(v_lastchr, current_files)
    
    if c_file != None:
        voltage_order.append(v_file)
        current_order.append(c_file)

# print out the final voltage & current files in the correct order
print('Detected Voltage files with matching current files: \n', voltage_order)
print('Detected Current files with matching voltage files: \n', current_order)
    


####Processing the files
#looping on the matching voltage & current files, loop will mainly refer to the voltage file
for x in range(0, len(voltage_order)):
    
    # import the csv file
    voltage = pd.read_csv(voltage_order[x])
    current = pd.read_csv(current_order[x])
    
    # get the last character of the filename for saving the power data later
    fn = get_last_chr(voltage_order[x])
    

    #### Butterworth LPF applied to voltage ####
    # parameter of low pass filter for voltage
    fs_v = len(voltage.iloc[:, 1])/voltage.iloc[-1, 0]  # fs = number of samples/time

    # apply the filter to the signal
    filtered_voltage, w_v, h_v = LP_butter_1st(voltage, f_cutoff, fs_v)
    
    
    
    #### Butterworth LPF applied to current ####
    # parameter of low pass filter for current
    fs_c = len(current.iloc[:, 1])/current.iloc[-1, 0]  # fs = number of samples/time

    # apply the filter to the signal
    filtered_current, w_c, h_c = LP_butter_1st(current, f_cutoff, fs_c)
    
    
    
    #### Downsampling the Data ####
    # downsampling parameter
    fs_vd = int(fs_v)/f_downsample
    fs_cd = int(fs_c)/f_downsample

    # downsampling the voltage
    filt_volt_df = pd.DataFrame(filtered_voltage)
    filt_volt_df.insert(0, 'time', voltage.iloc[:,0])
    filt_volt_df.rename(columns={0:'filt_volt'}, inplace=True)
    d_filt_volt_df = filt_volt_df.iloc[::int(fs_vd)]

    # downsampling the current
    filt_cur_df = pd.DataFrame(filtered_current)
    filt_cur_df.insert(0, 'time', current.iloc[:,0])
    filt_cur_df.rename(columns={0:'filt_cur'}, inplace=True)
    d_filt_cur_df = filt_cur_df.iloc[::int(fs_cd)]


    #### Calculating Power ####
    # multiply voltage and current
    power_df = pd.DataFrame(d_filt_volt_df['filt_volt'] * d_filt_cur_df['filt_cur'])
    power_df.insert(0, 'time', d_filt_volt_df.iloc[:, 0])
    power_df.rename(columns={0:'power'}, inplace=True)

    
    #### Smoothed Power ####
    # initialize
    smoothed_pwr = [power_df.iloc[0, 1]]

    for i in range(1, len(power_df)):
        new_value = (smoothing_constant * smoothed_pwr[-1]) + (1 - smoothing_constant) * power_df.iloc[i, 1]
        smoothed_pwr.append(new_value)

    # Assign the smoothed power values back to the DataFrame
    power_df['smoothed_pwr'] = smoothed_pwr

    
    #### Output ####
    # plot raw power and smoothed power
    plt.clf()
    plt.plot(power_df.iloc[:,0], power_df.iloc[:, 1], label="Raw Power")
    plt.plot(power_df.iloc[:,0], power_df.iloc[:, 2], label="Smoothened Power")
    plt.legend(loc='best')
    plt.xlabel('time (s)')
    plt.ylabel('power (W)')
    plt.title (f'Calculated Power ({power_file_prefix}{fn})')
    plt.grid(True)

    # save plot
    plot_filename = f'{power_file_prefix}{fn}.png'
    plt.savefig(plot_filename, dpi=300)
    print(f"Power Plot saved as {plot_filename}")

    plt.show()

    #save csv
    csv_filename = f'{power_file_prefix}{ fn}.csv'
    power_df.to_csv(csv_filename)
    print(f"Power Data saved as {csv_filename}")

    return "Done Processing All the Raw Data."
