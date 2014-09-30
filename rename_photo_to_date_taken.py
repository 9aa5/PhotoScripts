#!python

import os, sys
import re
import hashlib
lib_path = os.path.abspath('./exif-py')
sys.path.append(lib_path)
import EXIF

import os
import datetime


rename_list = {}
# key is the new name
# value is tuple: dir, old name, new_name_has_collision

class PhotoNameChanger():
   def __init__(self, start_dir, ext_filter, file_pattern):
      self.start_dir = start_dir
      self.ext_filter = ext_filter
      self.file_pattern = file_pattern
      self.new_filename_list = {}

   def base_name_contains(self, base_name, patterns):
      if not patterns:
         return True
      for pattern in patterns:
         if re.match(pattern, base_name):
            return True
      return False

   def filelist_generator(self):
      for dirname, dirnames, filenames in os.walk(self.start_dir):
         for filename in filenames:
            base_name, file_ext = os.path.splitext(filename)
            # file_ext contains the '.', e.g. '.jpg'
            if (len(file_ext) > 1 and file_ext[1:].lower() in self.ext_filter and
                self.base_name_contains(base_name, self.file_pattern)):
               yield os.path.join(dirname, filename)
         # remove unwanted dir names for further traversing.
         # e.g. if '.git' in dirnames:
         # dirnames.remove('.git')

   def get_time_and_model(self, filename):
      try:
         file=open(filename, 'rb')
      except:
         print "'%s': Cannot open for reading.\n" % filename
      data = EXIF.process_file(file, details=False, debug=False)
      if not data:
         print '%s: No EXIF data found' % filename
      date = data.get('EXIF DateTimeOriginal')
      if not date:
         date = data.get('Image DateTime')
      model = data.get('Image Model')
      file.close()
      return date, model

   def add_new_filename(self, filename, time_taken, model):
      key = time_taken
      key = key.replace(':', '')
      key = key.replace(' ', '-')
      key = model[:2] + key
      new_key = key

      if new_key in self.new_filename_list.keys():
         print '%s: Duplicate datestamp with %s' % (filename,
            self.new_filename_list[key])

      num = 1
      while new_key in self.new_filename_list.keys():
         new_key = key + '-' + str(num)
         num += 1
      self.new_filename_list[new_key] = filename

   def gen_request_file(self):
      for file_name in self.filelist_generator():
         time_taken, model = self.get_time_and_model(file_name)
         if not time_taken or not model:
            print 'ERROR: Cannot extra info for %s' % file_name
         else:
            self.add_new_filename(file_name, str(time_taken), str(model))
      for new_file_name in self.new_filename_list:
         old_file_name = self.new_filename_list[new_file_name]
         old_file_path = os.path.split(old_file_name)[0]
         print 'mv %s %s.JPG' % (self.new_filename_list[new_file_name],
                                 os.path.join(old_file_path, new_file_name))

# Parameters: New Prefix name: e.g. SH-,
#             File name filter.e.g. DSCN, IMG_, can be a collection.

def main():
   ext_filter = ['jpeg', 'jpg']
   # Rename file with this type of strange name: DB639A6D-FB0B-4892-ACBF-2A95CDCEFCA0.JPG
   file_patterns = ['[A-Z0-9]{8,8}-[A-Z0-9]{4,4}-[A-Z0-9]{4,4}-[A-Z0-9]{4,4}-[A-Z0-9]{12,12}']
   starting_dir = '.'
   if len(sys.argv) >= 2:
      starting_dir = sys.argv[1]
   name_changer = PhotoNameChanger(starting_dir, ext_filter, file_patterns)
   name_changer.gen_request_file()

main()
