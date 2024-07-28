# initialization
import os
from utils import helper
from pandas import DataFrame, read_csv
from matplotlib import pyplot as plt


def exec_main():

    print("Power Calculator")

    #### User Input
    # input parameters
    folder_path = helper.get_valid_str("Input folder path: ")
    voltage_file_prefix = helper.get_valid_str("Input Prefix name for Voltage: ")
    current_file_prefix = helper.get_valid_str("Input Prefix name for Current: ")
    power_file_prefix = helper.get_valid_str("Input Prefix name for Power: ")
    f_cutoff = helper.get_valid_int("Input cutoff Freq of LPF: ")
    f_downsample =helper.get_valid_int("Input Downsampling Freq: ")
    smoothing_constant = helper.get_valid_float("Input smoothing constant: ")


    #### Loading the files
    path = os.chdir(folder_path)
    files_in_dir = os.listdir(path)


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
        c_file = helper.get_match_current(v_lastchr, current_files)
        
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
        voltage = read_csv(voltage_order[x])
        current = read_csv(current_order[x])
        
        # get the last character of the filename for saving the power data later
        fn = helper.get_last_chr(voltage_order[x])
        

        #### Butterworth LPF applied to voltage ####
        # parameter of low pass filter for voltage
        fs_v = len(voltage.iloc[:, 1])/voltage.iloc[-1, 0]  # fs = number of samples/time

        # apply the filter to the signal
        filtered_voltage, w_v, h_v = helper.LP_butter_1st(voltage, f_cutoff, fs_v)
        
        
        #### Butterworth LPF applied to current ####
        # parameter of low pass filter for current
        fs_c = len(current.iloc[:, 1])/current.iloc[-1, 0]  # fs = number of samples/time

        # apply the filter to the signal
        filtered_current, w_c, h_c = helper.LP_butter_1st(current, f_cutoff, fs_c)
        
        
        
        #### Downsampling the Data ####
        D_filt_volt_df, D_filt_cur_df = helper.downsample(f_downsample, fs_v, filtered_voltage, voltage, fs_c, filtered_current, current)


        #### Calculating Power ####
        # multiply voltage and current
        power_df = DataFrame(D_filt_volt_df['filt_volt'] * D_filt_cur_df['filt_cur'])
        power_df.insert(0, 'time', D_filt_volt_df.iloc[:, 0])
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
        plt.plot(power_df.iloc[:,0], power_df.iloc[:, 2], label="Smoothed Power")
        plt.legend(loc='best')
        plt.xlabel('Time (s)')
        plt.ylabel('Power (W)')
        plt.grid(True)

        # save plot
        print("Saving plot...")
        plot_filename = helper.get_filename(folder_path, power_file_prefix, fn, 'png') #(path, prefix, fn, extension)
        plt.title (f'Calculated Power ({plot_filename})')
        plt.savefig(plot_filename, dpi=300)
        print(f"Power Plot saved as {plot_filename}")

        plt.show()

        #save csv
        print("Saving csv file...")
        csv_filename = helper.get_filename(folder_path, power_file_prefix, fn, 'csv') #(path, prefix, fn, extension)
        power_df.to_csv(csv_filename)
        print(f"Power Data saved as {csv_filename}")