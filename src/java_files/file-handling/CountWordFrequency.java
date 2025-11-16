// Contributor: AkshatBhatt-786
// Uploaded: 2025-11-16

import java.io.*;

public class CountWordFrequency {
    public static void main(String args[]) throws IOException {
        String filename = "files/sample_notes.txt";
        BufferedReader reader = new BufferedReader(new FileReader(filename));
        String line;
        int countWords = 0;
        String target = "Java";

        while((line = reader.readLine()) != null) {
            // Split line into words and count exact matches
            String[] words = line.split("\\s+");
            for(String word : words) {
                if(word.equals(target)) {
                    countWords++;
                }
            }
        }
        reader.close();

        System.out.printf("'%s' appears %d times in %s\n", target, countWords, filename);
    }
}