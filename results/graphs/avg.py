#!/usr/bin/env python3
import re

# TODO file name
def average_graph(element_count, content, is_float=None):
    result = 0
    for i in range(0, len(content)):
        if i%element_count == (element_count - 1):
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


def set_avg(file_name, agregate):
    print("Average ", file_name)
    with open(file_name, "r") as file_r:
        read_content = file_r.readlines()
    read_content = [x.strip() for x in read_content]

    average_graph(agregate, read_content)


def peer_node_ratio():
    print("Ratio")
    with open("./resultNF.txt", "r") as file_r:
        read_content = file_r.readlines()
    nodes = [x.strip() for x in read_content]

    with open("./resultPF.txt", "r") as file_r:
        read_content = file_r.readlines()
    peers = [x.strip() for x in read_content]

    results = []
    for i in range(0, len(peers)):
        key = re.search(r".*,", read_content[i]).group(0)
        node_value = re.search(r",.*", nodes[i]).group(0)[2:-2]
        peer_value = re.search(r",.*", peers[i]).group(0)[2:-2]
        try:
            ratio = int(peer_value)/int(node_value)
        except ValueError:
            continue
        key = key + str(ratio) + " )"
        results.append(key)

    average_graph(15, results, True)

def correct_ratio():
    print("Correct")
    with open("./ratio.txt", "r") as file_r:
        read_content = file_r.readlines()
    ratio = [x.strip() for x in read_content]

    average_graph(5, ratio, True)

if __name__ == '__main__':
    set_avg("./resultPF.txt", 20)
    peer_node_ratio()
    correct_ratio()
    set_avg("./resultH.txt", 20)
