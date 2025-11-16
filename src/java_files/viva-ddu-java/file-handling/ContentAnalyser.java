import java.io.*;

// Write code to count words in a file

public class ContentAnalyser
{
	public static void main(String args[])
	{
		try {
			String filename = "files/input.txt";
			BufferedReader reader = new BufferedReader(new FileReader(filename));
			String line;
			int totalWords = 0;
			int totalChars = 0;
			int totalLines = 0;

			while((line = reader.readLine()) != null)
			{
				String[] words = line.split("[\\s.,!?]+");

				for(String token : words)
				{
					if(!token.isEmpty())
					{
						totalWords ++;
					}
					for(int i=0; i<token.length(); i++)
					{
						totalChars++;
					}
				}
				totalLines++;
			}

			reader.close();
			System.out.printf("Total Words: %d\n", totalWords);
			System.out.printf("Total Characters: %d\n", totalChars);
			System.out.printf("Total Lines: %d\n", totalLines);


		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}