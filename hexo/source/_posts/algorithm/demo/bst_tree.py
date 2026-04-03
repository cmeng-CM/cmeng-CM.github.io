class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

#  构建树
# 插入 BST 节点
def insert(root, val):
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root

# 前序遍历
def preorder(node):
    if node:
        print(node.val, end=' ')
        preorder(node.left)
        preorder(node.right)

# 中序遍历
def inorder(node):
    if node:
        inorder(node.left)
        print(node.val, end=' ')
        inorder(node.right)

# 后序遍历
def postorder(node):
    if node:
        postorder(node.left)
        postorder(node.right)
        print(node.val, end=' ')

# 层序遍历
from collections import deque
def level_order(root):
    if not root:
        return
    q = deque([root])
    while q:
        node = q.popleft()
        print(node.val, end=' ')
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)

# 搜索
def search(root, target):
    if not root:
        return None
    if root.val == target:
        return root
    elif target < root.val:
        return search(root.left, target)
    else:
        return search(root.right, target)
    
# 插入新节点
def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root

# 删除节点
def delete(root, val):
    if not root:
        return None
    if val < root.val:
        root.left = delete(root.left, val)
    elif val > root.val:
        root.right = delete(root.right, val)
    else:
        # 找到节点
        if not root.left:
            return root.right
        elif not root.right:
            return root.left
        # 双子节点
        min_larger_node = root.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left
        root.val = min_larger_node.val
        root.right = delete(root.right, min_larger_node.val)
    return root

if __name__ == "__main__":
    # 构建 BST
    root = None
    for v in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
        root = insert(root, v)
    # print("Preorder traversal:")
    # preorder(root)
    # print("\nInorder traversal:")
    # inorder(root)
    # print("\nPostorder traversal:")
    # postorder(root)
    # print("\nLevel-order traversal:")
    # level_order(root)