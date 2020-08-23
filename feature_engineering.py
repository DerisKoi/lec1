import numpy as np
import pandas as pd 


def fe_application(df):
    df['id_renewal_days'] = df['DAYS_ID_PUBLISH'] - df['DAYS_BIRTH']
    df['id_renewal_days_issue'] = np.vectorize(
            lambda x: max(list(set([min(x, age) for age in [0, 20 * 366, 25 * 366, 45 * 366]]) - set([x]))))(
            df['id_renewal_days'])
    df.loc[df['id_renewal_days_issue'] <= 20 * 366, 'id_renewal_days_delay'] = -1
    df.loc[df['id_renewal_days_issue'] > 20 * 366, 'id_renewal_days_delay'] = \
            df.loc[df['id_renewal_days_issue'] > 20 * 366, 'id_renewal_days'].values - \
            df.loc[df['id_renewal_days_issue'] > 20 * 366, 'id_renewal_days_issue']
    
    df['income_per_person'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
    
    ft_list = ['id_renewal_days_delay', 'income_per_person']
    return df, ft_list


def fe_bureau(df, period = 30):
    """
    period: number of days
    """
    ft_list = []
    
    df.sort_values(['SK_ID_CURR', 'DAYS_CREDIT'], ascending=False, inplace=True)
    groupby = df.groupby(by=['SK_ID_CURR'])
    features = pd.DataFrame({'SK_ID_CURR': df['SK_ID_CURR'].unique()})
    
    g = groupby['DAYS_CREDIT'].agg('count').reset_index()
    g.rename(index=str, columns={'DAYS_CREDIT': 'bureau_number_of_past_loans'}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')

#     g = groupby['CREDIT_TYPE'].agg('nunique').reset_index()
#     g.rename(index=str, columns={'CREDIT_TYPE': 'bureau_number_of_loan_types'}, inplace=True)
#     features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
    g = groupby['AMT_CREDIT_SUM_DEBT'].agg('sum').reset_index()
    g.rename(index=str, columns={'AMT_CREDIT_SUM_DEBT': 'bureau_total_customer_debt'}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
    g = groupby['AMT_CREDIT_SUM'].agg('sum').reset_index()
    g.rename(index=str, columns={'AMT_CREDIT_SUM': 'bureau_total_customer_credit'}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
#     features['bureau_debt_credit_ratio'] = \
#         features['bureau_total_customer_debt'] / features['bureau_total_customer_credit']
    
#     features['bureau_average_of_past_loans_per_type'] = \
#         features['bureau_number_of_past_loans'] / features['bureau_number_of_loan_types']
    
    
    feature_name = 'last_{}_'.format(period) + 'CNT_CREDIT_PROLONG' + '_sum'
    gr_period = df[df['DAYS_CREDIT'] >= (-1) * period].groupby(by=['SK_ID_CURR'])
    g = gr_period['CNT_CREDIT_PROLONG'].agg('sum').reset_index()
    g.rename(index=str, columns={'CNT_CREDIT_PROLONG': feature_name}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
#     ft_list.extend(['bureau_debt_credit_ratio', 'bureau_average_of_past_loans_per_type', feature_name])
    ft_list.extend([feature_name])

    return features, ft_list

def fe_bureau_balance(df, period = 2):
    """
    period: number of months
    """
    def _status_to_int(status):
        if status in ['X', 'C']:
            return 0
        if pd.isnull(status):
            return np.nan
        return int(status)
    
    ft_list = []
    df['bureau_balance_dpd_level'] = df['STATUS'].apply(_status_to_int)
    
    features = pd.DataFrame({'SK_ID_BUREAU': df['SK_ID_BUREAU'].unique()})
    
    feature_name = 'last_{}_'.format(period) + 'bureau_balance_dpd_level' + '_sum'
    gr_period = df[df['MONTHS_BALANCE'] >= (-1) * period].groupby(by=['SK_ID_BUREAU'])
    g = gr_period['bureau_balance_dpd_level'].agg('sum').reset_index()
    g.rename(index=str, columns={'bureau_balance_dpd_level': feature_name}, inplace=True)
    features = features.merge(g, on=['SK_ID_BUREAU'], how='left')
    
    ft_list.extend([feature_name])
    
    return features, ft_list


def fe_previous_application(df):
    
    ft_list = []
    
    features = pd.DataFrame({'SK_ID_CURR': df['SK_ID_CURR'].unique()})
    df_sorted = df.sort_values(['SK_ID_CURR', 'DAYS_DECISION'])
    df_sorted['refused'] = (df_sorted['NAME_CONTRACT_STATUS'] == 'Refused').astype('int')
    
    df_sorted_groupby = df_sorted.groupby(by=['SK_ID_CURR'])
    
    g = df_sorted_groupby['CHANNEL_TYPE'].last().reset_index()
    g.rename(index=str, columns={'CHANNEL_TYPE': 'previous_application_channel_type'}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')

    g = df_sorted_groupby['refused'].mean().reset_index()
    g.rename(index=str, columns={'refused': 'previous_application_fraction_of_refused_applications'}, inplace=True)
    features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
    ft_list.extend(['previous_application_channel_type', 'previous_application_fraction_of_refused_applications'])
    return features, ft_list


def fe_credit_card(df):
    def credit_card_dynamic_features(self, credit_card, **kwargs):
        features = pd.DataFrame({'SK_ID_CURR': credit_card['SK_ID_CURR'].unique()})

        credit_card_sorted = credit_card.sort_values(['SK_ID_CURR', 'MONTHS_BALANCE'])

        groupby = credit_card_sorted.groupby(by=['SK_ID_CURR'])
        credit_card_sorted['credit_card_monthly_diff'] = groupby['AMT_BALANCE'].diff()
        groupby = credit_card_sorted.groupby(by=['SK_ID_CURR'])

        g = groupby['credit_card_monthly_diff'].agg('mean').reset_index()
        features = features.merge(g, on=['SK_ID_CURR'], how='left')

        return features

    ft_list = []
    df['number_of_installments'] = df.groupby(by=['SK_ID_CURR', 'SK_ID_PREV'])['CNT_INSTALMENT_MATURE_CUM'].agg('max').reset_index()['CNT_INSTALMENT_MATURE_CUM']
    features = pd.DataFrame({'SK_ID_CURR': df['SK_ID_CURR'].unique()})
    groupby = df.groupby(by=['SK_ID_CURR'])
    n_installs = groupby['number_of_installments'].agg('sum').reset_index()
    n_installs.rename(index=str, columns={'number_of_installments': 'credit_card_total_installments'}, inplace=True)
    features = features.merge(n_installs, on=['SK_ID_CURR'], how='left')
    
    n_loans = groupby['SK_ID_PREV'].agg('nunique').reset_index()
    n_loans.rename(index=str, columns={'SK_ID_PREV': 'credit_card_number_of_loans'}, inplace=True)
    features = features.merge(n_loans, on='SK_ID_CURR', how='left')
    features['credit_card_installments_per_loan'] = features['credit_card_total_installments'] / features['credit_card_number_of_loans']
    ft_list.extend(['credit_card_total_installments', 'credit_card_number_of_loans', 'credit_card_installments_per_loan'])
    
    amt_atm = groupby['AMT_DRAWINGS_ATM_CURRENT'].agg('sum').reset_index()
    amt_atm.rename(index=str, columns={'AMT_DRAWINGS_ATM_CURRENT': 'credit_card_drawings_atm'}, inplace=True)
    features = features.merge(amt_atm, on=['SK_ID_CURR'], how='left')

    amt_current = groupby['AMT_DRAWINGS_CURRENT'].agg('sum').reset_index()
    amt_current.rename(index=str, columns={'AMT_DRAWINGS_CURRENT': 'credit_card_drawings_total'}, inplace=True)
    features = features.merge(amt_current, on=['SK_ID_CURR'], how='left')
    features['credit_card_cash_card_ratio'] = features['credit_card_drawings_atm'] / features['credit_card_drawings_total']
    ft_list.extend(['credit_card_drawings_atm', 'credit_card_drawings_total', 'credit_card_cash_card_ratio'])
    
    df_sorted = df.sort_values(['SK_ID_CURR', 'MONTHS_BALANCE'])

    groupby = df_sorted.groupby(by=['SK_ID_CURR'])
    df_sorted['credit_card_monthly_diff'] = groupby['AMT_BALANCE'].diff()
    groupby = df_sorted.groupby(by=['SK_ID_CURR'])

    g = groupby['credit_card_monthly_diff'].agg('mean').reset_index()
    features = features.merge(g, on=['SK_ID_CURR'], how='left')
    
    ft_list.append('credit_card_monthly_diff')
    return features, ft_list


def fe_pos_cash(df, period=12):
#     df['is_contract_status_completed'] = df['NAME_CONTRACT_STATUS'] == 'Completed'
    df['pos_cash_paid_late'] = (df['SK_DPD'] > 0).astype(int)
    df['pos_cash_paid_late_with_tolerance'] = (df['SK_DPD_DEF'] > 0).astype(int)

    features = pd.DataFrame({'SK_ID_CURR': df['SK_ID_CURR'].unique()})
    
    groupby = df[df['MONTHS_BALANCE'] >= (-1) * period].groupby(['SK_ID_CURR'])    
    late_cash = groupby['pos_cash_paid_late'].agg('sum').reset_index()
    late_cash.rename(index=str, columns={'pos_cash_paid_late': f'pos_cash_paid_late_{period}_cnt'}, inplace=True)
    features = features.merge(late_cash, on=['SK_ID_CURR'], how='left')
    dpd = groupby['SK_DPD'].agg('sum').reset_index()
    dpd.rename(index=str, columns={'SK_DPD': f'SK_DPD_{period}_sum'}, inplace=True)
    features = features.merge(dpd, on=['SK_ID_CURR'], how='left')
    
    last_installments_ids = df[df['MONTHS_BALANCE'] == df['MONTHS_BALANCE'].max()]['SK_ID_PREV']
    groupby = df[df['SK_ID_PREV'].isin(last_installments_ids)].groupby(['SK_ID_CURR'])  
    late_pay = groupby['pos_cash_paid_late'].agg('sum').reset_index()
    late_pay.rename(index=str, columns={'pos_cash_paid_late': f'pos_cash_paid_late_last_cnt'}, inplace=True)
    features = features.merge(late_pay, on=['SK_ID_CURR'], how='left')
    dpd = groupby['SK_DPD'].agg('sum').reset_index()
    dpd.rename(index=str, columns={'SK_DPD': f'SK_DPD_last_sum'}, inplace=True)
    features = features.merge(dpd, on=['SK_ID_CURR'], how='left')
    
    ft_list = [f'pos_cash_paid_late_{period}_cnt', f'SK_DPD_{period}_sum', 'pos_cash_paid_late_last_cnt', 'SK_DPD_last_sum']
    return features, ft_list


def fe_install(df, period=30):
    df['installment_paid_late_in_days'] = df['DAYS_ENTRY_PAYMENT'] - df['DAYS_INSTALMENT']
    df['installment_paid_late'] = (df['installment_paid_late_in_days'] > 0).astype(int)
    df['installment_paid_over_amount'] = df['AMT_PAYMENT'] - df['AMT_INSTALMENT']
    df['installment_paid_over'] = (df['installment_paid_over_amount'] > 0).astype(int)
    
    features = pd.DataFrame({'SK_ID_CURR': df['SK_ID_CURR'].unique()})
    groupby = df[df['DAYS_INSTALMENT'] > (-1) * period].groupby(['SK_ID_CURR'])    
    late_pay = groupby['installment_paid_late'].agg('count').reset_index()
    late_pay.rename(index=str, columns={'installment_paid_late': f'installment_paid_late_{period}_cnt'}, inplace=True)
    features = features.merge(late_pay, on=['SK_ID_CURR'], how='left')
    
    late_pay_amt = groupby['installment_paid_late_in_days'].agg('sum').reset_index()
    late_pay_amt.rename(index=str, columns={'installment_paid_late_in_days': f'installment_paid_late_{period}_sum'}, inplace=True)
    features = features.merge(late_pay_amt, on=['SK_ID_CURR'], how='left')
    
    over_pay = groupby['installment_paid_over'].agg('count').reset_index()
    over_pay.rename(index=str, columns={'installment_paid_over': f'installment_paid_over_{period}_cnt'}, inplace=True)
    features = features.merge(over_pay, on=['SK_ID_CURR'], how='left')
    
    over_pay_amt = groupby['installment_paid_over_amount'].agg('sum').reset_index()
    over_pay_amt.rename(index=str, columns={'installment_paid_over_amount': f'installment_paid_over_{period}_sum'}, inplace=True)
    features = features.merge(over_pay_amt, on=['SK_ID_CURR'], how='left')
    
    ft_list = [f'installment_paid_late_{period}_cnt', f'installment_paid_late_{period}_sum', f'installment_paid_over_{period}_cnt', 
               f'installment_paid_over_{period}_sum']
    return features, ft_list



