import csv
import pandas
import matplotlib.pyplot as plt


# accept a location
# return financial analysis
# financial analysis includes:
#   - total number of months included in the dataset
#   - net total amount of "Profit/Losses" over the entire period

# about the battery
# 10 hour cycle
# 100 MW capacity
# %%
def find_max_sum_consecutive_block(arr, block_size):
    max_sum = float('-inf')
    max_sum_index = -1

    for i in range(len(arr) - block_size + 1):
        block_sum = sum(arr[i:i + block_size])
        if block_sum > max_sum:
            max_sum = block_sum
            max_sum_index = i

    return arr[max_sum_index:max_sum_index + block_size]

# allocate 40 MW per hour for 5 hours
def ancillary_revenue(day):
    ancillary_revenue = 0
    # open the csv file
    with open('ercotAS22_peak.csv', newline='') as csvfile:
        # create a csv reader
        reader = csv.reader(csvfile, delimiter=',')
        # find the dayth * 10 row
        for i in range(day * 10):
            next(reader)
        # iterate through the next 10 rows
        for i in range(10):
            # add the value in the 3rd column to ancillary_revenue
            row = next(reader)
            price = max(float(row[3]), float(row[4]))
            if price < PROFIT_THRESHOLD - 20:
                continue
            ancillary_revenue += price * 40 * 5
        return ancillary_revenue


# %%
# simulate 1 year
# strategy is to participate in RTM market
# battery will charge during solar hours RTM (this goes into losses)
# battery will discharge during peak hours (this goes into gains)
# count operational losses
# how to pick the best ancillary service to participate in?
# do all of them and return the most profitable
# constraint is state of charge
COSTPERKWH = 150

# INPUTS TO THE MODEL
# 1. different load zones
# 2. different discharge times
# 3. different profit thresholds
settlement_point_names = ['LZ_HOUSTON']
settlement_point_irradiance = {
    'LZ_AEN': 1.03,
    'LZ_CPS': 1.03,
    'LZ_HOUSTON': .98,
    'LZ_LCRA': 1,
    'LZ_NORTH': .99,
    'LZ_RAYBN': 1,
    'LZ_SOUTH': 1.045,
    'LZ_WEST': 1.08
}
PROFIT_THRESHOLD = 75

for settlement_point_name in settlement_point_names:
    discharge_cap = 100
    discharge_times = [8]
    for discharge_time in discharge_times:
        gains = 0
        ASgains = 0
        losses = 3000000
        # open the xlsx file
        df = pandas.read_excel('ercot22rtm_' + settlement_point_name + '.xlsx', sheet_name='LZ_AEN')

        historical_revenue = []
        historical_asrevenue = []
        hist_spp = []

        # %%
        # iterate through the rows 96 at a time
        # each row is 15 minutes
        for i in range(0, len(df), 96):
            # get the 96 rows
            block = df[i:i + 96]
            # get the prices
            prices = block['Settlement Point Price'].tolist()
            # get the 10 hour block with the highest sum
            max_sum_block = find_max_sum_consecutive_block(prices, discharge_time * 4)

            # calculate the revenue
            revenue = 0

            # calculate the average LMP price for the block
            sum_prices = sum(max_sum_block)
            avg_price = sum_prices / len(max_sum_block)
            hist_spp.append(avg_price)

            # don't turn on if not profitable
            # do ancillary service instead
            if avg_price < PROFIT_THRESHOLD:
                asrevenue = ancillary_revenue(i // 96)
                ASgains += asrevenue
                historical_asrevenue.append(asrevenue)
                historical_revenue.append(0)
                continue

            for price in max_sum_block:
                revenue = price * settlement_point_irradiance[settlement_point_name] * discharge_cap / 4
                if revenue > 0:
                    gains += revenue
                else:
                    losses += revenue

            historical_revenue.append(revenue)
            historical_asrevenue.append(0)

        # graph the historical revenue
        plt.plot(historical_revenue)
        plt.ylabel('Revenue ($): ' + settlement_point_name + ' ' + str(discharge_time) + 'hr')
        plt.xlabel('Day')
        plt.show()

        # graph the historical spp
        plt.plot(hist_spp)
        plt.ylabel('SPP ($): ' + settlement_point_name + ' ' + str(discharge_time) + 'hr')
        plt.xlabel('Day')
        plt.show()

        # graph the historical ancillary revenue
        plt.plot(historical_asrevenue)
        plt.ylabel('Ancillary Revenue ($): ' + settlement_point_name + ' ' + str(discharge_time) + 'hr')
        plt.xlabel('Day')
        plt.show()

        # %%
        # graph the historical prices for the year
        historical_prices = []

        # iterate through the rows 96 at a time
        # each row is 15 minutes
        for i in range(0, len(df), 96):
            # get the 96 rows
            block = df[i:i + 96]
            # get the prices
            prices = block['Settlement Point Price'].tolist()
            # get the 10 hour block with the highest sum
            max_price = max(prices)

            historical_prices.append(max_price)

        # graph the historical prices
        plt.plot(historical_prices)
        plt.ylabel('Price ($): ' + settlement_point_name + ' ' + str(discharge_time) + 'hr')
        plt.xlabel('Day')
        plt.show()

        # print financial analysis
        print("Financial Analysis for " + settlement_point_name)
        print("----------------------------")
        print(f"Total Gains: ${gains}")
        print(f"Total Losses: ${losses}")
        print(f"Total Ancillary Service Gains: ${ASgains}")

        # calc other stats
        tot_mwh = discharge_cap * discharge_time
        cost_construction = tot_mwh * COSTPERKWH * 1000
        breakeven = cost_construction / (ASgains + gains - losses)
        print(f"Cost of Construction: ${cost_construction}")
        print(f"Breakeven: {breakeven} years")
