{
    if(file_exist("GENSOU.SCR")) {
        file_ropen("GENSOU.SCR");
        file_seek((rank * sizeof(hi)), SEEK_SET);
        file_read(&hi, sizeof(hi));
        file_seek((4 * sizeof(hi)), SEEK_CUR);
        file_read(&hi2, sizeof(hi2));
        file_close();
        if(scoredat_decode() != 0) {
            scoredat_recreate();
            return true;
        }
    } else {
        scoredat_recreate();
        return true;
    }
    return false;
}
