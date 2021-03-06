#!python
import os, sys
import hashlib

def filelist_generator(start_dir, ext_list, prefix_list):
   def base_name_contains(base_name, prefixes):
      if not prefixes:
         return True
      for prefix in prefixes:
         if base_name.lower().startswith(prefix):
            return True
      return False

   for dirname, dirnames, filenames in os.walk(start_dir):
      ### print path to all subdirectories first.
      # for subdirname in dirnames:
      #    print os.path.join(dirname, subdirname)
      for filename in filenames:
         base_name, fileext = os.path.splitext(filename)
         # fileext contains the '.', e.g. '.jpg'
         if (len(fileext) > 1 and fileext[1:].lower() in ext_list and
             base_name_contains(base_name, prefix_list)):
            yield os.path.join(dirname, filename)
      # Advanced usage:
      # editing the 'dirnames' list will stop os.walk() from recursing into there.
      # don't go into any .git directories.
      # if '.git' in dirnames:
      #   dirnames.remove('.git')

class DupReport():
   def __init__(self, startDir, filter, file_pattern):
      self.startDir = startDir
      self.filter = filter
      self.file_pattern = file_pattern
      self.dup_list = [] # hash values of duplicated files.
      self.file_hash_list = {} # key: hash value, value: single file or a list of files.

   def compute_hash(self, file_path):
      return hashlib.sha256(open(file_path, 'rb').read()).digest()[:16]

   def same_size_files(self):
      filelist = filelist_generator(self.startDir, self.filter, self.file_pattern)
      file_size_list = {}
      size_duplicate = []
      for filepath in filelist:
         size_key = str(os.path.getsize(filepath))
         if size_key in file_size_list:
            if type(file_size_list[size_key]) is str:
               # The value is a single file, so this is a first time
               # collision.  Convert the single file into a list of files.
               files_with_same_size = []
               files_with_same_size.append(file_size_list[size_key])
               files_with_same_size.append(filepath)
               file_size_list[size_key] = files_with_same_size
            else:
               # The value is already a list, we just need to append
               # more size-duplicated file names.
               file_size_list[size_key].append(filepath)
         else:
            file_size_list[size_key] = filepath

      for file_size in file_size_list:
         if not (type(file_size_list[file_size]) is str):
            files_with_same_size = file_size_list[file_size]
            for file_path in files_with_same_size:
               size_duplicate.append(file_path)
      return size_duplicate

   def detect_dup_with_file_list(self, file_list):
      for filepath in file_list:
         hash_val = str(self.compute_hash(filepath))
         if hash_val in self.file_hash_list:
            if type(self.file_hash_list[hash_val]) is str:
               # The value is a single file, so this is a first time
               # collision.  Put this hash value onto to dup_list,
               # and convert the single file into a list of files.
               self.dup_list.append(hash_val)
               files_with_same_hash = []
               files_with_same_hash.append(self.file_hash_list[hash_val])
               files_with_same_hash.append(filepath)
               self.file_hash_list[hash_val] = files_with_same_hash
            else:
               # The value is already a list, we just need to append
               # more duplicated file names.
               self.file_hash_list[hash_val].append(filepath)
         else:
            self.file_hash_list[hash_val] = filepath

   def detect_dup(self):
      file_list = self.same_size_files()
      self.detect_dup_with_file_list(file_list)

   def detect_dup_brute_force(self):
      filelist = filelist_generator(self.startDir, self.filter, self.file_pattern)
      self.detect_dup_with_file_list(filelist)

   def print_dup(self):
      if not self.dup_list:
         print 'No duplication detected.'
      else:
         for hash_val in self.dup_list:
            print 'Duplication below:'
            files_with_same_hash = self.file_hash_list[hash_val]
            for file_path in files_with_same_hash:
               print '  %s' % file_path
            print

def main():
   filter = ['jpeg', 'jpg']
   # file_pattern = ['dsc', 'img', 'picture']
   file_pattern = []
   if len(sys.argv) == 1:
      startDir = '.'
   else:
      startDir = sys.argv[1]
   dup_reporter = DupReport(startDir, filter, file_pattern)
   dup_reporter.detect_dup()
   dup_reporter.print_dup()

main()
