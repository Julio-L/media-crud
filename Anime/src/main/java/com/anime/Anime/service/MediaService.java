package com.anime.Anime.service;

import com.anime.Anime.dto.MediaReturn;
import com.anime.Anime.dto.MediaTransfer;
import com.anime.Anime.models.Media;
import com.anime.Anime.repository.MediaRepository;
import com.anime.Anime.tools.ImageTool;
import com.anime.Anime.types.DeleteStatus;
import com.anime.Anime.types.Medium;
import org.modelmapper.ModelMapper;
import org.springframework.dao.DataAccessException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;


import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class MediaService {
    private MediaRepository mediaRepository;
    private ModelMapper modelMapper;

    public MediaService(MediaRepository mediaRepository, ModelMapper modelMapper){
        this.mediaRepository = mediaRepository;
        this.modelMapper = modelMapper;
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

    public DeleteStatus removeMedia(long mediaId){
        try{
            Optional<Media> mediaOpt = mediaRepository.findById(mediaId);
            if(mediaOpt.isEmpty()) return DeleteStatus.INVALID_ID;
            Media media = mediaOpt.get();
            mediaRepository.delete(media);
            ImageTool.deleteImageFromFileSystem(mediaId + media.getImgExtension());
        }catch(DataAccessException dataAccessException){
            System.out.println(dataAccessException.getMessage());
            return DeleteStatus.FAILED;
        }

        return DeleteStatus.SUCCESS;
    }

    public MediaReturn getMediaSortedBy(String field, boolean asc, int page){
        Page<Media> res = mediaRepository.getMediaSortedBy(PageRequest.of(page, 1, Sort.by(field)));
        MediaReturn mr = new MediaReturn();
        mr.setTotalElements(res.getTotalElements());
        mr.setTotalPages(res.getTotalPages());
        List<Media> content = res.getContent();

        List<MediaTransfer> mt = content.stream().map(m-> modelMapper.map(m, MediaTransfer.class)).collect(Collectors.toList());
        mr.setMedia(mt);

        for(MediaTransfer m: mt){
            byte[] imgBytes = ImageTool.getImageByFilename(m.getMediaId() + m.getImgExtension(), m.getImgExtension().substring(1));
            m.setImgBytes(imgBytes);
        }

        return mr;
    }


}
