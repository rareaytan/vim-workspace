import os

if (os.path.exists("cscope.files")):
    os.remove("cscope.files")
    print("remove cscope.files")
if (os.path.exists("cscope.in.out")):
    os.remove("cscope.in.out")
    print("remove cscope.in.out")
if (os.path.exists("cscope.out")):
    os.remove("cscope.out")
    print("remove cscope.out")
if (os.path.exists("cscope.po.out")):
    os.remove("cscope.po.out")
    print("remove cscope.po.out")

save_file = open("cscope.files", 'w')

for root, dirs, list in os.walk("./"):
    for i in list:
        cur_path = os.path.abspath(root)
        file_path = cur_path + "/" + i
        save_file.write(file_path+"\n")
        
save_file.close()
