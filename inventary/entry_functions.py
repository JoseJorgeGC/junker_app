def rename_file(file, id, entry_date):
    file_sufix = file.name.split('.')[-1]
    file_name = str(entry_date) + '-' + id + '.' + file_sufix
    file.name = file_name
    
    return file