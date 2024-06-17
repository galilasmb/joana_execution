package main;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class Main {

    public List<String> weaselWordsList = Arrays.asList(
            "many", "various", "very", "fairly", "several", "extremely",
            "exceedingly", "quite", "remarkably", "few", "surprisingly", "mostly",
            "largely", "huge", "tiny", "is a number", "are a number", "excellent",
            "interestingly", "significantly", "substantially", "clearly", "vast",
            "relatively", "completely");

    public static void main(String[] args) {
        Main cleaner = new Main(); //source
        String text = "Your text with weasel words"; //source
        if (text == null || cleaner.hasWeaselWords(text)) { //source
            cleaner.removeWeaselWords(text);
            cleaner.removeDuplicateWords(text); //sink
        }
    }

    public String cleanText(String text) {
        if (text == null || hasWeaselWords(text)) {
            removeWeaselWords(text);
            removeDuplicateWords(text);
        }
        return text;
    }

    public boolean hasWeaselWords(String text) {
        Set<String> weaselWordsSet = new HashSet<>(weaselWordsList);
        for (String word : text.split("\\s+")) {
            if (weaselWordsSet.contains(word)) {
                return true;
            }
        }
        return false;
    }

    public String removeWeaselWords(String text) {
        for (String weaselWord : weaselWordsList) {
            text = text.replaceAll("\\b" + weaselWord + "\\b", "");
        }
        return text;
    }

    public String removeDuplicateWords(String text) {
        Set<String> uniqueWords = new HashSet<>(Arrays.asList(text.split("\\s+")));
        return uniqueWords.stream().collect(Collectors.joining(" "));
    }
}
