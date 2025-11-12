import pandas as pd
import io

string = """
379511733X;Flut.;Wolfgang Hohlbein;2001;Schneekluth;http://images.amazon.com/images/P/379511733X.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/379511733X.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/379511733X.01.LZZZZZZZ.jpg
3548256007;Die Zuckerbäckerin.;Petra Durst-Benning;2003;Ullstein Tb;http://images.amazon.com/images/P/3548256007.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/3548256007.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/3548256007.01.LZZZZZZZ.jpg
3548255329;Fünf Viertel einer Orange.;Joanne Harris;2002;Ullstein Buchverlage GmbH & Co. KG / Ullstein Tas;http://images.amazon.com/images/P/3548255329.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/3548255329.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/3548255329.01.LZZZZZZZ.jpg
354825621X;Chocolat. Das Buch zum Film.;Joanne Harris;2003;Ullstein Tb;http://images.amazon.com/images/P/354825621X.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/354825621X.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/354825621X.01.LZZZZZZZ.jpg
3716022799;Schattenkinder.;Margaret Forster;2001;Arche Verlag;http://images.amazon.com/images/P/3716022799.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/3716022799.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/3716022799.01.LZZZZZZZ.jpg
3548364160;Die wei??e Hexe. Meine Abenteuer in Afrika.;Ilona Maria Hilliges;2003;Ullstein Tb;http://images.amazon.com/images/P/3548364160.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/3548364160.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/3548364160.01.LZZZZZZZ.jpg
3548257615;Die Glasbläserin.;Petra Durst-Benning;2002;List Tb.;http://images.amazon.com/images/P/3548257615.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/3548257615.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/3548257615.01.LZZZZZZZ.jpg
"""

HEADER = [
    "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication",
    "Publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L"
]

df = pd.read_csv(
    io.StringIO(string),
    sep=';',
    encoding='latin-1',
    names=HEADER
)


def fix_german_chars(text):
    if not isinstance(text, str):
        return text
    text = text.replace('?ä', 'ä').replace('?ö', 'ö').replace('?ü', 'ü')
    text = text.replace('?Ä', 'Ä').replace('?Ö', 'Ö').replace('?Ü', 'Ü')

    text = text.replace('??', 'ß').replace('?', 'ß').replace('??', 'ß')
    text = text.replace('??', 'ß').replace('?', 'ß')

    text = text.replace('ä', 'ä').replace('ü', 'ü').replace('ß', 'ß')
    text = text.replace('?', 'ß')

    text = text.replace('??', 'ß')

    return text


# Apply the fix to the relevant columns
df['Book-Title'] = df['Book-Title'].apply(fix_german_chars)
df['Book-Author'] = df['Book-Author'].apply(fix_german_chars)
df['Publisher'] = df['Publisher'].apply(fix_german_chars)


print(df[df['ISBN'].isin(['3548256007', '3548255329', '3548364160'])]
      [['Book-Title', 'Book-Author']])
