package main;

import java.io.IOException;

import com.ibm.wala.ipa.cha.ClassHierarchyException;
import com.ibm.wala.util.CancelException;
import com.ibm.wala.util.graph.GraphIntegrity.UnsoundGraphException;

public class TestJoanaInvocation {
	public static void main(String[] args) throws ClassHierarchyException, ClassNotFoundException, IOException, UnsoundGraphException, CancelException {
		JoanaInvocation.main(new String[]{
				//"/media/galileu/Arquivos/Doutorado/Pesquisa/JOANA/rsmbf/conflicts_analyzer/TestFlows/","1"
				//"//media/galileu/Arquivos/Doutorado/Pesquisa/JOANA/rsmbf/", "1"
				//"/media/galileu/Arquivos/Doutorado/Pesquisa/JOANA/rsmbf","0"
		});
	}
}
