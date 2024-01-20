import sqlite3
import myfoodfacts, openfoodfacts_search
import pandas as pd
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt

db_filepath = myfoodfacts.db_filepath

#adds entry to db from dictionary
def add_entry(entry_dict):
	con = sqlite3.connect(db_filepath)
	cursor = con.cursor()
	statement = "INSERT INTO Entries ({columns}) VALUES ({values});".format(columns=",".join(entry_dict.keys()), values=",".join(list(entry_dict.values())))
	cursor.execute(statement)
	con.commit()
	con.close()

#returns total of attributes (e.g. carbohydrates) in given date
#returns results as series
def get_total_for_date(date:str, attributes:list):
    AMOUNT_TYPE_CONVERSION = {"Serving":"_serving", "100g":"_100g"}
    MULTIPLIERS  = {"Serving": 1, "100g":0.01}
    statement = """
		SELECT entry_database, Entries.code, amount, amount_type
		FROM Entries
		WHERE entry_date = '{d}'
    """.format(d=date)
    con = sqlite3.connect(db_filepath)
    entries = pd.read_sql_query(statement, con)
    con.close()
    
    values_df = pd.DataFrame(columns=attributes)
    for index, row in entries.iterrows(): #for each entry in given day
        new_attr_list = [] #create new list with database specific attribute names
        for attr in attributes:
            if attr == "energy" and row["entry_database"] == "OFF":
                new_string = "energy-kcal" + AMOUNT_TYPE_CONVERSION[row["amount_type"]]
            elif attr == "energy":
                new_string = "energy_kcal" + AMOUNT_TYPE_CONVERSION[row["amount_type"]]
            elif attr == "fibre" and row["entry_database"] == "OFF":
                new_string = "fiber" + AMOUNT_TYPE_CONVERSION[row["amount_type"]]
            elif attr == "saturates" and row["entry_database"] == "OFF":
                new_string = "saturated-fat" + AMOUNT_TYPE_CONVERSION[row["amount_type"]]
            else:
                new_string = attr + AMOUNT_TYPE_CONVERSION[row["amount_type"]]
            new_attr_list.append(new_string)
        
        if row["entry_database"] == "MFF": #myfoodfacts entries
            item_id = myfoodfacts.get_item_from_code(row["code"])[0]
            results = myfoodfacts.get_item(item_id, new_attr_list) #fetch attribute info
        else: #openfoodfacts entries
            results = openfoodfacts_search.get_product_attributes(row["code"], new_attr_list)
        
        results = [row["amount"]*MULTIPLIERS[row["amount_type"]]*x for x in results] #calculate correct value for the specific entry
        
        values_df.loc[len(values_df)] = results
    
    return values_df.sum()

def plot_daily_graph(date:str, save_path:str):
    BG_COLOR = "#00181C"
    TEXT_COLOR = "white"
    attr_list = ["energy", "carbohydrates", "sugars", "fat", "saturates", "proteins", "sodium"]
    attr_list.reverse()
    daily_totals = get_total_for_date(date, attr_list).to_frame(name="total")
    RI_ADULT_PER_DAY = { "energy":2000, "fat":70, "saturates":20, "carbohydrates":260, "sugars":90, "fibre":30, "proteins":50, "sodium":6 }
    daily_ri = [RI_ADULT_PER_DAY[x] for x in attr_list] #get RI values and assign to list
    daily_totals = daily_totals.assign(ri=daily_ri) #add RI values as column to df
    
    #scale values so they all add up to 1000
    daily_totals["total"] = daily_totals["total"] * (1000 / daily_totals["ri"])
    daily_totals["ri"] = 1000
    
    daily_totals["ri"] = daily_totals["ri"] - daily_totals["total"]
    fig, ax = plt.subplots(layout="constrained")
    fig.set_figwidth(8)
    daily_totals.plot(
        kind="barh",
        stacked=True,
        mark_right=True,
        ax=ax,
        legend=False,
        colormap=plt.get_cmap("RdYlGn_r")
    )
    fig.set_facecolor(BG_COLOR)
    ax.spines[['left', 'top', 'bottom', 'right']].set_visible(False)
    ax.set_xticks([])
    ax.yaxis.set_tick_params(which=u'both', length=0, colors=TEXT_COLOR)
    ax.set_facecolor(BG_COLOR)
    fig.savefig(save_path)