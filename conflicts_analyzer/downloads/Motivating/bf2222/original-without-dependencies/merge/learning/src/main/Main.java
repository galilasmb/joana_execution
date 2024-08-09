package main;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class Main {
    public int source, sink, base;
    public static void main(String[] args) {
        Main inst = new Main();
        inst.source = 0; //SOURCE
        inst.source = inst.source(1); //SOURCE
        inst.base = 0;
        inst.sink = inst.sink(1)+inst.source; //SINK
        System.out.println(inst.sink); //SINK
        System.out.println(inst.source+inst.sink); //SOURCE
        System.out.println(inst.sink+inst.source); //SINK
    }

    public int cleaner(){   
        return 0;
    }

    public int source(int value){
        System.out.println(value);
        return value+1;
    }

    public int sink(int value){
        System.out.println(value);
        return value+1;
    }


}
