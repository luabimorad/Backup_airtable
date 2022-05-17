# Objective : create a airtable Back up in Python.
# - create the first back up,
# - compare directories,
# - compare data inside,
# - delete the old back up, if the data and attachment is the same


# 1. install api to read airtable

# pip install pyairtable

# 2. install api to read/shows attachments
# pip install pillow


# 3. import modules

import json  # to save data in json
import os  # to work with directories (operating system),operating mit directories
import urllib.request  # to work with attachments
import filecmp  # to compare directories
import shutil  # to compare files

from pyairtable import (
    Table,
    metadata,
)  # import class table in order to read tables and metadata from Airtable
from pathlib import Path  # import class to work , list directories inside
from datetime import datetime  # import datatime to compare time
from PIL import Image  # import image to work with attachments

# 4. Create a Main class
class TableBackup:
    # Konstructors
    def __init__(self,base_id,table_name):
        self.base_id = base_id
        self.table_name=table_name
    # Read the table in airtable
    def read_aritable(self):

        api_key = "keyscafR75XCFOj5x"

        table_example = Table(api_key, self.base_id, self.table_name)

        results = table_example.all()

        print(f"{len(results)} rows downloaded")

        return results

# 5. Save data and attachments in a date folder
        #Create folder with today date
    def create_data_folder(self, results):
        new_backup = (
            "backup"
            + "/"
            + datetime.today().isoformat(timespec="seconds").replace(":", "_")
        )
        os.makedirs(new_backup, exist_ok=True)
        # save the data
        for item in results:
            all_data = item["fields"]
        # json format
            with open(
                new_backup + "/" + str(item["fields"]["Id"]) + ".json", "w"
            ) as file:
                json.dump(all_data, file)

        return new_backup

    # Dowloand attachment and save
    def create_attach_folder(self, results, new_backup):
        for item in results:
            if "Attachments" in item["fields"]:
                attachments = item["fields"]["Attachments"]
                i = 0
                for attach in attachments:
                    print("downloading:", attach["url"])
                    urllib.request.urlretrieve(
                        attach["url"],
                        new_backup + "/" + str(item["fields"]["Id"]) + "_" + str(i) +  ".jpg",
                    )
                    i+=1

# 6. Compared back up and save the new back
    def compare(self, old_backup, new_backup):
        comparison = filecmp.dircmp(old_backup, new_backup)
        delete_old_backup = True
        # Check list of files
        if comparison.left_only or comparison.right_only:
        # Row number or attachments differ
            print(f"Different files structures. Previous backup: {comparison.left_only}. New backup: {comparison.right_only}")
            delete_old_backup = False
        else:
        # Check content of files
            match, missmatch, errors = filecmp.cmpfiles(
                old_backup, new_backup, comparison.common_files
            )
            if missmatch:
                print("different files contents for: ", missmatch)
                delete_old_backup = False

#7. Delete old back up when the back up are the same
        if delete_old_backup:
            print("Deleting old Back up")
            shutil.rmtree(old_backup)
        else:
            print("Keeping old backup")

    def run(self):
        rootdir = "backup"
        os.makedirs(rootdir, exist_ok=True)
        # Obtain the old Back up
        old_backup = None
        for path in Path(rootdir).iterdir():
            if path.is_dir():
                old_backup = path

        results = self.read_aritable()

        new_backup = self.create_data_folder(results)

        self.create_attach_folder(results, new_backup)

        if old_backup:
            self.compare(old_backup, new_backup)
        else:
            print("First Backup")


TableBackup("appfvIU1srFwN38Er","Example").run()
