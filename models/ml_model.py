from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np


def predict_next_month(data, return_model=False):
    """
    Predict next month's expense using Linear Regression.
    Performs simple hyperparameter tuning (fit_intercept True vs False).
    Returns:
        next_prediction, mae, r2
        If return_model=True → also returns trained model
    """

    # ====== PREPARE DATA ======
    X = np.arange(1, len(data) + 1).reshape(-1, 1)
    y = np.array(data)

    # ====== MODEL 1: WITH INTERCEPT ======
    model_with_intercept = LinearRegression(fit_intercept=True)
    model_with_intercept.fit(X, y)
    pred_with = model_with_intercept.predict(X)
    r2_with = r2_score(y, pred_with)

    # ====== MODEL 2: WITHOUT INTERCEPT ======
    model_without_intercept = LinearRegression(fit_intercept=False)
    model_without_intercept.fit(X, y)
    pred_without = model_without_intercept.predict(X)
    r2_without = r2_score(y, pred_without)

    # ====== SELECT BEST MODEL ======
    if r2_with >= r2_without:
        model = model_with_intercept
        predictions = pred_with
        selected_type = "With Intercept"
        r2 = r2_with
    else:
        model = model_without_intercept
        predictions = pred_without
        selected_type = "Without Intercept"
        r2 = r2_without

    # ====== METRICS ======
    mae = mean_absolute_error(y, predictions)

    # ====== NEXT MONTH PREDICTION ======
    next_month = np.array([[len(data) + 1]])
    next_prediction = model.predict(next_month)[0]

    # ====== CONSOLE OUTPUT (For Demo/Viva) ======
    print("====== HYPERPARAMETER TEST ======")
    print("With Intercept R2:", round(r2_with, 4))
    print("Without Intercept R2:", round(r2_without, 4))
    print("Selected Model:", selected_type)

    print("====== MODEL PERFORMANCE ======")
    print("Predicted Next Month:", round(next_prediction, 2))
    print("MAE:", round(mae, 2))
    print("R2 Score:", round(r2, 4))
    print("================================")

    # ====== RETURN VALUES ======
    if return_model:
        return next_prediction, mae, r2, model

    return next_prediction, mae, r2