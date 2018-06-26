#Adrian Swartz - part of the "baby project":
#We want to ask the question:
#If given a person's name, can we know (within some confidence interval)
#what year that person was probably born?

#This program downloads the actuarial data from the SSA website
#and converts it from probability of dying that year
#to probability that person is still alive in 2017

import re
import urllib
import matplotlib.pyplot as plt


def get_actuarial_website_data():
    """ Get 2014 actuarial data acuisition from website

    This function pulls the data from the SSA website and
    returns a dictionary containing the actuarial table data
    """

    act_table_dict = {}

    #access the table on the SSA website
    website = "https://www.ssa.gov/oact/STATS/table4c6_2014.html"
    f = urllib.urlopen(website)
    page = f.read()


    #pull out data from actuarial table for 0 to 119 (age)
    for i in range(0,120):
        # i represents the age in the actuarial table
        #pull out the male death probability
        pattern = '"center">\s+' + str(i) +'</td>\s+<td>\s+(\S+)</td>' 
        pattern += '\s+<td>\s+\S+</td>' #skip the male number of lives
        pattern += '\s+<td>\s+(\S+)</td>' #pull out male life expectancy
        pattern += '\s+<td>\s+(\S+)</td>' #pull out the female death prob.
        pattern += '\s+<td>\s+\S+</td>' #skip the female number of lives
        pattern += '\s+<td>\s+(\S+)</td>' #pull out female life expectancy

        # Do the pattern search
        n_tuple = re.findall(pattern, page)

        #convert from strings to floats and reassign as a tuple in the dict
        M_dp = float(n_tuple[0][0])   #male death prob.
        M_le = float(n_tuple[0][1])   #male life expectancy
        F_dp = float(n_tuple[0][2])   #female death prob.
        F_le = float(n_tuple[0][3])   #female life expectancy
        act_table_dict[i] = (M_dp, M_le, F_dp, F_le)
        
    #print act_table_dict 
    return act_table_dict  #returns a dictionary of tuples

def dict_to_arrays(act_table_dict):
    #"array" is actually a list - i'm doing this without numpy for now
    #I am curious to test how much you can do with lists alone

    #actuarial dictionary has the form key = "age" (0 to 119)
    #and value is a tuple containting four data points:
    #[0] = male death probability (float between 0 and 1)
    #[1] = male life expectancy (float)
    #[2] = female death probability (float between 0 and 1)
    #[3] = female life expectancy (float)
    
    ages = act_table_dict.keys()  #assign ages list (0 to 119)
    M_dp = []       # intialize
    M_le = []
    F_dp = []
    F_le = []
    
    for age in ages:
        M_dp.append(act_table_dict[age][0])  #Male death probability
        M_le.append(act_table_dict[age][1])
        F_dp.append(act_table_dict[age][2])
        F_le.append(act_table_dict[age][3])

    data = []
    data.append(ages)
    data.append(M_dp)
    data.append(M_le)
    data.append(F_dp)
    data.append(F_le)

    return data # a list of lists (an array but not using numpy)



def fixed_actuarial_data(act_table_dict, years):
    """ To use death table with 1880-2017 baby names data from SSA,
    need to map 0 to 119 ages --> 2017 to 2017-119.
    Also need fill in the death probabilities for those with age >= 120.
    Then, we want to convert this to the probability of being alive.
    This should return a list of lists containing all the actuarial data
    so that it can be plotted or saved to a file
    """
    # actuarial data pulled from SSA website:
    #data[0] = ages
    #data[1] = male death probability (float between 0 and 1)
    #data[2] = male life expectancy (float)
    #data[3] = female death probability (float between 0 and 1)
    #data[4] = female life expectancy (float)

    data = dict_to_arrays(act_table_dict)
    ages = data[0]
    M_dp = data[1]
    M_le = data[2]
    F_dp = data[3]
    F_le = data[4]

    #Male data first:
    #probability of not dying that year
    M_notdead = M_dp[:]   #initialize
    for index, mdp in enumerate(M_dp):
      M_notdead[index] = 1 - mdp  


    #calculate probability alive in 2017
    M_alive_prob = M_notdead[:]     #initialize
    for index, mnd in enumerate(M_notdead):
      count = index-1
      M_alive_prob[index] = mnd
      while count > 0:
        M_alive_prob[index] *= M_notdead[count]
        count-=1
      
    #Same thing for the female data:
    F_notdead = F_dp[:]
    for index, fdp in enumerate(F_dp):
      F_notdead[index] = 1 - fdp    #probability of not dying that year

    #calculate probability alive in 2017
    F_alive_prob = F_notdead[:]
    for index, mnd in enumerate(F_notdead):
      count = index-1
      F_alive_prob[index] = mnd
      while count > 0:
        F_alive_prob[index] *= F_notdead[count]
        count-=1

    #reverse ages with zero at the max of years
    #actuary table is from 2014, but we will assume that this is
    #not so different from 2018 statistics.
    for index, age in enumerate(ages):
      ages[index] = max(years)-age

    #kill off everyone over 120 (no extrapolation) 
    i = min(ages)-1  
    while len(ages) < len(years):
      ages.append(i)
      M_alive_prob.append(0) # assume that all males over 120 years old are dead
      M_notdead.append(0)
      M_le.append(0)
      M_dp.append(1)
      F_alive_prob.append(0) # same for women
      F_notdead.append(0)
      F_le.append(0)
      F_dp.append(1)     
      i-=1
    
    adj_data = []
    #want the data counting forward from years min (to match baby names data)
    ages.reverse()
    M_dp.reverse()
    M_le.reverse()
    M_notdead.reverse()
    M_alive_prob.reverse()
    F_dp.reverse()
    F_le.reverse()
    F_notdead.reverse()
    F_alive_prob.reverse()


    
    adj_data.append(ages)
    adj_data.append(M_dp)
    adj_data.append(M_le)
    adj_data.append(M_notdead)
    adj_data.append(M_alive_prob)
    adj_data.append(F_dp)
    adj_data.append(F_le)
    adj_data.append(F_notdead)
    adj_data.append(F_alive_prob)
    
    #return a list of lists (an array but not using numpy)
    return adj_data


def write_actdata_file(fixed_data):

    ages = fixed_data[0]
    M_dp = fixed_data[1]
    M_le = fixed_data[2]
    M_notdead = fixed_data[3]
    M_alive_prob = fixed_data[4]
    F_dp = fixed_data[5]
    F_le = fixed_data[6]
    F_notdead = fixed_data[7]
    F_alive_prob = fixed_data[8]
    
    f= open("adj_act_data_2014.txt","w+")
    for index, age in enumerate(ages):
        s = str(age) + ", "
        s += str(M_dp[index]) + ", "
        s += str(M_le[index]) + ", "
        s += str(M_notdead[index]) + ", "
        s += str(M_alive_prob[index]) + ", "
        s += str(F_dp[index]) + ", "
        s += str(F_le[index]) + ", "
        s += str(F_notdead[index]) + ", "
        s += str(F_alive_prob[index]) + "\n"
        f.write(s)

    f.close()

    return None
    



def plot_actuarial_table_data(act_table_dict, years):
    
    data = dict_to_arrays(act_table_dict)
    
    ages = data[0]
    M_dp = data[1]
    M_le = data[2]
    F_dp = data[3]
    F_le = data[4]

    plt.rcParams['figure.figsize'] = [8,4]
    plt.rcParams['font.family'] = ['Times New Roman']
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['ytick.right'] = True
    plt.rcParams['ytick.direction'] = "in"
    plt.rcParams['xtick.top'] = True
    plt.rcParams['xtick.direction'] = "in"
        
    plt.plot(ages, M_dp, label="Male death probability", color="blue")
    plt.plot(ages, F_dp, label="Female death probability", color="red")

    plt.legend()
    plt.xlabel('Age in 2014')
    plt.ylabel('Probability of dying that year')
    plt.title('Actuarial Table 2014')

    #Fix y range to be 1 to 1 data on linear plot
    plt.ylim(ymin=0)
    plt.ylim(ymax=1.05)
    
    plt.show()

    return None

def main():

    years = range(1880,2018)
    
    act_dict = get_actuarial_website_data()
#    plot_actuarial_table_data(act_dict, years)

    act_data = fixed_actuarial_data(act_dict, years)
    write_actdata_file(act_data)

    #I could improve this to make it more user friendly
    #with command line inputs for plot and save
    #but I'd rather spend the time getting through the analysis




if __name__ == '__main__':
  main()
