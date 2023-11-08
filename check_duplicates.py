# This file contains functions specific to checking for image uniqueness after downloading
from os import listdir, mkdir, path, remove, rename
from PIL import Image, UnidentifiedImageError
import numpy as np
import sys



def return_img_obj(path):
    try:
        return Image.open(path)
    except UnidentifiedImageError:
        return None



def check_other_files(img1, fol, deletions):

    # Sort files in fol
    sorted_files = sorted(listdir(fol), key=lambda x: int(x.split('.')[0]))

    # Iterate through files
    for file in sorted_files:

        if path.exists(fol + file):
                
            # Return PIL Image obj
            img2 = return_img_obj(fol + file)

            # If returned
            if img2 != None:

                # Check whether images are near identical
                result = is_equal(img1, img2)

                # If result is boolean
                if result == True or result == False:

                    # If images are near identical
                    if result:

                        # If image filenames aren't identical
                        if img1.filename != img2.filename:

                            # Delete file
                            try:
                                remove(img2.filename)
                                message = f'Deleted {img2.filename}'
                                log(message, log_file)
                                print(message)
                                deletions += 1
                            except Exception as e:
                                message = 'Tried to delete {}, experienced {}'.format(img2.filename, e)
                                log(message, log_file)
                                print(message)
                
                # Otherwise take unresizeable result and delete
                elif np.array_equal(result, img1) or np.array_equal(result, img2):
                    remove(result.filename)
                    message = 'Could not resize, deleted ' + result.filename
                    log(message, log_file)
                    print(message)
                    deletions += 1
    
    # Return count of deletions
    return deletions



def is_equal(img1, img2):
    # Takes PIL.Image objects as input

    # Define size
    size = (400, 400)

    # Resize imgs
    try:
        img1 = img1.resize(size)
    except OSError:
        return img1
    try:
        img2 = img2.resize(size)
    except OSError:
        return img2 

    # Convert imgs to grayscale
    gray1 = img1.convert('L')
    gray2 = img2.convert('L')

    # Convert imgs to arrays
    array1 = np.array(gray1).flatten()
    array2 = np.array(gray2).flatten()

    # Compute the mean squared error
    mse = np.mean((array1 - array2) ** 2)

    # Low mse indicates images almost identical, returns boolean
    return mse < 25



def log(message, log_file):
    
    # Open log file
    with open(log_file, 'a') as f:
        
        # Write message + newline
        f.write(message + '\n')



def get_log_file():

    # Create log directory if nonexistant
    if not path.exists('image_heap/logs'):
        mkdir('image_heap/logs')

    if '--reuse_log' not in sys.argv:
        # Define variables
        name, i = None, 0

        # Continue to rename 'name' until no file is found in 'logs/' with same name
        while name == None or path.exists(name):
            i += 1
            name = 'image_heap/logs/check_log_{}.txt'.format(i)
        
        return name

    # if --reuse_log was specified as an argument during cmd line execution
    else:
        files_amt = len(listdir('image_heap/logs/'))
        return 'image_heap/logs/check_log_{}.txt'.format(files_amt)



if __name__ == '__main__':

    print('''
    check_duplicates checks 
    - image_heap/unchecked/positive/
    - image_heap/unchecked/negative/
    for duplicate images (only in their respective folders)
    and moves unique files to corresponding image_heap/checked/ folders
    * Program can be run with the option '--reuse_log' to use the most recently
    created log instead of creating a new one

    >> To cancel cleaning, press 'CRTL c' together <<
    - You can resume cleaning by rerunning the execution (consider using '--reuse_log')
    ''')

    # Reassure user program is starting
    print('\nStarting to check for duplicates...')

    # Define parent and folders, dst_folders
    parent = 'image_heap/'
    folders = [parent + 'unchecked/positive/', parent + 'unchecked/negative/']
    dst_folders = [parent + 'checked/positive/', parent + 'checked/negative/']

    # Define log file
    log_file = get_log_file()

    try:

        # Iterate through both folders
        for fol in folders:

            print('\nNow checking ' + fol + '\n')

            # Define dst_fol
            if 'positive' in fol:
                dst_fol = dst_folders[0]
            else:
                dst_fol = dst_folders[1]

            # Define deletions
            deletions = 0

            # Sort files in fol
            sorted_files = sorted(listdir(fol), key=lambda x: int(x.split('.')[0]))

            # Iterate through sorted files
            for file in sorted_files:

                if path.exists(fol + file):

                    # Create PIL Image obj of file
                    img1 = return_img_obj(fol + file)

                    # If img1 is PIL Image obj
                    if img1 != None:
                        
                        # Check other files in fol for duplicates
                        deletions = check_other_files(img1, fol, deletions)

                        # Get new name for image file
                        new_name, i = None, 1
                        while new_name == None or path.exists(dst_fol + new_name):
                            new_name = str(i) + '.jpg'
                            i += 1

                        # Attempt to move file
                        try:
                            rename(fol + file, dst_fol + new_name)
                            message = 'Successfully moved ' + fol + file
                            log(message, log_file)
                            print(message)
                        except PermissionError:
                            message = 'PermissionError on ' + fol + file
                            log(message, log_file)
                            print(message)
                    
                    # If PIL Image obj creation wasn't successful
                    else:
                        remove(fol + file)
                        deletions += 1
                        message = 'Could not open and deleted ' + fol + file
                        log(message, log_file)
                        print(message)

            # Log and print results
            unique_imgs = len(listdir(dst_fol))

            messages = [
                '\n\nEnded check in {}. Results:'.format(fol),
                'Unique images in {}: {}'.format(dst_fol, str(unique_imgs)),
                'Deletions: ' + str(deletions) + '\n\n'
            ]
            for mes in messages:
                log(mes, log_file)
                print(mes)

    except KeyboardInterrupt:

        print('Cleaning interrupted.')
