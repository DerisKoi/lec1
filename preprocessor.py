# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd 
from pathlib import Path
from sklearn.preprocessing import LabelEncoder



def load_data(path):
    application = pd.read_csv(Path(path, 'application_train.csv'))
    bureau = pd.read_csv(Path(path, 'bureau.csv'))
    bureau_balance = pd.read_csv(Path(path, 'bureau_balance.csv'))
    credit_card_balance = pd.read_csv(Path(path, 'credit_card_balance.csv'))
    installment_payments = pd.read_csv(Path(path, 'installments_payments.csv'))
    pos_cash_balance = pd.read_csv(Path(path, 'POS_CASH_balance.csv'))
    previous_application = pd.read_csv(Path(path, 'previous_application.csv'))
    return application, bureau, bureau_balance, credit_card_balance, installment_payments, pos_cash_balance, previous_application


def application_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)
    
    df['CODE_GENDER'].replace('XNA', np.nan, inplace=True)
    df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace=True)
    df['DAYS_LAST_PHONE_CHANGE'].replace(0, np.nan, inplace=True)
    df['NAME_FAMILY_STATUS'].replace('Unknown', np.nan, inplace=True)
    df['ORGANIZATION_TYPE'].replace('XNA', np.nan, inplace=True)
    
    if fill_missing:
            df.fillna(fill_value, inplace=True)

    return df


def bureau_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)
    
    df['DAYS_CREDIT_ENDDATE'][df['DAYS_CREDIT_ENDDATE'] < -40000] = np.nan
    df['DAYS_CREDIT_UPDATE'][df['DAYS_CREDIT_UPDATE'] < -40000] = np.nan
    df['DAYS_ENDDATE_FACT'][df['DAYS_ENDDATE_FACT'] < -40000] = np.nan

    if fill_missing:
        df.fillna(fill_value, inplace=True)

    df['AMT_CREDIT_SUM'].fillna(fill_value, inplace=True)
    df['AMT_CREDIT_SUM_DEBT'].fillna(fill_value, inplace=True)
    df['AMT_CREDIT_SUM_OVERDUE'].fillna(fill_value, inplace=True)
    df['CNT_CREDIT_PROLONG'].fillna(fill_value, inplace=True)

    return df


def bureau_balance_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)
    
    if fill_missing:
        df.fillna(fill_value, inplace=True)
            
    return df


def credit_card_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)
    
    df['AMT_DRAWINGS_ATM_CURRENT'][df['AMT_DRAWINGS_ATM_CURRENT'] < 0] = np.nan
    df['AMT_DRAWINGS_CURRENT'][df['AMT_DRAWINGS_CURRENT'] < 0] = np.nan

    if fill_missing:
        df.fillna(fill_value, inplace=True)
    
    return df


def installment_payment_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)

    if fill_missing:
        df.fillna(fill_value, inplace=True)

    return df


def pos_cash_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)

    if fill_missing:
        df.fillna(fill_value, inplace=True)

    return df


def prev_application_cleaning(df, **kwargs):
    fill_missing = kwargs.get('fill_missing', False)
    fill_value = kwargs.get('fill_value', 0)

    df['DAYS_FIRST_DRAWING'].replace(365243, np.nan, inplace=True)
    df['DAYS_FIRST_DUE'].replace(365243, np.nan, inplace=True)
    df['DAYS_LAST_DUE_1ST_VERSION'].replace(365243, np.nan, inplace=True)
    df['DAYS_LAST_DUE'].replace(365243, np.nan, inplace=True)
    df['DAYS_TERMINATION'].replace(365243, np.nan, inplace=True)

    if fill_missing:
        df.fillna(fill_value, inplace=True)

    return df


def process_cat_feature(df):
    le = LabelEncoder()
    le_count = 0
    for col in df:
        if df[col].dtype == 'object':
            if len(list(df[col].unique())) <= 2:
                le.fit(df[col])
                df[col] = le.transform(df[col])
                le_count += 1
    print ('{} variable are label encoded'.format(le_count))
    return df


def one_hot_encoder(df):
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object']
    df = pd.get_dummies(df, columns= categorical_columns, dummy_na= True)
    print ('The shape of dataset after One hot encoding: {}'.format(df.shape))
    return df



