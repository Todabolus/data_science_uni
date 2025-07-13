from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

def evaluate_classification(model, X_train, y_train, X_test, y_test):
    """
    Evaluate a classifier by printing reports and plotting confusion matrices
    for both training and test datasets.
    """
    for split_name, X_split, y_split in [
        ('TRAIN', X_train, y_train),
        ('TEST',  X_test,  y_test)
    ]:
        # generate predictions for this split
        y_pred = model.predict(X_split)
        # print classification report
        print(f"\n=== {split_name} Classification Report ===")
        print(classification_report(y_split, y_pred))
        # compute and plot confusion matrix
        cm = confusion_matrix(y_split, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"{split_name} Confusion Matrix")
        plt.show()

def evaluate_regression(
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    feature_names=None,
    show_last_row_interval: bool = True,
    plot_test_set: bool = True,
    n_last=50
):
    """
    Evaluate a regression model by:
      - Displaying coefficients (with optional bootstrap intervals)
      - Reporting R², RMSE, MAE for train and test
      - Computing and printing a prediction interval for the last test sample
      - Plotting predictions and intervals for recent test samples
    """
    # determine feature names if not provided
    if feature_names is None:
        feature_names = (
            list(X_train.columns)
            if hasattr(X_train, "columns")
            else [f"x{i}" for i in range(X_train.shape[1])]
        )

    # assemble coefficient table
    base_df = pd.DataFrame({
        "Feature": ["Intercept"] + feature_names,
        "Coefficient": [model.intercept_] + list(model.coef_),
    }).set_index("Feature")
    if hasattr(model, "conf_int_"):
        # show coefficients with bootstrap confidence intervals
        print("Coefficients with bootstrap confidence intervals:")
        display(base_df.join(model.conf_int_))
    else:
        # show coefficients without intervals
        display(base_df)

    # compute and print metrics for training and test
    for name, Xs, ys in [("TRAIN", X_train, y_train), ("TEST", X_test, y_test)]:
        preds = model.predict(Xs)
        print(f"\n--- {name} ---")
        print(f"R²  : {r2_score(ys, preds):.4f}")
        print(f"RMSE: {np.sqrt(mean_squared_error(ys, preds)):.4f}")
        print(f"MAE : {mean_absolute_error(ys, preds):.4f}")

    # prediction interval for the last test sample (if bootstrap info is available)
    if show_last_row_interval and getattr(model, "boot_coefs_", None) is not None:
        # extract last test input and true value
        x_last = (
            X_test.iloc[-1].to_numpy()
            if hasattr(X_test, "iloc")
            else X_test[-1]
        )
        y_true_last = (
            y_test.iloc[-1]
            if hasattr(y_test, "iloc")
            else y_test[-1]
        )
        y_pred_last = model.predict(x_last.reshape(1, -1))[0]
        # generate bootstrap predictions for last sample
        boot_preds = model.boot_coefs_[:, 0] + model.boot_coefs_[:, 1:] @ x_last
        # compute percentile-based interval
        lower, upper = np.percentile(
            boot_preds,
            [(1 - model.ci_) / 2 * 100, (1 + model.ci_) / 2 * 100]
        )
        # display interval results
        print("\n=== Last Test Sample ===")
        print(f"True y      : {y_true_last:.4f}")
        print(f"Predicted y : {y_pred_last:.4f}")
        print(f"PI ({int(model.ci_*100)}%) : [{lower:.4f}, {upper:.4f}]")

    # plot recent predictions with intervals (if bootstrap info is available)
    if plot_test_set and getattr(model, "boot_coefs_", None) is not None:
        # prepare arrays for plotting
        X_arr = (
            X_test.to_numpy()
            if hasattr(X_test, "to_numpy")
            else X_test
        )
        y_arr = (
            y_test.to_numpy()
            if hasattr(y_test, "to_numpy")
            else y_test
        )
        preds_all = model.predict(X_arr)
        # compute bootstrap prediction matrix
        boot_preds_all = (
            model.boot_coefs_[:, 0][:, None]
            + model.boot_coefs_[:, 1:] @ X_arr.T
        )
        # calculate bounds for each sample
        lower_all = np.percentile(
            boot_preds_all, (1 - model.ci_) / 2 * 100, axis=0
        )
        upper_all = np.percentile(
            boot_preds_all, (1 + model.ci_) / 2 * 100, axis=0
        )

        # select index range for the last n samples
        start = max(0, len(y_arr) - n_last)
        idx = np.arange(1, len(y_arr) - start + 1)

        # slice data for plotting
        y_plot = y_arr[start:]
        pred_plot = preds_all[start:]
        lower_plot = lower_all[start:]
        upper_plot = upper_all[start:]

        # plot intervals and points
        plt.figure(figsize=(9, 5))
        plt.fill_between(idx, lower_plot, upper_plot, alpha=0.3,
                         label=f"{int(model.ci_*100)}% PI")
        plt.plot(idx, pred_plot, 'o-', label='Predicted y')
        plt.plot(idx, y_plot, 'x', markersize=7, linestyle='None',
                 label='Actual y')
        plt.xlabel('Recent Test Samples (chronological)')
        plt.ylabel('Target')
        plt.title('Predictions & Prediction Interval (Recent Samples)')
        plt.legend()
        plt.tight_layout()
        plt.show()
    elif plot_test_set:
        # notify if prediction intervals cannot be plotted
        print("\nPlot could not be generated (no bootstrap information).")
