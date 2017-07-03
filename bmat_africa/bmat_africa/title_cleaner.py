import unicodecsv as csv
import settings


class TitleCleaner:

    def __init__(self):
        self.exec_file = settings.EXEC_FILE
        self.song_list = []

    def load_exec_file(self):
        with open(self.exec_file, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.song_list.append(row)

    @staticmethod
    def clean_title(song):
        if len(song[0].split(':')) > 1:
            # Case -> '#NewAUDIO:'
            if len(song[0].split(':')) == 2:
                song[0] = song[0].split(':')[1]
            # Case -> 'DOWNLOAD: #NewAUDIO:'
            elif len(song[0].split(':')) == 3:
                song[0] = song[0].split(':')[2]
        if len(song[0].split('|')) > 1:
            # Case -> 'Listen/Download |'
            song[0] = song[0].split('|')[1]
        if len(song[0].split('(')) > 1:
            # Case -> '(New Audio)'
            if song[0].split('(')[0] == '' or song[0].split('(')[0] == ' ':
                song[0] = song[0].split('(')[1].split(')')[1]
            else:
                # Case -> ' (@JChameleone) '
                # TODO: SOMETIMES THERE ARE TWO @ !!
                if '@' in song[0].split('(')[1]:
                    song[0] = song[0].split('(')[0] + \
                              ' '.join(song[0].split('(')[1].split(')')[1:])
                    if len(song[0].split('(')) > 1:
                        if '@' in song[0].split('(')[1]:
                            song[0] = song[0].split('(')[0] + \
                                    ' '.join(song[0].split('(')[1].split(')')[1:])
        if len(song[0].split(')')) > 1:
            # Case -> '(Official Audio)'
            if song[0].split(')')[-1] == '':
                song[0] = song[0].split('(')[0]

        if len(song[0].split('[')) > 1:
            # Case -> '[Official Audio]'
            song[0] = song[0].split('[')[0]

        if 'Wimbo mpya' in song[0]:
            new_title = ''
            for word in song[0].split(' '):
                if word.isupper():
                    new_title += word + ' '
            song[0] = new_title

        return song

    @staticmethod
    def clean_title_2(title):
        title_split = title.split(' ')
        song_artist = []
        song_title = []
        get_artist = True
        open_brackets = False
        if 'Wimbo mpya' in title:
            prev_upper = False
            for word in title_split:
                if word.isupper():
                    if get_artist:
                        song_artist.append(word)
                        prev_upper = True
                    else:
                        song_title.append(word)
                else:
                    if prev_upper:
                        get_artist = False
        else:
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
                                song_artist.append(word)
                            else:
                                song_artist.append('FEAT.')
                    else:
                        if word != u'&' and word != u'|' and word != u'+' and word.isalpha() is False:
                            get_artist = False
                        if word.isalpha():
                            song_artist.append(word)
                else:
                    if '(' in word:
                        open_brackets = True
                    elif ')' in word:
                        open_brackets = False
                    else:
                        if open_brackets is False:
                            song_title.append(word)

        song_artist = ' '.join(song_artist)
        song_title = ' '.join(song_title)
        return song_artist, song_title

    def save_titles(self):
        with open('exec_file.csv', 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)

    def clean(self):
        self.load_exec_file()
        song_titles = [i[0] for i in self.song_list]
        song_dates = [i[1] for i in self.song_list]
        song_posts = [i[2] for i in self.song_list]
        track_artists = []
        track_titles = []
        for song in song_titles:
            # song = self.clean_title(song)
            song_artist, song_title = self.clean_title_2(song)
            track_artists.append(song_artist)
            track_titles.append(song_title)
        self.song_list = zip(track_artists, track_titles, song_dates, song_posts)
        self.save_titles()
