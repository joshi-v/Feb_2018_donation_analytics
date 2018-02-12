import sys
import re
import math
from collections import defaultdict

data_file = sys.argv[1]
percentile_file = sys.argv[2]
output_file = sys.argv[3]


class DonationAnalytics(object):
    def __init__(self):

        # {'donor_name' : 'donor_zip'}
        self.repeat_donors = {}

        # {'cmte_id' : {'zipcode' : { 'year' : [] } } }
        self.donation_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        self.percentile_value = None # is populated from percentile.txt file

        # These fields are populated with values for the current record from itcont.txt when is_valid_line is called
        self.current_cmte_id = None
        self.current_donor_name = None
        self.current_donor_zip = None
        self.current_transaction_date = None
        self.current_transaction_amount = None
        self.current_other_id = None

    def create_output_record(self):
        cmte_id = self.current_cmte_id
        donor_zip = self.current_donor_zip[0:5]
        year = self.current_transaction_date[-4:]
        transaction_amount = self.current_transaction_amount

        self.donation_stats[cmte_id][donor_zip][year].append(transaction_amount)
        number_of_contributions = str(len(self.donation_stats[cmte_id][donor_zip][year]))
        total_dollar_amount_of_contributions = str(sum(map(int,self.donation_stats[cmte_id][donor_zip][year])))
        value_at_percentile = self.get_value_at_percentile(self.donation_stats[cmte_id][donor_zip][year])

        return '|'.join([cmte_id, donor_zip, year, value_at_percentile, total_dollar_amount_of_contributions, number_of_contributions])

    def get_value_at_percentile(self, data):
        ordinal_rank = int(math.ceil(self.percentile_value * len(data) / 100.)) # convert to int since indexes must be ints not float
        return data[ordinal_rank - 1]

    def is_repeat_donor(self, donor_name, donor_zip):
        if donor_name in self.repeat_donors and self.repeat_donors[donor_name] == donor_zip:
            return True
        else:
            self.repeat_donors[donor_name] = donor_zip # add the donor details and return False
            return False


    def is_valid_line(self, line):
        '''
        Check if the line is a valid line
        :param line: line from input file that is to be validated
        :return: True if line is valid, False otherwise
        '''

        def is_valid_cmte_id(cmte_id):
            if cmte_id == '':
                return False
            return True

        def is_valid_donor_name(donor_name):
            if donor_name == '':
                return False
            return True

        def is_valid_donor_zip(donor_zip):
            if not re.match('^[0-9]{5,}$', donor_zip):
                return False
            return True

        def is_valid_transaction_date(transaction_date):
            if not re.match('^[0-9]{8}$', transaction_date):
                return False
            return True

        def is_valid_transaction_amount(transaction_amount):
            if not re.match('^[0-9]+$', transaction_amount):
                return False
            return True

        def is_valid_other_id(other_id):
            if not other_id == '':
                return False
            return True

        line_data = line.split('|')
        self.current_cmte_id = line_data[0].strip() # aka filer id
        self.current_donor_name = line_data[7].strip()
        self.current_donor_zip = line_data[10].strip()
        self.current_transaction_date = line_data[13].strip()
        self.current_transaction_amount = line_data[14].strip()
        self.current_other_id = line_data[15].strip()

        return is_valid_cmte_id(self.current_cmte_id) and is_valid_donor_name(self.current_donor_name) and is_valid_donor_zip(self.current_donor_zip) and is_valid_transaction_date(self.current_transaction_date) and is_valid_transaction_amount(self.current_transaction_amount) and is_valid_other_id(self.current_other_id)


if __name__ == '__main__':
    obj = DonationAnalytics()

    with open(percentile_file) as percf:
        percentile_value = percf.readline().strip()
        if not re.match('^[0-9]{1,3}$', percentile_value):
            print "Percentile value does not meet correct format {}".format(percentile_value)
            sys.exit(1)
        else:
            obj.percentile_value = int(percentile_value) # set attribute

    with open(data_file) as dataf, open(output_file, "w") as outf:
        for line in dataf:
            if not obj.is_valid_line(line):
                continue
            else:
                donor_name = obj.current_donor_name
                donor_zip = obj.current_donor_zip[0:5]
                if obj.is_repeat_donor(donor_name, donor_zip):
                    outf.write(obj.create_output_record() + "\n")
                else:
                    continue



