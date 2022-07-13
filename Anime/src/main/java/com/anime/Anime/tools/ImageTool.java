package com.anime.Anime.tools;

import org.apache.tomcat.util.codec.binary.Base64;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class ImageTool {
    private static final String MEDIA_PATH = "src/main/resources/static/assets/";

    public static String getImageByFilename(String filename, String format){
        File file = new File(MEDIA_PATH + filename);
        try {
            BufferedImage bImage = ImageIO.read(file);
            ByteArrayOutputStream bao = new ByteArrayOutputStream();
            ImageIO.write(bImage, format, bao);
            String img = Base64.encodeBase64String(bao.toByteArray());

            return img;
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }
        return null;
    }

    public static void createImageFromBytes(byte[] imgBytes){

    }

    public static void deleteImageFromFileSystem(String filename){
        File file = new File(MEDIA_PATH + filename);
        file.delete();
    }

    public static void saveImageToFileSystem(long mediaId, String imgExtension, String imgBytes) throws IOException {
        File outputFile = new File(MEDIA_PATH + mediaId + imgExtension);
        FileOutputStream outputStream = new FileOutputStream(outputFile);
        outputStream.write(imgBytes.getBytes());
    }


}
