import pandas as pd
import numpy as np

from typing import Optional, List
from IPython.display import display


def show_file_change_proneness(con, period_type: Optional[str] = None, start_date: Optional[str] = None,
                               end_date: Optional[str] = None, file_name_list: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Displays a table with the change proneness of the project files during a given time window.

    Parameters:
      period_type: 'm','w'
      start_date: date format '12-11-2019'
      end_date: date format '12-11-2019'
      file_name_list: Optional[List[str]]

    Returns:
      df: dataframe with 
    """
    if period_type == 'w':
        sql_statement = """select
        file_name,
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1 as iso_week,
        count(*) as changes_in_week
        from file_commit
        group by 
        file_name,
        strftime('%Y', date(commit_commiter_datetime)),
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1;"""
        df = pd.read_sql_query(sql_statement, con)

        df['yr_wk'] = df.apply(lambda row: ''.join([str(row.iso_yr),
                               '-', str(row.iso_week)]), axis=1)
        pdf = df[['yr_wk', 'file_name', 'changes_in_week']]
        changes_matrix = pd.pivot_table(pdf, index=['file_name'], values='changes_in_week',
                                        columns=['yr_wk'], aggfunc=np.sum)
        changes_matrix_styler = changes_matrix.style.background_gradient(cmap='viridis')\
            .set_properties(**{'font-size': '5px'})
        display(changes_matrix_styler)
        return changes_matrix

    else:
        sql_statement = """select
        file_name,
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        strftime('%m', date(commit_commiter_datetime)) as iso_month,
        count(*) as changes_in_month
        from file_commit
        group by 
        file_name,
        strftime('%Y', date(commit_commiter_datetime)),
        strftime('%m', date(commit_commiter_datetime));"""
        df_m = pd.read_sql_query(sql_statement, con)

        df_m['yr_m'] = df_m.apply(lambda row: ''.join(
            [str(row.iso_yr), '-', str(row.iso_month)]), axis=1)
        changes_matrix_m = pd.pivot_table(df_m, index=['file_name'], values='changes_in_month',
                                          columns=['yr_m'], aggfunc=np.sum)
        changes_matrix_m_styler = changes_matrix_m.style.background_gradient(cmap='viridis')\
            .set_properties(**{'font-size': '5px'})
        display(changes_matrix_m_styler)
        return changes_matrix_m


def plot_change_distribution_file(con_analytics_db):
    sql_statement = """select
    file_name,
    count(*) as nr_changes
    from file_commit
    group by 
    file_name;"""
    df = pd.read_sql_query(sql_statement, con_analytics_db)
    dd = df.hist()
    display(dd)
    return df   


def show_component_change_proneness(con, period_type: Optional[str] = None, start_date: Optional[str] = None,
                               end_date: Optional[str] = None, file_name_list: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Displays a table with the change proneness aggregating files on their file_path during a given time window.

    Parameters:
      period_type: 'm','w'
      start_date: date format '12-11-2019'
      end_date: date format '12-11-2019'
      file_name_list: Optional[List[str]]

    Returns:
      df: dataframe with 
    """
    if period_type == 'w':
        sql_statement = """select
        file_dir_path,
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1 as iso_week,
        count(*) as changes_in_week
        from file_commit
        where change_type != 'ModificationType.DELETE'
        group by 
        file_dir_path,
        strftime('%Y', date(commit_commiter_datetime)),
        (strftime('%j', date(commit_commiter_datetime, '-3 days', 'weekday 4')) - 1) / 7 + 1;"""
        df = pd.read_sql_query(sql_statement, con)

        df['yr_wk'] = df.apply(lambda row: ''.join([str(row.iso_yr),
                               '-', str(row.iso_week)]), axis=1)
        pdf = df[['yr_wk', 'file_dir_path', 'changes_in_week']]
        changes_matrix = pd.pivot_table(pdf, index=['file_dir_path'], values='changes_in_week',
                                        columns=['yr_wk'], aggfunc=np.sum)
        changes_matrix_styler = changes_matrix.style.background_gradient(cmap='viridis')\
            .set_properties(**{'font-size': '5px'})
        display(changes_matrix_styler)
        return changes_matrix

    else:
        sql_statement = """select
        file_dir_path,
        strftime('%Y', date(commit_commiter_datetime)) as iso_yr,
        strftime('%m', date(commit_commiter_datetime)) as iso_month,
        count(*) as changes_in_month
        from file_commit
        where change_type != 'ModificationType.DELETE'
        group by 
        file_dir_path,
        strftime('%Y', date(commit_commiter_datetime)),
        strftime('%m', date(commit_commiter_datetime));"""
        df_m = pd.read_sql_query(sql_statement, con)

        df_m['yr_m'] = df_m.apply(lambda row: ''.join(
            [str(row.iso_yr), '-', str(row.iso_month)]), axis=1)
        changes_matrix_m = pd.pivot_table(df_m, index=['file_dir_path'], values='changes_in_month',
                                          columns=['yr_m'], aggfunc=np.sum)
        changes_matrix_m_styler = changes_matrix_m.style.background_gradient(cmap='viridis')\
            .set_properties(**{'font-size': '5px'})
        display(changes_matrix_m_styler)
        return changes_matrix_m