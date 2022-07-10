package com.anime.Anime.dto;

import java.util.List;

public class MediaReturn {
    long totalElements;
    int totalPages;
    List<MediaTransfer> media;

    public long getTotalElements() {
        return totalElements;
    }

    public void setTotalElements(long totalElements) {
        this.totalElements = totalElements;
    }

    public int getTotalPages() {
        return totalPages;
    }

    public void setTotalPages(int totalPages) {
        this.totalPages = totalPages;
    }

    public List<MediaTransfer> getMedia() {
        return media;
    }

    public void setMedia(List<MediaTransfer> media) {
        this.media = media;
    }
}
