package com.anime.Anime.tools;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

public class ImageTool {
    private static final String MEDIA_PATH = "src/main/resources/static/assets/";

    public static byte[] getImageByFilename(String filename){
        return null;
    }

    public static void createImageFromBytes(byte[] imgBytes){

    }

    public static void saveImageToFileSystem(long mediaId, String imgExtension, byte[] imgBytes) throws IOException {
        File outputFile = new File(MEDIA_PATH + mediaId + imgExtension);
        FileOutputStream outputStream = new FileOutputStream(outputFile);
        outputStream.write(imgBytes);
    }


}
