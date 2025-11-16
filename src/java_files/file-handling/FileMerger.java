// Contributor: AkshatBhatt-786
// Uploaded: 2025-11-16

import java.io.*;
import java.util.*;

// write a code to merge two files

public class FileMerger
{
	StringBuilder content;
	String file1, file2, file3;

	FileMerger(String file1, String file2)
	{
		this.file1 = file1;
		this.file2 = file2;
		content = new StringBuilder();
	}

	public static void main(String args[])
	{
		FileMerger manager = new FileMerger("file1.txt", "file2.txt");
		manager.mergeTwoFiles();
		System.out.println("Successfully merged the two files.");

	}

	public void mergeTwoFiles()
	{
		try {
			copyContent(file1);
			copyContent(file2);
			file3 = "output.txt";
			BufferedWriter writer = new BufferedWriter(new FileWriter(file3));
			writer.write(content.toString());
			writer.close();
			File f = new File(file3);
			System.out.println("merged file output at: " + f.getAbsolutePath());
		} catch(IOException e)
		{
			e.printStackTrace();
		}
	}

	public void copyContent(String file)
	{

		try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
		String line;

			while((line = reader.readLine()) != null)
			{
				content.append(line).append("\n");
			}
			System.out.println("Successfully copy the content of : " + file);
		} catch(IOException e)
		{
			e.printStackTrace();
		}
	}
}
