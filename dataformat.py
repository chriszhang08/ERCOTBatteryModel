import pandas

# clean the following xlsx file
# only select the rows where the Settlement Point Name = "LZ_AEN"

# read the xlsx file
df = pandas.read_excel('ercot22rtm.xlsx', sheet_name='Jan')

# select the rows where the Settlement Point Name =
settlement_point_names = ['LZ_AEN', 'LZ_CPS', 'LZ_HOUSTON', 'LZ_LCRA', 'LZ_NORTH', 'LZ_RAYBN', 'LZ_SOUTH', 'LZ_WEST']
for settlement_point_name in settlement_point_names:
    df = df[df['Settlement Point Name'] == settlement_point_name]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for month in months:
        # read the xlsx file
        newdf = pandas.read_excel('ercot22rtm.xlsx', sheet_name=month)
        # select the rows where the Settlement Point Name = "LZ_AEN"
        newdf = newdf[newdf['Settlement Point Name'] == settlement_point_name]
        # select the rows where the Settlement Point Type = "LZ"
        newdf = newdf[newdf['Settlement Point Type'] == 'LZ']
        # append the selected rows to the previous dataframe
        df = df.append(newdf, ignore_index=True)

    # write the selected rows to a new xlsx file
    df.to_excel('ercot22rtm_' + settlement_point_name + '.xlsx', sheet_name='LZ_AEN', index=False)

    # print the max of the column named Settlement Point Price
    print(df['Settlement Point Price'].max())
