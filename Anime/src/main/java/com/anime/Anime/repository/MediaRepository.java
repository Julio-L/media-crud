package com.anime.Anime.repository;

import com.anime.Anime.models.Media;
import com.anime.Anime.types.Medium;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MediaRepository extends JpaRepository<Media, Long> {

    @Query("select m from Media m")
    public Page<Media> getMediaSortedBy(Pageable pageable);

}
