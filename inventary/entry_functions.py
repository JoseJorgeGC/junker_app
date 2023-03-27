def rename_file(file, id,date):
    file_sufix = file.name.split('.')[-1]
    file_name = date + '-' + id + '.' + file_sufix
    file.name = file_name
    
    return file