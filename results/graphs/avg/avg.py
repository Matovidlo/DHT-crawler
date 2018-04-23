#!/usr/bin/env python3
import re

# TODO file name
def average_graph(element_count, content, is_float=None, file_name=None):
    result = 0
    if file_name:
        f_open = open(file_name, 'w')
    for i in range(0, len(content)):
        if i%element_count == (element_count - 1):
            if file_name:
                print(re.search(r".*,", content[i]).group(0),
                      result/element_count, ")", file=f_open)
            else:
                print(re.search(r".*,", content[i]).group(0),
                      result/element_count, ")")

            result = 0
        value = re.search(r",.*", content[i]).group(0)[2:-2]
        if is_float:
            try:
                result = result + float(value)
            except ValueError:
                continue
        else:
            try:
                result = result + int(value)
            except ValueError:
                continue


def set_avg(file_name, agregate, output=None):
    print("Average ", file_name)
    with open(file_name, "r") as file_r:
        read_content = file_r.readlines()
    read_content = [x.strip() for x in read_content]

    average_graph(agregate, read_content, file_name=output)


def peer_node_ratio(file1, file2):
    print("Ratio")
    with open(file1, "r") as file_r:
        read_content = file_r.readlines()
    nodes = [x.strip() for x in read_content]

    with open(file2, "r") as file_r:
        read_content = file_r.readlines()
    peers = [x.strip() for x in read_content]

    results = []
    for i in range(0, len(peers)):
        key = re.search(r".*,", read_content[i]).group(0)
        node_value = re.search(r",.*", nodes[i]).group(0)[2:-2]
        peer_value = re.search(r",.*", peers[i]).group(0)[2:-2]
        try:
            ratio = (float(peer_value)/float(node_value)) * 100
        except ValueError:
            continue
        key = key + str(ratio) + " )"
        results.append(key)
    for key in results:
        print(key)
    # average_graph(1, results, True)

def compare_to_real(file_name, cnt):
    print("Compare real")
    with open(file_name, "r") as file_r:
        read_content = file_r.readlines()
    read_content = [x.strip() for x in read_content]

    for i in range(0, len(read_content)):
        key = re.search(r".*,", read_content[i]).group(0)
        peer_value = re.search(r",.*", read_content[i]).group(0)[2:-2]
        try:
            ratio = (float(peer_value)/float(cnt)) * 100
        except ValueError:
            continue
        print(key, ratio, ")")

def correct_ratio(file_name):
    print("Correct")
    with open(file_name, "r") as file_r:
        read_content = file_r.readlines()
    ratio = [x.strip() for x in read_content]

    average_graph(5, ratio, True)

if __name__ == '__main__':
    #set_avg("../resultPF.txt", 20)
    #peer_node_ratio()
    correct_ratio("../ratio.txt")
    set_avg("../resultH.txt", 20)
    set_avg("../lifoH.txt", 10, "../lifo_avgP.txt")
    set_avg("../lifoNF.txt", 10, "../lifo_avgN.txt")
    peer_node_ratio("../lifo_avgN.txt", "../lifo_avgP.txt")
    set_avg("../fifoH.txt", 10, "../fifo_avgP.txt")
    set_avg("../fifoNF.txt", 10, "../fifo_avgN.txt")
    peer_node_ratio("../fifo_avgN.txt", "../fifo_avgP.txt")

    # compare peers to real peers
    compare_to_real("../lifoH.txt", 2500)
