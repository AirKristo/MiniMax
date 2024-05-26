import sys

#Define node and attributes and functions
class Node(object):
    def __init__(self, value):
        self.value = value #Varible name such as 'a' or 'b29'
        self.children = [] #List of all the nodes kids
        self.parents = [] #List of all the nodes parents
        self.score = None #This is the given score in the assignment for variables that have one

    def add_child(self, obj):
        self.children.append(obj)

    def add_parent(self, obj):
        self.parents.append(obj)

    def get_children(self):
        return self.children


# To find nodes and easily connect them


def find_node(node_list, target):
    for n in node_list:
        if n.value == target:
            return n
        t = find_node(n.children, target)
        if t:
            return t
    return None


verbose = False
alpha_beta = False
range_value = None
filename = None

root_player = ''

for item in sys.argv:
    if ".txt" in item:
        filename = item
    elif "-range" in item:
        try:
            range_index = sys.argv.index(item)
            range_value = int(sys.argv[range_index + 1])
        except(ValueError, IndexError):
            sys.exit(1)
    elif "-v" == item:
        verbose = True
    elif "-ab" == item:
        alpha_beta = True
    elif ("min" == item) or ("max" == item):
        root_player = item

# Check if min or max was provided

if not root_player:
    raise Exception("Provide either 'max' or 'min' argument when running minimax (no caps)")

if not filename:
    raise Exception("Provide an argument for an existing txt file")


# open file line by line and all the nodes to a list
# Then go through file again and link children with parents and set the values of the leaves

file = open(filename, 'r')
node_list = []

for line in file:
    line = line.strip('\n')
    if not line:
        continue
    token = line.strip().split(':')
    if len(token) == 2:
        node_name = token[0]
        parent_node = find_node(node_list, node_name)
        if not parent_node:
            node_list.append(Node(node_name))
        node_child = token[1]
        node_child = node_child.strip().split(",")
        for child in node_child:
            child = child.strip("[] ")
            child_node = find_node(node_list, child)
            if not child_node:
                node_list.append(Node(child))


file.seek(0)

for line in file:
    line = line.strip('\n')
    if not line:
        continue
    tokens = line.strip().split(':')
    if len(tokens) == 2:
        parent_node_name = tokens[0]
        parent_node = find_node(node_list, parent_node_name)
        node_child = tokens[1]
        node_child = node_child.strip().split(",")
        children_list = []
        for child in node_child:
            child = child.strip("[] ")
            child_node = find_node(node_list, child)
            if child_node:
                parent_node.add_child(child_node)
                child_node.add_parent(parent_node)
    if len(tokens) == 1:
        leaf_value = tokens[0].split('=')
        leaf_name = leaf_value[0]
        leaf_score = leaf_value[1]
        if range_value is not None:
            if abs(int(leaf_score)) > abs(range_value):
                raise Exception("Value of " + str(leaf_name) + " outside of range")
        leaf_node = find_node(node_list, leaf_name.strip())
        leaf_node.score = int(leaf_score.strip())

# Check for multiple roots and for undefined leaves

nodes_without_parent = 0
list_of_nodes_without_parent = []

for n in node_list:
    if (not n.children) and (n.score is None):
        raise Exception('leaf node "' + n.value + '" of "' + n.parents[0].value + '" not found')
    if not n.parents:
        nodes_without_parent += 1
        list_of_nodes_without_parent.append(n)

if nodes_without_parent > 1:
    error_text = 'multiple roots: "' + str(list_of_nodes_without_parent[0].value) + '"'
    for n in list_of_nodes_without_parent[1:]:
        error_text += ' and "' + str(n.value) + '"'
    raise Exception(error_text)


def minimax(node, depth, player_type, alpha, beta):
    if not node.children:
        return node, node.score
    no_pruned = True
    max_value, min_value = None, None

    if player_type == "max":
        for child in node.children:
            node_choice,  value_choice = minimax(child, depth + 1, "min", alpha, beta)
            if max_value is None:
                max_value = value_choice
                child_picked = child
            else:
                if value_choice > max_value:
                    child_picked = child
                max_value = max(max_value, value_choice)
            if alpha_beta:
                if alpha is None:
                    alpha = value_choice
                alpha = max(alpha, value_choice)
                if range_value is not None and value_choice >= (abs(range_value)):
                    break #The cut off for max value found
                if beta is not None:
                    if value_choice >= beta:
                        no_pruned = False
                        break #This is the pruning
        if verbose and no_pruned:
            print(player_type + "(" + str(node.value) + ")" + " chooses " + str(child_picked.value) + " for " + str(max_value))
        return child_picked, max_value
    elif player_type == "min":
        for child in node.children:
            node_choice, value_choice = minimax(child, depth + 1, "max", alpha, beta)
            if min_value is None:
                min_value = value_choice
                child_picked = child
            else:
                if value_choice < min_value:
                    child_picked = child
                min_value = min(min_value, value_choice)
            if alpha_beta:
                if beta is None:
                    beta = value_choice
                beta = min(beta, value_choice)
                if range_value is not None and value_choice <= (abs(range_value) * -1):
                    break # min value cut off
                if alpha is not None:
                    if value_choice <= alpha:
                        no_pruned = False
                        break #This is the pruning
        if verbose and no_pruned: # Don't print if pruned
            print(player_type + "(" + str(node.value) + ")" + " chooses " + str(child_picked.value) + " for " + str(min_value))
        return child_picked, min_value


root = node_list[0]


def print_result(root, root_player):
    node, score = minimax(root, 0, root_player, None, None)
    if not verbose:
        print(root_player + "(" + str(root.value) + ") chooses " + str(node.value) + " for " + str(score))


print_result(root, root_player)






