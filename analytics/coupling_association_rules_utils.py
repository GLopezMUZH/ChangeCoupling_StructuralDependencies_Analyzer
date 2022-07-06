# %%
from typing import List
from re import search
import pandas as pd
import apyori
from typing import List
from itertools import combinations


# %%
def calculate_structural_coupling_rates(
    con_analytics_db,
    records,
    min_confidence=0.1,
    min_support=0.1,
    print_rules=False,
    calc_structural_dependency=True,
):
    rules = apyori.apriori(
        records, min_confidence=min_confidence, min_support=min_support
    )
    rules_list = list(rules)
    nr_rules = len(rules_list)
    nr_struct_coupling = 0
    itemsets_list = []
    for r in rules_list:
        if len(list(r.items)) > 1:
            output_list = [i.replace("'", "") for i in list(r.items)]
            if calc_structural_dependency:
                d = exist_import_dependency(con_analytics_db, output_list)
                if d[0][0] > 0:
                    nr_struct_coupling += 1
            if print_rules:
                print(output_list, d[0][0])
            itemsets_list.append(output_list)

    r = 0 if nr_rules == 0 else nr_struct_coupling / nr_rules
    if calc_structural_dependency:
        print(
            "Nr rules {0}, with structural coupling {1}, {2}".format(
                nr_rules, nr_struct_coupling, round(r, 2)
            )
        )
    else:
        print("Nr rules {0}".format(nr_rules))
    return rules_list, itemsets_list


def show_component_change_proneness(records, min_confidence=0.1, min_support=0.1):
    rules = apyori.apriori(
        records, min_confidence=min_confidence, min_support=min_support
    )
    rules_list = list(rules)
    itemsets_list = []
    for r in rules_list:
        if len(list(r.items)) > 1:
            output_list = [i.replace("'", "") for i in list(r.items)]
            itemsets_list.append(output_list)
    return itemsets_list


def get_records(con_graph_db, df_column_name, sql_statement, min_items=2):
    df = pd.read_sql_query(sql_statement, con_graph_db)
    print("df len: ", len(df))
    # stack functionality removes NaNs to generate the nested list:
    records_concats = (
        pd.DataFrame(df[df_column_name])
        .stack()
        .groupby(level=0)
        .apply(list)
        .values.tolist()
    )
    records = []
    for r in records_concats:
        records.append(list(r[0].split(sep=",")))
    print("records len: ", len(records))
    pruned_records = []
    for r in records:
        if len(r) > min_items:
            pruned_records.append(r)
    print("pruned_records len: ", len(pruned_records))
    return records, pruned_records, df


def show_transactions_containing_items(
    df, col_name: str, items_list: List[str], print_elems=True
):
    """
    Displays the summarized occurences of the items in the list troughout the whole set of transactions.
    ind are the occurences where the item appeared, independently of the successor item,
    dep are the occurences where the successor item appeared following the appearance of the predecesor

    """
    if len(items_list) == 2:
        transactions_2_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 3:
        transactions_3_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 4:
        transactions_4_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 5:
        transactions_5_elem_rule(df, col_name, items_list, print_elems)


def transactions_2_elem_rule(
    df, col_name: str, items_list: List[str], print_elems=True
):
    i = 0
    j = 0
    jj = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if print_elems:
                    print(df[col_name][ind])

    print(
        "Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 2ind: {3}".format(
            len(df), i, j, jj
        )
    )


def transactions_3_elem_rule(
    df, col_name: str, items_list: List[str], print_elems=True
):
    i = 0
    j = 0
    k = 0
    jj = 0
    kk = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if print_elems:
                        print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3},
    2ind: {4}, 3ind: {5}""".format(
        len(df), i, j, k, jj, kk
    )
    print(msg)


def transactions_4_elem_rule(
    df, col_name: str, items_list: List[str], print_elems=True
):
    i = 0
    j = 0
    k = 0
    l = 0
    jj = 0
    kk = 0
    ll = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1
        if search(items_list[3], df[col_name][ind]):
            ll += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if search(items_list[3], df[col_name][ind]):
                        l += 1
                        if print_elems:
                            print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3}, 4dep: {4},
    2ind: {5}, 3ind: {6}, 4ind: {7}""".format(
        len(df), i, j, k, l, jj, kk, ll
    )
    print(msg)


def transactions_5_elem_rule(
    df, col_name: str, items_list: List[str], print_elems=True
):
    i = 0
    j = 0
    k = 0
    l = 0
    m = 0
    jj = 0
    kk = 0
    ll = 0
    mm = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1
        if search(items_list[3], df[col_name][ind]):
            ll += 1
        if search(items_list[4], df[col_name][ind]):
            mm += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if search(items_list[3], df[col_name][ind]):
                        l += 1
                        if search(items_list[4], df[col_name][ind]):
                            m += 1
                            if print_elems:
                                print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3}, 4dep: {4}, 5dep: {5}
    2ind: {6}, 3ind: {7}, 4ind: {8}, 5ind: {9}""".format(
        len(df), i, j, k, l, m, jj, kk, ll, mm
    )
    print(msg)


def exist_import_dependency(con_analytics_db, l_items: List):
    """
    Returns list with format [exist_dependency, list_of_items]
    where exist_dependency = 1 if there is a structural dependency and 0 if not
    """
    r = []
    list_combinations = list(combinations(l_items, 2))
    dep = 0
    for c in list_combinations:
        dep = exist_import_dependency_2_items(con_analytics_db, c[0], c[1])
        if dep == 1:
            break
    r.append([dep, l_items])
    return r


def exist_import_dependency_2_items(
    con_analytics_db, A_file_name: str, B_file_name: str
):
    """
    File B exists in the import list of file A
    """
    obj = 0
    cur = con_analytics_db.cursor()
    sql_statement = """select ifnull(sum(b_exists),0) r_exists from 
    (
    select 1 as b_exists from file_import a
        where a.file_name = '{0}'
        and EXISTS(
            select b.file_pkg
            from file_pkg b
            where b.file_name = '{1}'
            and b.class_pkg = a.import_file_pkg)
    union          
    select 1 as b_exists from file_import a
        where a.file_name = '{1}'
        and EXISTS(
            select b.file_pkg
            from file_pkg b
            where b.file_name = '{0}'
            and b.class_pkg = a.import_file_pkg)
    union
    select 
    (count(file_pkg) - count(distinct(file_pkg)))==1 as b_exists
    from file_pkg where file_name in('{0}','{1}')	
    );""".format(
        A_file_name, B_file_name
    )
    cur.execute(sql_statement)
    obj = cur.fetchone()
    con_analytics_db.commit()
    cur.close()
    return obj[0]


def get_artifact_couplings(
    records, artifact_name, min_confidence=0.05, min_support=0.05
):
    """
    Returns list with itemsets that contain the given artifact_name when analyzing
    apriori association rules with the given support and confidence thresholds
    """
    itemsets_list = get_coupling_itemsets(
        records, min_confidence=min_confidence, min_support=min_support
    )

    itemsets_including = []
    for l in itemsets_list:
        if artifact_name in l:
            itemsets_including.append(l)

    return itemsets_including
