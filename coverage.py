import numpy as np
import pandas as pd 


def application_stat(application, show_res=False):
	users = len(application['SK_ID_CURR'].unique())
	default_users = len(application[application['TARGET'] == 1]['SK_ID_CURR'].unique())
	if show_res:
		rows = len(application['SK_ID_CURR'])
		print("# rows in application table: ", rows)
		print("# users in application table: ", users)
		print("# default users in application table: ", default_users)
		ratio = default_users / users
		print("% default users in application table: ", ratio)
	return users, default_users

def application_coverage(application, right_table, table_name, key='SK_ID_CURR'):
	users, default_users = application_stat(application)
	rows = len(right_table[key])
	tab_users = len(right_table[key].unique())
	# print("# rows in", table_name, rows)
	# print("# users in", table_name, tab_users)
	joined_table = application.merge(right_table, on=key, how='inner')
	covered_users = len(joined_table[key].unique())
	print("# all users covered by", table_name, covered_users)
	covered_ratio = covered_users / users
	print("% all users covered by", table_name, covered_ratio)
	pos_covered_users = len(joined_table[joined_table['TARGET'] == 1][key].unique())
	print("# default users covered by", table_name, pos_covered_users)
	pos_covered_ratio = pos_covered_users / default_users
	print("% default users covered by", table_name, pos_covered_ratio)
