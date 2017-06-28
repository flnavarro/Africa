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

    def clean_title(self, song):
        if len(song[0].split(':')) > 1:
            if len(song[0].split(':')) == 2:
                song[0] = song[0].split(':')[1]
            elif len(song[0].split(':')) == 3:
                song[0] = song[0].split(':')[2]
        if len(song[0].split('(')) > 1:
            if song[0].split('(')[0] == '':
                song[0] = song[0].split('(')[1].split(')')[1]
            else:
                if '@' in song[0].split('(')[1]:
                    song[0] = song[0].split('(')[0] + \
                              song[0].split('(')[1].split(')')[1]
                else:
                    song[0] = song[0].split('(')[0]
        if len(song[0].split('[')) > 1:
            song[0] = song[0].split('[')[0]
        return song

    def save_titles(self):
        with open('exec_file_clean.csv', 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)

    def clean(self):
        self.load_exec_file()
        for song in self.song_list:
            song = self.clean_title(song)
        self.save_titles()
