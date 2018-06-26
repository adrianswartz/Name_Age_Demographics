#Extract all babynames and ranks from txt files downloaded from SSA website
#Extract patached actuarial data from file generated with get_actdata_2014.py
#This program takes in a single name and sex and outputs the age and st deviation


import re
import numpy as np
import matplotlib.pyplot as plt
import csv
import scipy.stats as st


def get_singlename_year(name, sex, year):
    """Given a name (string), sex ("M" or "F"), and year (integer) as input,
    opens the file in directory /names with file: "yob1999.txt",
    returns the associated number of names for that year
    """

    #identify filename for that year
    filename = "names/yob" + str(year) + ".txt"

    #open the file and search for that name and sex, extracting the number
    with open(filename) as f:
        text = f.read()
        pat = name + "," + sex + ",(\d+)"
        result = re.findall(pat, text) 

    if result == []:
        number = 0     #set number to zero if name isn't on the list
    else:
        number = int(result[0])
    return number #returns the number for that name in that year





def get_name_numbers(name, sex, years):
    """Compile the name data from SSA for a single name over a range of years

    Given a name, the sex, and a list of years,
    use the get_single_name_year() function iterated over the list of years.

    Returns a list containing the number of babies for that name from that year
    """
    data = []
    for year in years:
        number = get_singlename_year(name, sex, year)
        data.append(number)

    return data #a list of numbers







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


def calc_number_alive(name, sex, years):
    """Given a name, sex and range of years,
    calls functions which extract the number of name instances throuught years
    and which extract the actuarial information.

    Returns a list with the number expected to still be alive in 2017.
    Returned list is in same order as years.
    """

    #Get actuarial data for sex = "M" or "F"
    alive_prob = open_actuarial_data(sex, years)

    #Get baby numbers for that name and sex
    names_data = get_name_numbers(name, sex, years) #a list of numbers

    number_alive = names_data[:] #initialize, mainly for length

    for index, num in enumerate(names_data):  
      number_alive[index] = names_data[index] * alive_prob[index]

    return number_alive
  

#Need to flip number_alive vs. years data into a histogram
#in order to perform standard statistics with numpy an scipy


def analysis(number_alive, years):

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
    
      
  

def main():
    print 
    print
    name = raw_input("Please enter a name: ")
    sex = raw_input("and M or F? ")
    print
    print "Crunching the numbers. cruch, crunch, crunch, ..."
    print
    print


    years = range(1880,2018)  #let's look at all the available data

    
    number_alive = calc_number_alive(name, sex, years)

    result = analysis(number_alive,years)
    av_age = max(years) - result[0]
    med_age = max(years) - result[1]
    
    print
    print
    print "The average age for %s, %s is %0.1f." %(name, sex, av_age)
    print "The median age for %s, %s is %0.1f." %(name, sex, med_age)
    print "The std dev is %0.1f,  skewness is %0.3f, and kurtosis is %0.3f.\n\n" %(result[2], result[3], result[4])

    # Plotting
    plt.rcParams['figure.figsize'] = [7,4]
    plt.rcParams['font.family'] = ['Times New Roman']
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['ytick.right'] = True
    plt.rcParams['ytick.direction'] = "in"
    plt.rcParams['xtick.top'] = True
    plt.rcParams['xtick.direction'] = "in"


    names_data = get_name_numbers(name, sex, years) #a list of numbers


    plt.plot(years, number_alive ,label="Number likely to be alive", color="blue")
    plt.plot(years, names_data,label="Total number born", color="red")
    plt.axvline(x=result[0], label="mean", color = "black")
    plt.axvline(x=result[1], label="median", color = "orange")
    left = result[0]-result[2]
    right = result[0]+result[2]
    plt.axvline(x=left, label="std. dev.", color = "purple", linestyle='--')
    plt.axvline(x=right, color = "purple", linestyle='--')
    

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Counts')
    plt.title('Age distribution for "%s, %s" ' %(name, sex))
    plt.ylim(ymin=0)
    y_max = 1.1*max(max(number_alive), max(names_data))
    plt.ylim(ymax=y_max)
    plt.show()



if __name__ == '__main__':
  main()
