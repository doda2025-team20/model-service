# File:        read_data.py
#
# Author:      Rohan Patel
#
# Date:        05/09/2018
#
# Description:
# This script reads SMS data from the SMSSpamCollection file, prints the total
# number of SMS messages in the dataset, and then prints the first 100 messages.
# The purpose is to give an initial overview of how the dataset is structured.


# Path to the SMS Spam Collection dataset
DATA_PATH = "smsspamcollection/SMSSpamCollection"


def main():
    # Read all lines from the dataset file
    # rstrip() is used to remove trailing newline characters
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        messages = [line.rstrip() for line in file]

    # Print total number of messages in the dataset
    # Output formatting is intentionally kept identical to the original script
    print('\nTotal number of messages:' + str(len(messages)))
    print('\n')

    # Print the first 100 messages with their index
    # enumerate() is used to number each message starting from 0
    for messno, msg in enumerate(messages[:100]):
        print(messno, msg)
        print('\n')


# Entry point of the script
# This ensures the script runs only when executed directly
# and not when imported as a module
if __name__ == "__main__":
    main()