import pandas as pd

films = pd.read_csv('films.csv', delimiter=';')

print("Tabel:\n\n", films.head())

print("\n\nTitles:\n\n", films[['Title']])

print("\n\nInfo of \"Uncharted\"\n\n", films[films.Title == "Uncharted"])

print("\n\nShowing titles and genre of books with year 2022:\n\n", films[films.Year == 2022][['Title', 'Genre']])

print("\n\nExample of count function usage:\n\n", films[films.Year == 2022][['Year']].count())

print("\n\nExample of min, max and sum functions usage:\n\n", films.Rating.max(), films.Rating.min(), films.Rating.sum())

print("\n\nOther examples:\n\n", films[films.Year > films.Year.mean()])

print("\n\nOther examples:\n\n", films.groupby('Rating').Year.mean())

print("\n\nOther examples:\n\n", films.groupby('Rating').Year.min(), films.groupby('Rating').Year.max())

