import os
import pypandoc

#%% set up directory structure
dir = '/Users/nathaniel.hunt/Desktop/epub downloads/'
os.chdir(dir)
sub_dirs = [x for x in os.listdir(dir) if 'DS' not in x]
sub_dirs_full_path = [str(dir + x) for x in sub_dirs]

epub_tmp = '/usr/local/etc/epub_temp'
if 'epub_temp' not in os.listdir('/usr/local/etc/'):
    os.mkdir(epub_tmp)
html_tmp = '/usr/local/etc/html_tmp'
if 'html_tmp' not in os.listdir('/usr/local/etc/'):
    os.mkdir(html_tmp)

working_dir = '/Users/nathaniel.hunt/Desktop/epub converted/'
if 'epub converted' not in os.listdir('/Users/nathaniel.hunt/Desktop/'):
    os.mkdir(working_dir)
os.chdir(working_dir)

#%% iterate through all EPUBs and convert them to plaintext using pandoc
for d in sub_dirs_full_path:
    i = sub_dirs_full_path.index(d)
    dest_d = sub_dirs[i]
    if dest_d not in os.listdir(working_dir):
        os.mkdir(working_dir+dest_d)
    for file_tuple in os.walk(d):
        files = file_tuple[2]
        for f in files:
            if 'epub' in f:
                dest_file = working_dir + dest_d + '/' + f.split('.')[0] + '.txt'
                source = d + '/' + f
                if dest_file.split('/')[-1] not in os.listdir(working_dir + dest_d):
                    pypandoc.convert_file(source,to='plain',outputfile=dest_file)


# #%%
# t = sub_dirs_full_path[0] + '/0001BC.epub'
# zip = zipfile.ZipFile(t)
# 
# zip.extractall(epub_tmp)
# htmls = []
# for file_tuple in os.walk(epub_tmp):
#     branch = file_tuple[0]
#     files = file_tuple[2]
#     for f in files:
#         if '.html' in f and 'copyright' not in f.lower():
#             htmls.append(branch+'/'+f)
#     print(htmls)
# for h in htmls:
#     dest_file = html_tmp + '/' + h.split('/')[-1].split('.')[0] + '.txt'
#     print(h,dest_file)
#     os.system('pandoc {} -s -o {}'.format(h,dest_file))
# 