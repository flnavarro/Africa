import unicodecsv as csv
import settings


class TitleCleaner:

    def __init__(self):
        self.track_list = []
        self.load_new_posts()

    def load_new_posts(self):
        # Load new posts data
        with open(settings.NEW_POSTS, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.track_list.append(row)

    @staticmethod
    def clean_title(title):
        title_split = title.split(' ')
        track_artist = []
        track_title = []
        get_artist = True
        open_brackets = False
        if 'Wimbo mpya' in title:
            # If 'wimbo mpya' post - Title and artist is upper case
            prev_upper = False
            for word in title_split:
                if word.isupper():
                    if get_artist:
                        track_artist.append(word)
                        prev_upper = True
                    else:
                        track_title.append(word)
                else:
                    if prev_upper:
                        get_artist = False
        else:
            # Other posts - discard info words to get only artist and title
            for word in title_split:
                if get_artist:
                    if len(word) > 1:
                        if word != u'LISTEN' and word != u'DOWNLOAD' and word != u'#NewAUDIO:' \
                                and word != u'#NewVIDEO:' and word != u'AUDIO:' and word != u'DOWNLOAD:' \
                                and word != u'(Audio)' and word != u'(Listen/Download)' and word != u'NEW' \
                                and word != u'MUSIC:' and word != u'(New' and word != u'Audio)' \
                                and word != u'(Audio+Video)' and word != u'(Video+Audio)' \
                                and word != u'(OldSchool' and word != u'Lyrics)' and word != u'(Official' \
                                and word != u'Audio' and word != u'Youtube' and word != u'#DJChokaMusic:' \
                                and word != u'UNOFFICIAL' and word != u'RELEASE' and word != u'LYRICS' \
                                and word != u'VIDEO:' and word != u'#AUDIO:' and word != u'AUDIO' \
                                and word != u'LYRICS:' and word != u'Download' and word != u'WIMBO' \
                                and word != u'MPYA:' and word != u'VIDEO+AUDIO:' and word != u'Listen/Download:' \
                                and word != u'Listen' and word != u'Listen/Download' \
                                and word != u'Sikiliza/Pakua:' and word != u'Sikiliza/Pakuwa:' \
                                and word != u'Sikiliza/Pakua' and word != u'Music)' \
                                and word != u'(AUDIO)' and word != u'AUDIOS:' and word != u'VIDEO' \
                                and word != u'(Youtube' and word != u'AUDIO+LYRICS:' \
                                and word != u'|#NewAUDIO:' \
                                and '@' not in word:
                            if word != u'Feat' and word != u'feat' and word != u'Feat.' and word != u'feat.' \
                                    and word != u'Ft' and word != u'ft' and word != u'Ft.' and word != u'ft.' \
                                    and word != u'FT' and word != u'FT.' and word != u'FEAT' and word != u'FEAT.':
                                track_artist.append(word)
                            else:
                                track_artist.append('FEAT.')
                    else:
                        if word != u'&' and word != u'|' and word != u'+' and word.isalpha() is False:
                            get_artist = False
                        if word.isalpha():
                            track_artist.append(word)
                else:
                    if '(' in word:
                        open_brackets = True
                    elif ')' in word:
                        open_brackets = False
                    else:
                        if open_brackets is False:
                            track_title.append(word)

        track_artist = ' '.join(track_artist)
        track_title = ' '.join(track_title)
        return track_artist, track_title

    def save_titles(self):
        # Save a download list with clean titles to use later
        with open(settings.DL_LIST, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.track_list)

    def clean(self):
        print('Obtaining track artists and titles...')
        post_titles = [i[0] for i in self.track_list]
        post_dates = [i[1] for i in self.track_list]
        post_links = [i[2] for i in self.track_list]
        track_artists = []
        track_titles = []
        # Clean post titles and get track artist and title
        for post_title in post_titles:
            track_artist, track_title = self.clean_title(post_title)
            track_artists.append(track_artist)
            track_titles.append(track_title)
        self.track_list = zip(track_artists, track_titles, post_links, post_titles, post_dates)
        self.save_titles()
