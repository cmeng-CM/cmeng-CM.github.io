# 节点定义
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1

# 获取节点高度
def get_height(node):
    return node.height if node else 0

# 更新高度
def update_height(node):
    node.height = 1 + max(get_height(node.left), get_height(node.right))

# 获取平衡因子
def get_balance(node):
    return get_height(node.left) - get_height(node.right)

# 左旋
def left_rotate(z):
    y = z.right
    T2 = y.left
    y.left = z
    z.right = T2
    update_height(z)
    update_height(y)
    return y

# 右旋
def right_rotate(z):
    y = z.left
    T3 = y.right
    y.right = z
    z.left = T3
    update_height(z)
    update_height(y)
    return y

# 插入新节点
def insert(node, key):
    if not node:
        return TreeNode(key)
    
    if key < node.val:
        node.left = insert(node.left, key)
    else:
        node.right = insert(node.right, key)
    
    update_height(node)
    
    balance = get_balance(node)
    
    # LL
    if balance > 1 and key < node.left.val:
        return right_rotate(node)
    # RR
    if balance < -1 and key > node.right.val:
        return left_rotate(node)
    # LR
    if balance > 1 and key > node.left.val:
        node.left = left_rotate(node.left)
        return right_rotate(node)
    # RL
    if balance < -1 and key < node.right.val:
        node.right = right_rotate(node.right)
        return left_rotate(node)
    
    return node