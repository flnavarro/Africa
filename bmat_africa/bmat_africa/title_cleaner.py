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
                              song[0].split('(')[1].split(')')[1]
        if len(song[0].split(')')) > 1:
            # Case -> '(Official Audio)'
            if song[0].split(')')[-1] == '':
                song[0] = song[0].split('(')[0]

        if len(song[0].split('[')) > 1:
            # Case -> '[Official Audio]'
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
