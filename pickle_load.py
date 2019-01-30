import pickle

pkl_file = open('chckpt_1', 'wb')
listoflist = [[1, 2], [3, 5, 4], [5, 6]]
pickle.dump(listoflist, pkl_file)

pkl_file2 = open('chckpt_1', 'wb')
listoflist2 = [[1, 2], [3, 5, 423], [5, 6]]
pickle.dump(listoflist2, pkl_file2)
pkl_file.close()

objects = []
with (open("D:\Sem V\DWDM\DWDM Final\Stock-cluster\chckpt_1", "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
print(objects)
