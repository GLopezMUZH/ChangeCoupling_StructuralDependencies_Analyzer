#from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend import frequent_patterns
from mlxtend.preprocessing import TransactionEncoder
import numpy as np
import pandas as pd


def get_rules_by_threshold(df, min_t=0.1, max_t=0.5, n=11, max_nr_rules=100):
    """
    Returns list of [threshold, nr_rules]
    """
    r = []
    for threshold in np.linspace(max_t,min_t,n):
        tmp = frequent_patterns.apriori(df, min_support=threshold, use_colnames=True)
        r.append([threshold, len(tmp)])
        if len(tmp)> max_nr_rules:
            break
    return r

def get_rules_by_threshold_on_commit_and_file(con_analytics_db, min_t=0.1, max_t=0.5, n=11, max_nr_rules=100):
    # for processing mlxtend apriori
    sql_statement = """select commit_hash, file_name from file_commit"""
    dfsql = pd.read_sql_query(sql_statement, con_analytics_db)
    df_hash = dfsql.groupby('commit_hash')['file_name'].apply(list)
    # generate scarce matrix
    te = TransactionEncoder()
    oht_ary = te.fit(df_hash).transform(df_hash, sparse=True)
    sparse_df = pd.DataFrame.sparse.from_spmatrix(oht_ary, columns=te.columns_)

    return get_rules_by_threshold(sparse_df, min_t, max_t, n, max_nr_rules)