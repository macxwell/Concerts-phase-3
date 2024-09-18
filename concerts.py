import sqlite3

# Connect to the database (or create it)
conn = sqlite3.connect('concerts.db')
cursor = conn.cursor()

# Step 1: Create tables
def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hometown TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        city TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS concerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        band_id INTEGER,
        venue_id INTEGER,
        date TEXT NOT NULL,
        FOREIGN KEY (band_id) REFERENCES bands (id),
        FOREIGN KEY (venue_id) REFERENCES venues (id)
    )
    ''')
    conn.commit()

# Step 2: Call create_tables()
create_tables()

# Step 3: CRUD Operations
def add_band(name, hometown):
    cursor.execute('INSERT INTO bands (name, hometown) VALUES (?, ?)', (name, hometown))
    conn.commit()

def add_venue(title, city):
    cursor.execute('INSERT INTO venues (title, city) VALUES (?, ?)', (title, city))
    conn.commit()

def add_concert(band_id, venue_id, date):
    cursor.execute('INSERT INTO concerts (band_id, venue_id, date) VALUES (?, ?, ?)', (band_id, venue_id, date))
    conn.commit()

# Class Definitions
class Band:
    def __init__(self, band_id):
        self.band_id = band_id

    def concerts(self):
        cursor.execute('''
        SELECT c.id, v.title, v.city, c.date
        FROM concerts c
        JOIN venues v ON c.venue_id = v.id
        WHERE c.band_id = ?
        ''', (self.band_id,))
        return cursor.fetchall()

    def venues(self):
        cursor.execute('''
        SELECT v.id, v.title, v.city
        FROM concerts c
        JOIN venues v ON c.venue_id = v.id
        WHERE c.band_id = ?
        ''', (self.band_id,))
        return cursor.fetchall()

    def play_in_venue(self, venue_title, date):
        cursor.execute('''
        SELECT id FROM venues WHERE title = ?
        ''', (venue_title,))
        venue = cursor.fetchone()
        if venue:
            add_concert(self.band_id, venue[0], date)

    def all_introductions(self):
        cursor.execute('''
        SELECT v.city, b.name, b.hometown
        FROM concerts c
        JOIN venues v ON c.venue_id = v.id
        JOIN bands b ON c.band_id = b.id
        WHERE c.band_id = ?
        ''', (self.band_id,))
        introductions = cursor.fetchall()
        return [f"Hello {city}!!!!! We are {name} and we're from {hometown}" for city, name, hometown in introductions]

    @staticmethod
    def most_performances():
        cursor.execute('''
        SELECT b.id, b.name, COUNT(c.id) as performance_count
        FROM bands b
        JOIN concerts c ON b.id = c.band_id
        GROUP BY b.id
        ORDER BY performance_count DESC
        LIMIT 1
        ''')
        return cursor.fetchone()

class Venue:
    def __init__(self, venue_id):
        self.venue_id = venue_id

    def concerts(self):
        cursor.execute('''
        SELECT c.id, b.name, c.date
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        WHERE c.venue_id = ?
        ''', (self.venue_id,))
        return cursor.fetchall()

    def bands(self):
        cursor.execute('''
        SELECT DISTINCT b.id, b.name
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        WHERE c.venue_id = ?
        ''', (self.venue_id,))
        return cursor.fetchall()

    def concert_on(self, date):
        cursor.execute('''
        SELECT c.id, b.name
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        WHERE c.venue_id = ? AND c.date = ?
        LIMIT 1
        ''', (self.venue_id, date))
        return cursor.fetchone()

    def most_frequent_band(self):
        cursor.execute('''
        SELECT b.id, b.name, COUNT(c.id) as performance_count
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        WHERE c.venue_id = ?
        GROUP BY b.id
        ORDER BY performance_count DESC
        LIMIT 1
        ''', (self.venue_id,))
        return cursor.fetchone()

class Concert:
    def __init__(self, concert_id):
        self.concert_id = concert_id

    def hometown_show(self):
        cursor.execute('''
        SELECT b.hometown, v.city
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        JOIN venues v ON c.venue_id = v.id
        WHERE c.id = ?
        ''', (self.concert_id,))
        hometown, city = cursor.fetchone()
        return hometown.lower() == city.lower()

    def introduction(self):
        cursor.execute('''
        SELECT b.name, b.hometown, v.city
        FROM concerts c
        JOIN bands b ON c.band_id = b.id
        JOIN venues v ON c.venue_id = v.id
        WHERE c.id = ?
        ''', (self.concert_id,))
        name, hometown, city = cursor.fetchone()
        return f"Hello {city}!!!!! We are {name} and we're from {hometown}"

# Example Usage
if __name__ == "__main__":
    # Adding sample data
    add_band('The Beatles', 'Liverpool')
    add_band('Led Zeppelin', 'London')
    add_venue('Madison Square Garden', 'New York')
    add_venue('The O2', 'London')

    # Adding concerts
    add_concert(1, 1, '2023-10-01')
    add_concert(2, 2, '2023-11-15')

    # Example concert
    concert = Concert(1)
    print("Hometown Show:", concert.hometown_show())
    print("Concert Introduction:", concert.introduction())

    # Retrieve bands for a venue
    venue = Venue(1)
    print("Concerts at Venue:", venue.concerts())
    print("Bands at Venue:", venue.bands())

    # Retrieve concerts for a band
    band = Band(1)
    print("Concerts by Band:", band.concerts())
    print("Venues for Band:", band.venues())
    print("Band Introductions:", band.all_introductions())

    # Most performances
    most_band = Band.most_performances()
    print("Most Performances Band:", most_band)

    # Most frequent band at a venue
    frequent_band = venue.most_frequent_band()
    print("Most Frequent Band at Venue:", frequent_band)

# Close the connection
conn.close()
