import os
import glob

if __name__ == "__main__":
    dirpath = os.path.abspath("../../")
    total = 0
    lupdateCommand = "pyside-lupdate"
    nfiles = 0
    for path, folders, files in os.walk(dirpath):                
        archives = glob.glob(os.path.join(path, "*.py"))
        for filepath in archives:
            nfiles = nfiles + 1
            if not filepath in lupdateCommand:
                cf = file(filepath, "r")
                total = total + len(cf.readlines())
                lupdateCommand = "{0} {1}".format(lupdateCommand, filepath)
    lupdateCommand = lupdateCommand+ " -ts /home/igorznt/Desenvolvimento/neppo/moonstone/src/resources/locale/pt_BR/LC_MESSAGES/moonstone.ts"
    print total, nfiles    
    os.system(lupdateCommand)
