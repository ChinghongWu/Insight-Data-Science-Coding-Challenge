#!/usr/bin/env python3
# h1b_statistics.py
# -*- coding: utf-8 -*-
# Author: Prudhvi

"""
h1b_statistics.py outputs two files containing top ten occupations and states
based on number of certified applications of h1b. Given input file separated
by ';', it counts the number of certified applications and stores the
information in a dictionary which is sorted to provide the top results.
"""

# Import sys module to use command line arguments.
import sys

# Initialize global variables and data structures.

# Initialize global dictionaries.
occupations_dictionary = {}
states_dictionary = {}

# Initialize global variables.
state_column_index = -1
status_column_index = -1
occupation_name_index = -1
occupation_code_index = -1
total_certified_applications_number = 0

# Initialize constant headers.
TOP_OCCUPATIONS_FILE_HEADER = ('TOP_OCCUPATIONS;'
                               'NUMBER_CERTIFIED_APPLICATIONS;'
                               'PERCENTAGE\n')
TOP_STATES_FILE_HEADER = ('TOP_STATES;'
                          'NUMBER_CERTIFIED_APPLICATIONS;'
                          'PERCENTAGE\n')


def infer_schema(header, separator):
    """
    Takes inputs: header(string) and separator(string).
    Captures the required columns' information, i.e., their indexes.
    """
    # Access global variables for modification.
    global state_column_index, status_column_index, occupation_name_index, occupation_code_index
    columns = header.split(separator)

    for column in columns:
        if ('STATUS' in column.upper()):
            # case status column
            status_column_index = columns.index(column)

        if ('SOC_CODE' in column.upper()):
            # soc code column
            occupation_code_index = columns.index(column)

        if ('SOC_NAME' in column.upper()
                or 'SOC_TITLE' in column.upper()):
            # soc name column
            occupation_name_index = columns.index(column)

        if ('LCA_CASE_WORKLOC1_STATE' in column.upper()
                or 'WORKSITE_STATE' in column.upper()
                or 'JOB_INFO_WORK_STATE' in column.upper()):
            # work location state column
            state_column_index = columns.index(column)


def custom_split(row, separator):
    """
    Takes inputs: row(string) and separator(string).

    Splits the string on occurence of separator in the string,
    with exception when separator is in between double quotations("").

    This method is used to parse the data correctly, mapping data
    to the right columns in cases when data has separator(';') in
    a single column.

    example: "1811 WEST DIEHL RD; SUITE #400" belongs
    to one column(address) but normal split would split on semicolon
    inside this column leading to incorrect data parsing.

    Returns a list of columns' data.
    """
    # Initialize local variables.
    list_of_columns = []
    column = ''
    dont_split = False

    for character in row:
        if (character != separator):
            if (character == '"' and not dont_split):
                # reached opening double quotation mark.
                dont_split = True
                continue            # to skip the quotation mark in the result.
            else:
                # reached closing double quotation mark.
                dont_split = False
                continue            # to skip the quotation mark in the result.
            column = column + character

        else:
            # reached separator,
            # check if this separator is between double quoatations.
            if (dont_split):
                # separator inside double quotations, don't split.
                column = column + character
            else:
                # regular separator, split.
                list_of_columns.append(column)   # add column data to list.
                column = ''         # reset local variable.
    list_of_columns.append(column)  # append the last column data.
    return list_of_columns


def clean_occupation_name(columns):
    """
    Takes input: list of columns.

    Some of the data rows have &AMP; in the occupation name,
    this method cleans by removing the AMP; from the name, attributing
    to more accurate counts.

    example: Software developer, Applications R&AMP;D will become
    Software developer, Applications R&D which is more intuitive
    and provides more accurate counting.
    """
    if ('&AMP;' in columns[occupation_name_index].upper()):
        columns[occupation_name_index] = columns[occupation_name_index].replace('AMP;',
                                                                                '')
    return columns


def clean_occupation_code(columns):
    """
    Takes input: list of columns.

    Some of the data rows donot correspond to the correct format
    of SOC_CODE, this method recovers any such incorrect format data
    that can be recovered (converted to correct format).

    Correct format of SOC code is dd-dddd, where d is a digit.
    Case1: Few rows have all digits in place but instead of the hyphen(-), they
    have some other character.
    example1: 13.1081 instead of 13-1081.
    example2: 25/1071 instead of 25-1071.

    Case2: Few rows have all digits in place but they donot have the hyphen(-)
    in the string.
    example: 151132 instead of 15-1132.

    Returns a list of columns.
    """
    if (len(columns[occupation_code_index]) > 7):
        # Trim any white space between the characters of the soc code.
        columns[occupation_code_index] = columns[occupation_code_index].replace(' ',
                                                                                '')
        columns[occupation_code_index] = columns[occupation_code_index][0:7]
        if ('-' not in columns[occupation_code_index]):
            # Case1: replace character at index 2 with hyphen(-)
            columns[occupation_code_index] = columns[occupation_code_index].replace(columns[occupation_code_index][2],
                                                                                    '-')
    elif(len(columns[occupation_code_index]) == 7):
        if ('-' not in columns[occupation_code_index]):
            # Case1: replace character at index 2 with hyphen(-)
            columns[occupation_code_index] = columns[occupation_code_index].replace(columns[occupation_code_index][2],
                                                                                    '-')
    else:
        if (len(columns[occupation_code_index]) == 6
                and (columns[occupation_code_index].isdigit())):
            # Case2: insert hyphen(-) at index 2
            columns[occupation_code_index] = (columns[occupation_code_index][:2]
                                              + '-'
                                              + columns[occupation_code_index][2:])
    return columns


def insert_into_states_dictionary(states_dictionary, state):
    """
    Takes inputs: states dictionary and state.
    states dictionary is a dictionary with states as key and count as value.
    This method updates the dictionary with state and its number of
    certified applications.
    """
    if state in states_dictionary:
        states_dictionary[state] = states_dictionary[state] + 1
    else:
        states_dictionary[state] = 1


def insert_into_occupation_dictionary(
        occupations_dictionary, soc_code, soc_name):
    """
    Takes inputs: occupation dictionary, soc code and soc name.
    occupations dictionary is a with soc codes as keys and
    another dictionary as values. The value of occupations dictionary
    is a dictionary with key corresponding soc names
    and their number of certified applications as values.
    This method updates the occupations dictionary with
    the soc name and count.

    This structure, dictionary of dictionaries is chosen for
    counting top occupations as simple dictionary with soc name as keys
    would not yield accurate results.
    This is because soc name is not unique, many rows of data have
    spelling errors, plural forms, etc and would be counted as
    different occupations even though intuitively they belong
    to same occupation.
    Thus in order to increase accuracy of counts soc code is used as key.
    """
    if soc_code in occupations_dictionary:
        if soc_name in occupations_dictionary[soc_code]:
            # both soc code and soc name have already been encountered.
            occupations_dictionary[soc_code][soc_name] = occupations_dictionary[soc_code][soc_name] + 1
        else:
            # only soc code has been previously encountered.
            occupations_dictionary[soc_code][soc_name] = 1
    else:
        # none of soc code and soc name have been previously encountered.
        occupations_dictionary[soc_code] = {soc_name: 1}


def check_and_split(line):
    """
    Takes input: line of data (string).
    This method checks if a line contains double quotation
    and splits with the appropriate split method(custom or in-built).
    Returns a list of columns and a boolean specifying if the row
    is clean or not.
    """
    is_clean_line = True
    if ('"' in line):
        # unclean data row, use custom split method.
        columns = custom_split(line, ';')
        is_clean_line = False
    else:
        # clean data row, use in-built split method.
        columns = line.split(';')
    return columns, is_clean_line


def clean_and_insert_columns(columns, is_clean_line):
    """
    Takes input: columns and boolean is_clean_line.
    This method applies appropriate data cleaning
    and then inserts the data into dictionary.
    """
    if (not is_clean_line):
        # unclean data row, clean the occupation column.
        columns = clean_occupation_name(columns)

    if (columns[occupation_code_index] != ''):
        # clean and insert only rows that have value.
        columns = clean_occupation_code(columns)
        insert_into_occupation_dictionary(occupations_dictionary,
                                          columns[occupation_code_index],
                                          columns[occupation_name_index])

    if (columns[state_column_index] != ''):
        # clean and insert only rows that have value.
        insert_into_states_dictionary(states_dictionary,
                                      columns[state_column_index])


def sort_occupations_dictionary():
    """
    This method first reduces the occupations_dictionary from
    having multiple key-value pairs(inner-dictionary) for one soc code to
    one key-value pair for the soc code and then sorts the dictionary.

    The reduced key in inner-dictionary is the key with
    highest value(maximum count) and reduced value in inner-dictionary
    is the sum of all values of inner-dictionary.

    Example: occupations_dictionary
    {'11-1011': {'CHIEF EXECUTIVES': 472},
     '11-1021': {'GENERAL AND OPERATIONS MANAGER': 2,
                 'GENERAL AND OPERATIONS MANAGERS': 1708,
                 'GENERAL AND OPERATIONS MANAGERSE': 1}
    }
    The inner dictionary for code 11-1021 has three keys and this method will
    reduce the above dictionary to
    {'11-1011': {'CHIEF EXECUTIVES': 472},
     '11-1021': {'GENERAL AND OPERATIONS MANAGERS': 1711}
    }
    The key with maximum count or value is chosen as
    key for reduced inner dictionary and value for the reduced inner dictionary
    is the sum of all values of inner dictionary.
    2 + 1708 + 1 = 1711.

    The assumption here is that most of the data rows donot have
    spelling errors which will be appropriate names to show to the user.
    Computing counts as sum of all values gives more accurate counts
    for the given name even though spelling errors and plural forms are used.

    Returns the sorted list.
    """
    for key in occupations_dictionary:
        # for each soc code, sort and reduce the inner-dictionary.

        # sort inner dictionary by descending counts and ascending names
        # to find top occupation string name
        # among different occupation names (soc names).
        sorted_inner_dictionary = sorted(occupations_dictionary[key].items(),
                                         key=lambda key_value: (-key_value[1],
                                                                key_value[0]))

        # for reduced key: take the first name
        # which will be the name with highest counts
        occupation_name = sorted_inner_dictionary[0][0]

        # for reduce value: compute the sum of all counts
        certified_applications_number = sum(occupations_dictionary[key].values())

        # reduce the inner dictionary
        occupations_dictionary[key] = {occupation_name: certified_applications_number}

    # sort the outer dictionary by descending counts and ascending names
    # to find top occupations among different occupations (soc codes)
    top_occupations = sorted(occupations_dictionary.items(),
                             key=lambda key_value: (-list(key_value[1].values())[0],
                                                    list(key_value[1].keys())[0]))
    return top_occupations


def sort_states_dictionary():
    """
    This method sorts the states_dictionary by descending counts and
    ascending names of states.

    Returns sorted list.
    """
    # sort by descending counts and ascending names.
    top_states = sorted(states_dictionary.items(),
                        key=lambda key_value: (-key_value[1],
                                               key_value[0]))
    return top_states


def write_top_occupations(top_occupations, top_ten_occupations_file):
    """
    Takes input: sorted list of occupations, file handler.
    This method writes the top ten occupations to the output file.

    sorted list of occupations is in format:
    [('15-1132', {'SOFTWARE DEVELOPERS, APPLICATIONS': 106189}),
     ('15-1121', {'COMPUTER SYSTEMS ANALYSTS': 104563}),
     ('15-1131', {'COMPUTER PROGRAMMERS': 74077}),
     ('15-1199', {'COMPUTER OCCUPATIONS, ALL OTHER': 55598})
    ]
    Each element of list is a tuple with soc code as first element
    and dictionary as second element.
    The key of the dictionary is soc name and value is the count.
    """
    with open(top_ten_occupations_file, 'w', encoding='utf8') as top_ten_occupations_file:
        # write header.
        top_ten_occupations_file.write(TOP_OCCUPATIONS_FILE_HEADER)
        line_number = 0

        for occupation in top_occupations:
            # prepare line in specified format.
            line = (list(occupation[1].keys())[0] + ';'
                    + str(list(occupation[1].values())[0]) + ';'
                    + str(round((((int(list(occupation[1].values())[0]))/total_certified_applications_number) * 100), 1)) + '%'
                    + '\n')

            # write line to file
            top_ten_occupations_file.write(line)

            # check if ten records are written.
            line_number = line_number + 1
            if (line_number == 10):
                # stop when top ten are done.
                break


def write_top_states(top_states, top_ten_states_file):
    """
    Takes list of sorted states and file handler.
    This method writes the top ten states to the file.

    sorted list of states is in the format:
    [('CA', 103682),
     ('TX', 59272),
     ('NY', 50533),
     ('NJ', 42833),
     ('IL', 31022)
    ]
    Each element of the list is a tuple with state as first
    element and count as second element.
    """
    with open(top_ten_states_file, 'w', encoding='utf8') as top_ten_states_file:
        # write header.
        top_ten_states_file.write(TOP_STATES_FILE_HEADER)
        line_number = 0

        for state in top_states:
            # prepare line in specified format.
            line = (state[0] + ';' + str(state[1]) + ';'
                    + str(round((((int(state[1]))/total_certified_applications_number) * 100), 1)) + '%'
                    + '\n')

            # write line to output file.
            top_ten_states_file.write(line)

            # check if ten records are written.
            line_number = line_number + 1
            if (line_number == 10):
                # stop when top ten are done.
                break


def output_top_occupations_and_states(
        input_file, occupations_dict, states_dict):
    """
    Takes input: input file, occupations dictionary and states dictionary.
    This is a wrapper method that runs all above methods to ouput
    top ten occupations and states.
    """
    # Access global variables for modification.
    global total_certified_applications_number

    with open(input_file, 'r', encoding='utf8') as file:
        # read header and capture necessary column information.
        infer_schema(file.readline(), ';')

        for line in file:
            # check line and split accordingly.
            columns, is_clean_line = check_and_split(line)

            # we need only certified counts, so filter.
            if (columns[status_column_index].upper() == 'CERTIFIED'):
                total_certified_applications_number = total_certified_applications_number + 1

                # clean necessary columns and insert into dictionaries.
                clean_and_insert_columns(columns, is_clean_line)

    # sort dictionaries to get top records.
    top_occupations = sort_occupations_dictionary()
    top_states = sort_states_dictionary()

    # write result to files.
    write_top_occupations(top_occupations, top_ten_occupations_file)
    write_top_states(top_states, top_ten_states_file)


if __name__ == '__main__':
    # Assign input and output files.
    input_file = sys.argv[1]
    top_ten_occupations_file = sys.argv[2]
    top_ten_states_file = sys.argv[3]

    # Call wrapper to solve challenge.
    output_top_occupations_and_states(input_file,
                                      occupations_dictionary,
                                      states_dictionary)
