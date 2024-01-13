import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

cars = pd.read_csv("./car_deals.csv", sep=",")

# EDAQ
cars.info()
cars.shape
print(cars.describe())

# 1. ratings distribution

fig, ax = plt.subplots(2)

models = (
    cars.groupby(["Model"])["Rating"]
    .aggregate(["mean"])
    .sort_values(by=["mean"])
    .reset_index()
)

sns.barplot(ax=ax[0], x=models["Model"].iloc[0:9], y=models["mean"])
sns.barplot(ax=ax[1], x=models["Model"].iloc[9:17], y=models["mean"])
fig.suptitle("Ratings for each car models (0-5)")
ax[0].set_ylabel("Mean Rating")
ax[1].set_ylabel("Mean Rating")
ax[0].set_xlabel("Car models")
ax[1].set_xlabel("Car models")

plt.show()

# 2. Prices by location
fig, axs = plt.subplots(2)
prices = (
    cars.drop(columns=["Name", "Location"])
    .groupby(["Model", "Deals"])
    .mean()[["Price"]]
).reset_index()

prices = prices[prices["Deals"] != "CPO Warrantied"]
sns.barplot(
    ax=axs[0],
    data=prices.iloc[0:19],
    x="Price",
    y="Model",
    hue="Deals",
    orient="horizontal",
    gap=0.5
)
sns.barplot(
    ax=axs[1],
    data=prices.iloc[20:39],
    x="Price",
    y="Model",
    hue="Deals",
    orient="horizontal",
    gap=0.5
)
fig.suptitle("Prices for each models classified by the deal quality")
axs[0].set_ylabel("Car model")
axs[0].set_yticklabels(axs[0].get_yticklabels(),fontsize=6)
axs[1].set_yticklabels(axs[1].get_yticklabels(),fontsize=6)
axs[1].set_ylabel("Car model")
axs[0].set_xlabel("Price ($)q")
axs[1].set_xlabel("Price ($)")

plt.show()

# 3. used_mi and price and rating correlation
corr = cars[["Mileage", "Rating", "Price"]]
hm = sns.heatmap(
    corr.corr(),
    vmin=-1,
    vmax=1,
    annot=True,
    cbar_kws={"label": "Correlation", "orientation": "horizontal"},
)
hm.set_title("Correlation of mileage used, ratings and prices of rental cars in US")
plt.show()
print(corr.corr())

# 4. regression plot of mileage
fig, ax = plt.subplots(2)
vars = ["Mileage", "Rating"]
for i, v in enumerate(vars):
    sns.regplot(data=cars, x=v, y="Price", ax=ax[i])
fig.suptitle("Regression line plot for Price and Rating vs Mileage")
ax[0].set_ylabel("Price ($)")
ax[1].set_ylabel("Price ($)")
plt.show()


# 5. Cheapest car with least used mileage
ordered_by_price = cars.sort_values(by=["Price"], ascending=True)
cheap_low_mil = ordered_by_price[
    ordered_by_price["Mileage"] == min(ordered_by_price.Mileage)
]
high_mil = ordered_by_price[
    ordered_by_price["Mileage"] == max(ordered_by_price.Mileage)
]
combined = pd.concat([cheap_low_mil, high_mil], ignore_index=True)[
    ["Name", "Rating", "Mileage", "Deals", "Price"]
].reset_index()
combined = combined.pivot(
    index="Name", columns=[], values=["Rating", "Deals", "Mileage", "Price"]
)
print(combined)

# 6 - Do x = "Price" as well!
jg = sns.JointGrid(data=cars, x="Reviews", y="Price_change")
jg.plot(sns.lineplot, sns.histplot)
jg.set_axis_labels("Reviews","Price Change ($)")
jg.fig.suptitle("Relationship of price change of cars and reviews it gets")
jg.fig.tight_layout()
plt.show()

# 7 ##TODO
box = sns.boxplot(data=cars, x="Deals", y="Reviews")
box.set(xlabel="Deal Quality", title="Number of reviews for each deal qualities")
plt.show()


# 8
def get_states(x):
    return str(x).split(", ")[1]


cars["Location"] = cars["Location"].apply(get_states)
d = cars.groupby(["Location"]).mean(numeric_only=True).reset_index()


def count(i):
    c = 0
    for j in cars["Location"]:
        if str(j) == str(i):
            c += 1
    return c


d["Cars_from"] = [count(i) for i in d["Location"]]
d = d.sort_values(by=["Rating"], ascending=False).drop(columns=["id"])
d=d[d["Cars_from"]>1].reset_index()
print(d)

figs,axs = plt.subplots(5)
cats = ["Price", "Rating", "Reviews", "Mileage","Price_change"]
for i in range(0,5):
    sns.barplot(data=d, x="Location", y=cats[i], ax=axs[i], gap=0.5)
figs.tight_layout(pad=7)
figs.suptitle("Descriptive statistic of rental cars for each US states")
axs[4].set_ylabel("Price Change ($)")
plt.show()