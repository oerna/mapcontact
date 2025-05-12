const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const NodeGeocoder = require('node-geocoder');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static('.'));

// Initialize geocoder
const geocoder = NodeGeocoder({
    provider: 'openstreetmap'
});

// Initialize database
const db = new sqlite3.Database('contacts.db', (err) => {
    if (err) {
        console.error('Error opening database:', err);
    } else {
        console.log('Connected to SQLite database');
        // Create contacts table if it doesn't exist
        db.run(`CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            telephone TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL
        )`);
    }
});

// API Endpoints
app.post('/api/contacts', async (req, res) => {
    const { name, company, email, telephone, address } = req.body;
    try {
        // Geocode the address
        const geoResults = await geocoder.geocode(address);
        if (geoResults.length === 0) {
            return res.status(400).json({ error: 'Could not geocode address' });
        }

        const { latitude, longitude } = geoResults[0];
        
        db.run(
            'INSERT INTO contacts (name, company, email, telephone, address, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)',
            [name, company, email, telephone, address, latitude, longitude],
            function(err) {
                if (err) {
                    res.status(500).json({ error: err.message });
                    return;
                }
                res.json({
                    id: this.lastID,
                    name,
                    company,
                    email,
                    telephone,
                    address,
                    latitude,
                    longitude
                });
            }
        );
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/contacts', (req, res) => {
    db.all('SELECT * FROM contacts', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 