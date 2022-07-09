package com.anime.Anime.models;

import com.anime.Anime.types.Medium;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import javax.persistence.*;
import java.util.Date;

@Entity
@EntityListeners(AuditingEntityListener.class)
public class Media {

    @GeneratedValue(strategy = GenerationType.AUTO)
    @Id
    long mediaId;

    @Enumerated(value= EnumType.STRING)
    private Medium medium;

    private String title;

    private int bookmark;

    private int rating;

    private String notes;

    private String imgExtension;

    @LastModifiedDate
    private Date lastModified;

    public Media(){}

    public Media(String title, Medium medium, int rating, int bookmark, String notes, String imgExtension){
        this.title = title;
        this.medium = medium;
        this.rating = rating;
        this.bookmark = bookmark;
        this.notes = notes;
        this.imgExtension = imgExtension;
    }

    public long getMediaId() {
        return mediaId;
    }

    public void setMediaId(long mediaId) {
        this.mediaId = mediaId;
    }

    public Medium getMedium() {
        return medium;
    }

    public void setMedium(Medium medium) {
        this.medium = medium;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public int getBookmark() {
        return bookmark;
    }

    public void setBookmark(int bookmark) {
        this.bookmark = bookmark;
    }

    public int getRating() {
        return rating;
    }

    public void setRating(int rating) {
        this.rating = rating;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public Date getLastModified() {
        return lastModified;
    }

    public void setLastModified(Date lastModified) {
        this.lastModified = lastModified;
    }

    public String getImgExtension() {
        return imgExtension;
    }

    public void setImgExtension(String imgExtension) {
        this.imgExtension = imgExtension;
    }
}
