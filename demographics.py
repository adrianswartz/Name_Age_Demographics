#Demographics analysis based on SSA baby names
#between 1880 and 2017 and 2014 actuarial table.
#Results only include those who registered with SSA at birth

# This program does the following:
# 1) Imports all SSA baby names from files into a dictionary.
#    Two dictionaries (M and F) are used throughout the program.
# 2) Identifies the number of unique names in the SSA database 
#    and creates a dictionary of all unique names
# 3) Patches the SSA names dictionaries to fill in missing data.
# 4) Imports the 2014 actuarial table generated using get_actdata_2014.py
#    and calculates the number expected to be alive in 2017.
# 5) Asks the user for a threshold cutoff value.
#    Only names with a total number of people ever born
#    exceeding the threshold will be looked at.  
#    In the future, this step could be done before patching the dictionary to save time
# 6) The program then proceeds with the "Main analysis" which examines all
#    above threshold names and runs the statistics for those expected to be alive.
# 7) These names are then placed in to different demographics
#    based on their median value
# 8) This set is filtered for narrow distributions (std dev < 15 years)
#    and which can be well described by a single peak (kurtosis > 0)
# 9) This subset of names in each demographic are sorted by rank and printed to the screen.

#Adrian Swartz June 2018

import re
import numpy as np
import matplotlib.pyplot as plt
import csv
import scipy.stats as st



def get_allnames_year(year):
    """Given an integer year as input, opens the file in directory /names with file: "yob1999.txt",
    returns a dict tuple (Female, Male) where the keywords are the name
    and the value is the associated number of names for that year
    """
    #initialize Male and Female dictionaries
    singleyear_F_dict = {}
    singleyear_M_dict = {}

    #identify filename for that year
    filename = "names/yob" + str(year) + ".txt"

    #initialize counter for number of males and females born that year
    count_F = 0
    count_M = 0

    #read file and separate into two dictionaries by sex
    with open(filename) as f:
        for i, line in enumerate(f):
            #print("Line {}: {}".format(i, line))
            n_tuple = re.findall(r'(\w+),(\w),(\d+)', line)

            name = n_tuple[0][0]
            sex = n_tuple[0][1]
            number = int(n_tuple[0][2])
            
            if sex == "F":
                singleyear_F_dict[name] = number
                count_F += 1
            else:
                singleyear_M_dict[name] = number
                count_M += 1
            
#    print
#    print 'From %4d\n' %year
#    print "Number of lines: ", i
#    print "Number of M names: ", count_M
#    print "Number of F names: ", count_F
#    print
            
    #Return a tuple of two dictionaries for the male and female names
    return (singleyear_M_dict, singleyear_F_dict)

def build_allyears_dict(years):
    """Given a list of years (integers) as input, calls the
    get_allnames_year(year) function. 
    """
    
    #initialize Male and Female dictionaries
    years_F_dict = {}
    years_M_dict = {}
    for year in years:
        singleyear_M_dict, singleyear_F_dict = get_allnames_year(year)
        years_M_dict[year] = singleyear_M_dict
        years_F_dict[year] = singleyear_F_dict
    
  
    return (years_M_dict, years_F_dict)


#The dictionary has holes, which need to be filled
#There are names which do not appear in all years,
#therefore calling the dict for a single name over all years
#would generate a list of different lengths for each name
#To patch the dictionary, it helps to know every name:

def extract_allnames(years, years_dict):

    names = {} #initialize dict
    #faster to access than a list and solves the duplicates problem
    #if duplicates included, there can be over 1 million entries
    #should only be about 67 thousand total female names in the SSA data

    for year in years:
        for name in years_dict[year].keys():
            names[name] = name
                
    return names #a dictionary of all uniqe names in SSA baby data

#Now I can fill the holes for years which are missing data for that name

def patch_years_dict(years_dict, names_dict, years):
    for name in names_dict:
        for year in years_dict:
            if name not in years_dict[year]:
                years_dict[year][name] = 0

    return years_dict




def extract_name_numbers(name, years, patched_dict):
    numbers = [] #initialize
    for year in years:
        numbers.append(patched_dict[year][name])

    return numbers


def quick_sum(name, years, patched_dict):

    total = 0
    for year in years:
        total += patched_dict[year][name]

    return total


def open_actuarial_data(sex, years):
    """ Opens the adjusted 2014 actuarial table.
    Imports only the data spanning the input years (list of integers)
    Imports only the probability to be alive in 2017 for sex ="M" or "F".
    The actuarial file has years, M_dp, M_le, M_notdead, M_alive_prob, F_dp, ...
    """
    filename = "adj_act_data_2014.txt"  #file generated using get_actdata_2014.py

    all_data = []

    with open(filename) as f:
      text = csv.reader(f)   
      for line in text:
        all_data.append(line)

    #I discovered the csv reader after I had already
    #written the get_singlename_year() function
    
    alive_prob = []
    shift = min(years) - 1880
    for index, item in enumerate(years):
      index +=shift
      if sex == "M":
        #Male alive prob. data is stored in column 4 of actuary file
        alive_prob.append(float(all_data[index][4]))  
      elif sex == "F":
        #Female alive prob. data is stored in column 8 of actuary file
        alive_prob.append(float(all_data[index][8]))
      else:
        print "Neither F or M chosen"
        return False


    return alive_prob  #returns the probability of being alive in 2017



def get_stats(number_alive, years):

    data = []  # convert number_alive vs years into a histogram for stats analysis
    for index, value in enumerate(number_alive):
        i = 0
        while i < value:
          data.append(years[index])
          i+=1

    mean = np.mean(data)
    median = np.median(data)
    stddev = np.std(data)
    sk = st.skew(data)
    kurt = st.kurtosis(data)

#    print st.describe(data)
    
    return (mean, median, stddev, sk, kurt) #a tuple


# This is already a more powerful way to handle the data.
# From this point, I can easily move forward with demographics analysis.
# Or, I could easily do the same thing as the names_age.py program
# i.e. with names_age.py, the functionality was reduced. I am learning.





def demographics_analysis(results_dict):

    demo_groups = [] #dicts will go in here
    gen_z = {}
    millennials = {}
    gen_x = {}
    baby_boomers = {}
    silent_gen = {}
    greatest_gen = {}
    greatest_gen = {}
    dead_gen = {}

    
    # start with simple demographics splitting by median
    # not worrying about std dev, skewness, or kurtosis.
    for name in results_dict:
        median_age = results_dict[name][1]
        if median_age > 2000 :
            gen_z[name] = results_dict[name]
        elif median_age > 1980: 
            millennials[name] = results_dict[name]
        elif median_age > 1964:
            gen_x[name] = results_dict[name]
        elif median_age > 1944:
            baby_boomers[name] = results_dict[name]
        elif median_age > 1926:
            silent_gen[name] = results_dict[name]
        elif median_age > 1900:
            greatest_gen[name] = results_dict[name]
        else:
            dead_gen[name] = results_dict[name]

    demo_groups.append(gen_z)
    demo_groups.append(millennials)
    demo_groups.append(gen_x)
    demo_groups.append(baby_boomers)
    demo_groups.append(silent_gen)
    demo_groups.append(greatest_gen)
    demo_groups.append(dead_gen)

    return demo_groups

def demographics_filter(demo_groups):
    #demo_groups is a list of dicts
    filtered_demo_groups = []
    
    #filter by two criteraia:
    #A resonably tight standard deviation (not too much statistical spread)
    #and, most importantly, a kurtosis > 0.
    #(meaning there's one well defined peak that isn't too wide)
    
    for demo_dict in demo_groups:
        filtered_dict = {}
        for name in demo_dict:
            median_age = demo_dict[name][1]
            std_dev = demo_dict[name][2]
            kt = demo_dict[name][4]
        
            if std_dev < 15 and kt > 0:
                filtered_dict[name] = demo_dict[name]
        filtered_demo_groups.append(filtered_dict)
 

    return filtered_demo_groups
        
def Last(a):
  return a[-1]
    
def main():

    years = range(1880,2018)

    print
    print "Reading baby names data from SSA files ... ... ..."
    print

    #create Male, Female dictionaries from raw data in SSA baby files
    years_M_dict, years_F_dict = build_allyears_dict(years)

    print
    print "... done reading files!"
    print

    print
    print "Extract all unique names..."
    print

 
    #create dictionary containing all unique names in SSA baby names database
    names_F = extract_allnames(years, years_F_dict)
    names_M = extract_allnames(years, years_M_dict)

    print    
    print "Total number of unique Female names: ", len(names_F) 
    print "Total number of unique Male names: ", len(names_M)
    print

    print
    print "Patching holes in the dictionary..."
    print

    #Patch the dictionaries with zeros
    patched_F_dict = patch_years_dict(years_F_dict, names_F, years)
    patched_M_dict = patch_years_dict(years_M_dict, names_M, years)

    print
    print "... patched!"
    print

    print
    print "Compile actuarial tables..."
    print

    alive_prob_F = open_actuarial_data("F", years)
    alive_prob_M = open_actuarial_data("M", years)

    print
    print "... done!"
    print

    
    print "Minimum number of people with that name over time."
    print "(Threshold value, i.e. 400000)"
    threshold = raw_input("Please enter a number: " )
    threshold = int(threshold)
    count = 0
    results_dict_F = {} #initialize
    
    print
    print "Begin analysis of all Female names with minimum %d total instances" %threshold
    print "... takes about 1 min, please be patient ..."
    
    #Calculate number_alive using the actuarial table
    #Then get the statistics using the get_stats function
    for name in names_F:
        sex = "F"
        total = quick_sum(name, years, patched_F_dict)
        if total > threshold:
#            print name, total
            count +=1
            #Get baby numbers for name and sex="F"
            name_data = extract_name_numbers(name, years, patched_F_dict)
        

            number_alive = name_data[:] #initialize, mainly for length
            for index, num in enumerate(name_data):  
                number_alive[index] = name_data[index] * alive_prob_F[index]


            
            mean, median, stddev, sk, kurt = get_stats(number_alive, years)
            results_dict_F[name] = (mean, median, stddev, sk, kurt, total)
    

    print
    print "Number of Female names exceeding %d throughout history: %d" %(threshold, count)

    count = 0
    results_dict_M = {} #initialize
    
    print
    print "Begin analysis of all Male names with minimum %d total instances" %threshold
    print "... takes about 1 min, please be patient ..."
    
    for name in names_M:
        sex = "M"
        total = quick_sum(name, years, patched_M_dict)
        if total > threshold:
#            print name, total
            count +=1
            #Get baby numbers for name and sex="M"
            name_data = extract_name_numbers(name, years, patched_M_dict)
        

            number_alive = name_data[:] #initialize, mainly for length
            for index, num in enumerate(name_data):  
                number_alive[index] = name_data[index] * alive_prob_M[index]


            
            mean, median, stddev, sk, kurt = get_stats(number_alive, years)
            results_dict_M[name] = (mean, median, stddev, sk, kurt, total)
        




    print
    print "Number of Male names exceeding %d throughout history: %d" %(threshold, count)
    print
    print "\033[1;31mPrimary analysis Complete! Yay!\033[1;m"

    demo_groups_F = demographics_analysis(results_dict_F)
    demo_groups_M = demographics_analysis(results_dict_M)
    # This list of dicts has all the information we are looking for!
    # Each list represents a demographic containting a dictionary of
    # names with associated (mean, median, stddev, skewness, and kurtosis)
    # The subset of names in these demographics are filtered by two concepts:
    # 1) Popularity - the threshold value
    # 2) Likelyhood to still be alive in 2017


    filtered_groups_F = demographics_filter(demo_groups_F)
    filtered_groups_M = demographics_filter(demo_groups_M)
    # The subset of names in these demographics are filtered an additional two concepts:
    # 1) narrow distribution of names - std_dev < 15 years
    # 2) AND best described by one peak, kurtosis > 0.

    print
    print "Filter demographics for those with a tight distribution."
    print "Standard deviation < 15 years and Kurtosis > 0."
    print "Filtered results: "
    print
    print "Number of characteristic names for each demographic:"
    print "Female: "
    print "Gen. Z: %d, Millennials: %d, Gen X: %d, Baby Boomers:  %d" %(len(filtered_groups_F[0]), len(filtered_groups_F[1]), len(filtered_groups_F[2]), len(filtered_groups_F[3]))
    print "Silent Gen.: %d, Greatest Gen: %d, Dead Gen.: %d" %(len(filtered_groups_F[4]), len(filtered_groups_F[5]), len(filtered_groups_F[6]))
    print
    print "Male: "
    print "Gen. Z: %d, Millennials: %d, Gen X: %d, Baby Boomers:  %d" %(len(filtered_groups_M[0]), len(filtered_groups_M[1]), len(filtered_groups_M[2]), len(filtered_groups_M[3]))
    print "Silent Gen.: %d, Greatest Gen: %d, Dead Gen.: %d" %(len(filtered_groups_M[4]), len(filtered_groups_M[5]), len(filtered_groups_M[6]))


    ##Print the results
    i=0
    while i < len(filtered_groups_F):
        print
        print
        if i==0:
            print "\033[1;31mCharacteristic Gen. Z names!\033[1;m"
        elif i==1:
            print "\033[1;31mCharacteristic Millennial names!\033[1;m"
        elif i==2:
            print "\033[1;31mCharacteristic Gen. X names!\033[1;m"
        elif i==3:
            print "\033[1;31mCharacteristic Baby Boomer names!\033[1;m"
        elif i==4:
            print "\033[1;31mCharacteristic Silent Gen. names!\033[1;m"
        elif i==5:
            print "\033[1;31mCharacteristic Greatest Gen. names!\033[1;m"
        elif i==6:
            print "\033[1;31mCharacteristic Dead Gen. names!\033[1;m"


        print "Name, Sex, Age, number alive today"
        rank = 1
        for name, value in sorted(filtered_groups_F[i].items(), key=lambda x: x[1][-1], reverse=True):
            sex = 'F'
            age = max(years) - int(value[0])
            print '%d. %s, %s, %d, %d' %(rank, name, sex, age, value[-1])
            rank +=1
        if sorted(filtered_groups_F[i].items()) == []:
            print 'F: NONE'
            
        print 
        rank = 1
        for name, value in sorted(filtered_groups_M[i].items(), key=lambda x: x[1][-1], reverse=True):
            sex = 'M'
            age = max(years) - int(value[0])
            print '%d. %s, %s, %d, %d' %(rank, name, sex, age, value[-1])
            rank +=1
        if sorted(filtered_groups_M[i].items()) == []:
            print 'M: NONE'
        i+=1
        if i > 10:
            return None
    


if __name__ == '__main__':
  main()
