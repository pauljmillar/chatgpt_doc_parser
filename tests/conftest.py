import os
import logging
import csv
import datetime
from collections import OrderedDict

import pytest

failed = False
#test_results = None
statistics_csv_path = 'test_result.csv'
all_test_results = None



def get_current_test():
    """Just a helper function to extract the current test"""
    full_name = os.environ.get('PYTEST_CURRENT_TEST').split(' ')[0]
    test_file = full_name.split("::")[0].split('/')[-1].split('.py')[0]
    test_name = full_name.split("::")[1]
    #global statistics_csv_path
    #new_statistics_csv_path = test_file+".csv"
    #if new_statistics_csv_path != statistics_csv_path:
        #reset
        #global test_results
        #test_results = None
        #failed = False
        #statistics_csv_path = new_statistics_csv_path

        #compare current file name to keys of all_test_results

    return full_name, test_file, test_name

def pytest_configure(config):
#def pytest_runtestloop():
    """Called when pytest is starting and before running any tests."""
    #global test_results
    test_results = OrderedDict()
    test_results['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Initial state is success, only change on failure
    test_results['state'] = "Success"
    test_results['first_error_message'] = ""
    test_results['amount_of_failed_tests'] = 0


    test_results2 = OrderedDict()
    test_results2['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    global all_test_results
    all_test_results = {'test_auto_service_1': test_results,
                        'test_auto_service_2': test_results.copy(),
                        'test_auto_service_3': test_results.copy(),
                        'test_auto_warranty_1': test_results.copy(),
                        'test_auto_warranty_2': test_results.copy(),
                        'test_auto_warranty_3': test_results.copy()
                        }
    #for each file, create the ordered dict, set in all_test_results

def pytest_unconfigure(config):
#def pytest_runtest_logfinish():

    """Called when pytest is about to end. Can be used to print the result dict or
    to pipe the data into a file"""

    #for each ordered dict in all_test_results
    #set first row
    #first read the first row from the file, and file name will be equal to the key + csv

    for key,value in all_test_results.items():
        create_first_line = False
        line_to_be_written = list(value.values())
        csv_header = list(value.keys())
        #print('###############################')
        #print(value.keys())

        try:
            filename = key + ".csv"
            with open(filename) as statistics_csv:
                csv_reader = csv.reader(statistics_csv)
                header = next(csv_reader)
                if header is not None:
                    #for i in range(len(csv_header)):
                    #    try:
                    #        if header[i] != csv_header[i]:
                    #            print(f"Non matching header column in the csv file: {header[i]} != {csv_header[i]}!!!!")
                    #            #raise Exception("Probably the csv format of your tests have changed.. please fix!")
                    #    except IndexError:
                    #        raise Exception("Probably the csv format of your tests have changed.. please fix!")
                    #        print("Probably the csv format of your tests have changed.. please fix!")
                    print("header exists")
                else:
                    create_first_line = True
        except FileNotFoundError:
            create_first_line = True

        with open(filename, 'a+', newline='') as statistics_csv:
            csv_writer = csv.writer(statistics_csv)
            if create_first_line:
                csv_writer.writerow(csv_header)
            csv_writer.writerow(line_to_be_written)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """The actual wrapper that gets called before and after every test"""

    global all_test_results
    #for key,value in all_test_results:

    #global test_results
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        full_name, test_file, test_name = get_current_test()
        test_name_msg = f"{test_name}_msg"

        for key, value in all_test_results.items():
            #filename = key + ".csv"
            #update the results dict with the key name that equals the filename that this test is in
            if key == test_file:
                print('##############'+key)

                if rep.failed:
                    value['state'] = "Failure"
                    value['amount_of_failed_tests'] += 1
                    value[test_name] = f"Failure"
                    #test_results[test_name_msg] = f"{call.excinfo.typename} - {call.excinfo.value}"
                    value[test_name_msg] = f"{call.excinfo.exconly(True)}".split('|')[0]
                    value[test_name_msg] = value[test_name_msg].split('Actual:')[1]

                    #if value['first_error_message'] == "":
                    #    if test_name_msg in value:
                    #        value['first_error_message'] = value[test_name_msg]

                else:
                    value[test_name] = "Success"
                    value[test_name_msg] = f""

                    #determine which top level dictionary

def pytest_collect_file(path, parent):
    if path.ext == ".py":
        # Do something for each Python file, like print the file name
        print(f"Collecting tests from file: {path}")

def pytest_csv_register_columns(columns):
    columns['my_constant_column'] = 'foobar'