# Predicting price based on mileage
# Predicting
import pandas as pd
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso
)
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

cars = pd.read_csv("./car_deals.csv", sep=",")
X = cars.drop(columns=["id", "Location", "Name", "Model", "Deals", "Price", "Mileage"])
y = cars[["Price"]]

print(X.shape)
print(y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

threshold = 3 
skb = SelectKBest(score_func=chi2, k=threshold).fit(X,y)
sel_skb = skb.fit(X_train, y_train)
sel_skb_index = sel_skb.get_support()
best_features = X_train.iloc[:, sel_skb_index]
print('p_values', sel_skb.pvalues_)
print(best_features.columns)

# Use Gridsearch to find the maximum score within reasonable parameter values

model_info = [
    {"model": LinearRegression(fit_intercept=True), "name": "lm", "params": {}},
    {
        "model": RandomForestRegressor(),
        "name": "rfr",
        "params": {
            "n_estimators": [i for i in range(0, 7)],
        },
    },
    
    {
        "model": Lasso(fit_intercept=True),
        "name": "lasso",
        "params": {"alpha": [0.001, 0.01, 0.5, 0.8, 1, 1.5, 2]},
    },
    {
        "model": Ridge(fit_intercept=True),
        "name": "ridge",
        "params": {"alpha": [0.001, 0.01, 0.5, 0.8, 1, 1.5, 2]},
    }
]


def run_grid_search(m):
    # TODO
    res = []
    for item in m:
        model_name = item["model"]
        param = item["params"]
        name = item["name"]
        gs = GridSearchCV(
            estimator=model_name, param_grid=param, cv=5, return_train_score=True
        )

        g = gs.fit(X_train, y_train)
        res.append(
            {
                "name": name,
                "result": g.cv_results_,
                "result_2": g.best_estimator_,
                "score": g.best_score_,
            }
        )

    return res


result = run_grid_search(model_info)
result_df = pd.DataFrame()
result_df["Model"] = [i["name"] for i in result]
result_df["Score"] = [i["score"] for i in result]
print(result_df)


best = RandomForestRegressor()

fitted_1 = best.fit(X_train, y_train)
res_1 = fitted_1.predict(X_train)
score_1 = best.score(X, y)

r21 = r2_score(y_train, res_1)
mse1 = mean_squared_error(y_train, res_1)
mae1 = mean_absolute_error(y_train, res_1)

metrics = pd.DataFrame(
    {
        "Metrics": ["Overall Score", "R2", "Mean Squared Error", "Mean Absolute Error"],
        "RF": [score_1, r21, mse1, mae1]
    }
)
print(metrics)


