package com.anime.Anime.service;

import com.anime.Anime.dto.MediaTransfer;
import com.anime.Anime.models.Media;
import com.anime.Anime.repository.MediaRepository;
import com.anime.Anime.tools.ImageTool;
import com.anime.Anime.types.Medium;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;

import javax.xml.stream.util.XMLEventAllocator;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Optional;

@Service
public class MediaService {
    private MediaRepository mediaRepository;

    public MediaService(MediaRepository mediaRepository){
        this.mediaRepository = mediaRepository;
    }

    public long updateMedia(MediaTransfer mediaTransfer){
        long ret = -1;
        Optional<Media> mediaOpt = mediaRepository.findById(mediaTransfer.getMediaId());
        if(!mediaOpt.isPresent()) return ret;

        Media media = mediaOpt.get();
        media.setTitle(mediaTransfer.getTitle());
        media.setMedium(mediaTransfer.getMedium());
        media.setBookmark(mediaTransfer.getBookmark());
        media.setNotes(mediaTransfer.getNotes());
        media.setRating(mediaTransfer.getRating());

        try{
            media = mediaRepository.saveAndFlush(media);
            ret = media.getMediaId();
            ImageTool.saveImageToFileSystem(media.getMediaId(), media.getImgExtension(), mediaTransfer.getImgBytes());
        }catch(DataAccessException dataAccessException){
            System.out.println(dataAccessException.getMessage());
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }
        return ret;
    }

    public long addMedia(MediaTransfer mediaTransfer){
        long ret = -1;
        String title = mediaTransfer.getTitle();
        int rating = mediaTransfer.getRating();
        int bookmark = mediaTransfer.getBookmark();
        String notes = mediaTransfer.getNotes();
        Medium medium = mediaTransfer.getMedium();
        String imgExtension = mediaTransfer.getImgExtension() == null ? ".jpeg":mediaTransfer.getImgExtension();

        Media media = new Media(title, medium, rating, bookmark, notes, imgExtension);
        try{

            Media savedMedia  = mediaRepository.saveAndFlush(media);
            ret = savedMedia.getMediaId();
            if(mediaTransfer.getImgBytes() != null){
                long mediaId = savedMedia.getMediaId();
                ImageTool.saveImageToFileSystem(mediaId, imgExtension, mediaTransfer.getImgBytes());
            }
        }catch(DataAccessException dataAccessException){
            System.out.println(dataAccessException.getMessage());
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }

        return ret;
    }

}
