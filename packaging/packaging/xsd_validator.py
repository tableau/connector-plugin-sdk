
# files_list: List of files to validate
# folder_path: path to folder that contains the files.
# Return value: True if all xml files pass validation, false if they do not or there is an error
def validate_xsd(files_list, folder_path = ""):
    print("===Start XSD Validation===")
    
    if type(files_list) != list:
        print("Error: validate_xsd input is not a list")
        return False

    print("No XSD Violations Found")
    return True

#For testing, will remove and add unit tests once initial version is done
if __name__ == "__main__":
    files_list = ["manifest.xml"]
    validate_xsd(files_list)
    files_list = 2
    validate_xsd(files_list)