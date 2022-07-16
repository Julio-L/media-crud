package com.anime.Anime.Controller;

import com.anime.Anime.dto.MediaReturn;
import com.anime.Anime.dto.MediaTransfer;
import com.anime.Anime.service.MediaService;
import com.anime.Anime.types.DeleteStatus;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/media")
public class MediaController {

    private MediaService mediaService;

    public MediaController(MediaService mediaService){
        this.mediaService = mediaService;
    }

    @PutMapping
    public ResponseEntity updateMedia(@RequestBody MediaTransfer mt){
        mediaService.updateMedia(mt);
        return null;
    }

    @PostMapping
    public ResponseEntity addMedia(@RequestBody MediaTransfer mt){
        mediaService.addMedia(mt);
        return null;
    }

    @DeleteMapping
    public ResponseEntity<DeleteStatus> removeMedia(@RequestParam("mediaId") long mediaId){
        DeleteStatus res = mediaService.removeMedia(mediaId);
        return ResponseEntity.status(res== DeleteStatus.SUCCESS? HttpStatus.ACCEPTED:HttpStatus.EXPECTATION_FAILED).body(res);
    }

    @GetMapping
    public ResponseEntity<MediaReturn> getMedia(@RequestParam("sort") String field, @RequestParam("asc") boolean asc, @RequestParam("page") int page){
        MediaReturn res = mediaService.getMediaSortedBy(field,asc, page);
        return ResponseEntity.ok(res);
    }


}
