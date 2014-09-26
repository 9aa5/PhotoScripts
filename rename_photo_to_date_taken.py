#!python

import os, sys
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

   def base_name_contains(self, base_name, prefixes):
      if not prefixes:
         return True
      for prefix in prefixes:
         if base_name.lower().startswith(prefix):
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
      date = data['EXIF DateTimeOriginal']
      if not date:
         date = data['Image DateTime']
      model = data['Image Model'].printable
      file.close()
      return date, model

   def add_new_filename(self, filename, time_taken, model):
      key = time_taken.printable
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
         self.add_new_filename(file_name, time_taken, model)
      for new_file_name in self.new_filename_list:
         print 'mv %s %s.JPG' % (self.new_filename_list[new_file_name], new_file_name)

# Parameters: New Prefix name: e.g. SH-,
#             File name filter.e.g. DSCN, IMG_, can be a collection.

def main():
   ext_filter = ['jpeg', 'jpg']
   # file_pattern = ['dsc', 'img', 'picture']
   file_pattern = []
   starting_dir = '.'
   if len(sys.argv) >= 2:
      starting_dir = sys.argv[1]
   name_changer = PhotoNameChanger(starting_dir, ext_filter, file_pattern)
   name_changer.gen_request_file()

main()
