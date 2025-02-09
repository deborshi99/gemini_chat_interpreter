import os
import glob

def get_df_info_as_dict(df):
    """Convert DataFrame info() to a dictionary containing column info"""
    info_dict = {
        'columns': {},
        'total_rows': len(df),
        'memory_usage': df.memory_usage(deep=True).sum(),
    }
    
    for column in df.columns:
        info_dict['columns'][column] = {
            'dtype': str(df[column].dtype),
            'non_null_count': df[column].count(),
            'null_count': df[column].isnull().sum(),
            'memory_usage': df[column].memory_usage(deep=True)
        }
    
    return info_dict


def get_latest_folder_and_file(base_path):
    """Get the latest folder and the latest file inside that folder."""
    # Get all folders in the base path
    folders = [f for f in glob.glob(base_path + "/*") if os.path.isdir(f)]
    
    if not folders:
        return None, None

    # Get the latest folder based on modification time
    latest_folder = max(folders, key=os.path.getmtime)
    
    # Get all files in the latest folder
    files = [f for f in glob.glob(latest_folder + "/*") if os.path.isfile(f)]
    
    if not files:
        return latest_folder, None

    # Get the latest file based on modification time
    latest_file = max(files, key=os.path.getmtime)
    
    return latest_folder, latest_file