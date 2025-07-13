import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline
from types import MethodType
from scipy.stats import t

def mlr(
    X,
    y,
    train_ratio: float = 0.7,
    random_state: int = 42,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    weight=None,
):
    """
    Train a (optionally weighted) multivariate linear regression model
    and store bootstrap coefficients for confidence and prediction intervals.
    """
    # determine sample weights if provided as column name or array
    if weight is None:
        sample_weight_full = None
    elif isinstance(weight, str):
        if not hasattr(X, "__getitem__"):
            raise ValueError("weight as str requires X to support column access")
        sample_weight_full = X[weight].to_numpy()
        X = X.drop(columns=[weight])
    else:
        sample_weight_full = np.asarray(weight)
        if len(sample_weight_full) != len(X):
            raise ValueError("Length of weight array must match number of samples")

    # split data (and weights) into training and test sets
    split_args = [X, y]
    if sample_weight_full is not None:
        split_args.append(sample_weight_full)
    split_res = train_test_split(
        *split_args,
        train_size=train_ratio,
        random_state=random_state,
    )
    if sample_weight_full is not None:
        X_train, X_test, y_train, y_test, w_train, w_test = split_res
    else:
        X_train, X_test, y_train, y_test = split_res
        w_train = w_test = None

    # fit linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train, sample_weight=w_train)

    # perform bootstrap to estimate coefficient distributions
    model.boot_coefs_ = None
    if n_bootstrap and n_bootstrap > 0:
        rng = np.random.RandomState(random_state)
        n_feats = X_train.shape[1]
        boot_coefs = np.zeros((n_bootstrap, n_feats + 1))
        for i in range(n_bootstrap):
            idx = rng.randint(0, len(X_train), len(X_train))
            X_bs = X_train.iloc[idx] if hasattr(X_train, "iloc") else X_train[idx]
            y_bs = y_train.iloc[idx] if hasattr(y_train, "iloc") else y_train[idx]
            w_bs = None if w_train is None else (
                w_train.iloc[idx] if hasattr(w_train, "iloc") else w_train[idx]
            )
            m_bs = LinearRegression().fit(X_bs, y_bs, sample_weight=w_bs)
            boot_coefs[i, 0] = m_bs.intercept_
            boot_coefs[i, 1:] = m_bs.coef_

        # compute percentile-based confidence intervals for coefficients
        lower_pct, upper_pct = (1 - ci) / 2 * 100, (1 + ci) / 2 * 100
        lowers = np.percentile(boot_coefs, lower_pct, axis=0)
        uppers = np.percentile(boot_coefs, upper_pct, axis=0)
        feats = list(X_train.columns) if hasattr(X_train, "columns") else [f"x{i}" for i in range(n_feats)]
        model.conf_int_ = pd.DataFrame({
            "Feature": ["Intercept"] + feats,
            f"CI_{int(ci*100)}%_lower": lowers,
            f"CI_{int(ci*100)}%_upper": uppers,
        }).set_index("Feature")
        model.boot_coefs_ = boot_coefs

    # store confidence level
    model.ci_ = ci

    return model, X_train, X_test, y_train, y_test

def naive_bayes(X, y, train_ratio=0.7, random_state=42):
    """
    Split data into train and test sets and fit a GaussianNB classifier.
    """
    # split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=train_ratio,
        random_state=random_state
    )
    # fit Gaussian Naive Bayes model
    model = GaussianNB()
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test

def lda(X, y, train_ratio=0.7, random_state=42):
    """
    Split data into train and test sets and fit an LDA classifier.
    """
    # split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=train_ratio,
        random_state=random_state
    )
    # fit Linear Discriminant Analysis model
    model = LinearDiscriminantAnalysis()
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test

def logistic_regression_classifier(X, y, train_ratio=0.7, random_state=42,
                                   solver='lbfgs', max_iter=5000):
    """
    Split data into train and test sets and fit a logistic regression classifier.
    """
    # split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=train_ratio,
        random_state=random_state,
        stratify=y
    )
    # build pipeline: standardize features -> logistic regression
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            solver=solver,
            max_iter=max_iter,
            random_state=random_state
        )
    )
    # fit pipeline
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test