import os
import send2trash
 
rootdir = os.environ['HOME'] + '/Nextcloud'

for dirpath, subdirs, files in os.walk(rootdir):
    for conflict_name in files:
        if " (conflicted copy " in conflict_name:
            path, ext = os.path.splitext(conflict_name)
            original_name = path[:path.find(" (conflicted copy ")] + ext

            if os.path.exists(os.path.join(dirpath, original_name)) == False:
                os.rename(os.path.join(dirpath, conflict_name), os.path.join(dirpath, original_name))
                continue
            
            print('Solving conflict in: %s' % os.path.join(dirpath, original_name))

            mtime_conflict = os.path.getmtime(os.path.join(dirpath, conflict_name))
            mtime_original = os.path.getmtime(os.path.join(dirpath, original_name))

            if mtime_conflict > mtime_original:
                send2trash.send2trash(os.path.join(dirpath, original_name))
                os.rename(os.path.join(dirpath, conflict_name), os.path.join(dirpath, original_name))
                print("\tConflict file is more recent")
            elif mtime_original > mtime_conflict:
                send2trash.send2trash(os.path.join(dirpath, conflict_name))
                print("\tOriginal file is more recent")
