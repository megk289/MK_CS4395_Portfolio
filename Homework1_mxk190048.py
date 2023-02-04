# Meghana Kambhampati
# MXK190048
# CS 4395.001
# Portfolio 1: Text Processing with Python
#   This program takes in an Excel file for processing.
# The file holds a Person's information, which is to be
# read and displayed in a more organized manner. The first name,
# last name, and middle initial of each person should be capitalized.
# The person's id and phone number should be in a standardized
# format. This information is then stored in a dict and can be displayed.

import pickle
import re
import sys


''' 
Opens the input file with Person 
information and splits it into tokens.

Args:
    inputfile: input excel file with person details
    
Returns: 
    file information split into tokens in a list
'''


def open_and_setup_tokens(inputfile):
    with open(inputfile, "r") as f:
        text = f.readlines()[1:]
    return [line.split(',') for line in text]


''' 
Create a dict for Person based on id

Args:
    inputfile: input excel file with person details

Returns: 
    the dict for the Person class using id
'''


def create_dict(inputfile):
    person_dict = dict()
    for tokens in open_and_setup_tokens(inputfile):
        person = Person(*tokens)
        
        # add person info to dict if it is not already there
        if person.id not in person_dict:
            person_dict[person.id] = person
        else:
            print("There cannot be multiple employees with the same id.")
    return person_dict


class Person:
    def __init__(self, last, first, mi, id, phone):
        self.last = last.upper()
        self.first = first.upper()

        if mi:
            self.mi = mi.upper()
        else:
            self.mi = 'X'

        self.id = id
        self.check_id_format()

        self.phone = phone
        self.check_phone_format()

    ''' 
    Displays the information of a Person.
    '''

    def display(self):
        print('\n\tEmployee id: ', self.id)
        print('\n\t\t', self.first, self.mi, self.last)
        print('\n\t\t', self.phone)

    ''' 
    Checks to make sure that the id is in 
    the correct format. If it is not, an error message 
    asking for it to be re-entered is sent to the user

    Returns: 
        nothing or an error message and the new, correct id
    '''

    def check_id_format(self):
        if re.search('[A-Z]{2}[0-9]{4}', self.id) is None:
            print('\nID invalid: ', self.id)
            print('\nID is two letters followed by 4 digits')
            new_id = input('Please enter a valid id: ')
            self.id = new_id
            return new_id

    ''' 
    Checks to make sure that the phone number is in 
    the correct format. If it is not, an error message 
    asking for it to be re-entered is sent to the user
    
    Returns: 
        nothing or an error message and the new, correct phone number
    '''

    def check_phone_format(self):
        if re.search('[0-9]{3}-[0-9]{3}-[0-9]{4}', self.phone) is None:
            print('\nPhone number invalid: ', self.phone)
            new_phone = input('\nPlease enter phone number in the form xxx-xxx-xxxx: ')
            self.phone = new_phone
            return new_phone


def main():
    # check for data file
    if len(sys.argv) < 2:
        print('ERROR: No data file provided')
        return
    else:
        inputfile = sys.argv[1] # data file
        person_dict = create_dict(inputfile)
        
        # pickle file 
        pickle.dump(person_dict, open('dict.p', 'wb'))
        dict_in = pickle.load(open('dict.p', 'rb'))
        
        #display dict values
        print('\n\nEmployee List:\n')
        for person in person_dict.values():
            person.display()
        return person_dict

if __name__ == '__main__':
    main()
