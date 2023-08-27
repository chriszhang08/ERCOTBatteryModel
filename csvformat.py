import csv

# open the csv file
with open('ercotAS22_clean.csv', newline='') as csvfile:
    # create a new csv
    # but only select the rows where hour > 15:00
    with open('ercotAS22_peak.csv', 'w', newline='') as csvfile2:
        # create a csv writer
        writer = csv.writer(csvfile2, delimiter=',')
        # create a csv reader
        reader = csv.reader(csvfile, delimiter=',')
        # skip header
        next(reader)
        # iterate through the rows
        for row in reader:
            # only select the rows where hour > 15:00
            if int(row[1][0:2]) >= 15:
                writer.writerow(row)
