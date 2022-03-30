package hexo.source._posts.java_demo;

public class test {
    
    public static void main(String[] args) {    
        int[][] graph = {{1,2},{3},{3},{}};
        System.out.println("rows:"+graph.length);
        System.out.println("rows:"+graph[3].length);
    }





    public Node connect(Node root) {
        Node result = new Node(0,root,null,null);
        dfs(root,null);
        return result.left;
    }

    public void dfs(Node curr,Node brother){
        if(curr==null){
            return;
        }

        if(curr.left!=null){
            curr.left.next = curr.right;
            dfs(curr.left,curr.right);
        }

        if(curr.right!=null){
            if(brother!=null){
                if(brother.left!=null){
                    curr.right.next = brother.left;
                }else{
                    curr.right.next = brother.right;
                }
            }
            dfs(curr.right,null);
        }
    }

    
}


class Node {
    public int val;
    public Node left;
    public Node right;
    public Node next;

    public Node() {}
    
    public Node(int _val) {
        val = _val;
    }

    public Node(int _val, Node _left, Node _right, Node _next) {
        val = _val;
        left = _left;
        right = _right;
        next = _next;
    }
}
