const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Настройка EJS как шаблонизатора
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Обслуживание статических файлов
app.use(express.static(path.join(__dirname, 'public')));

// Маршруты для EJS страниц
app.get('/', (req, res) => {
  res.render('pages/index');
});

app.get('/leaderboard', (req, res) => {
  res.render('pages/leaderboard');
});

app.get('/boosts', (req, res) => {
  res.render('pages/boosts');
});

app.get('/profile', (req, res) => {
  res.render('pages/profile');
});

// Обработка статических страниц, таких как login.html
app.get('/login.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

io.on('connection', (socket) => {
  console.log('A user connected');

  socket.on('click', (data) => {
    console.log(`User clicked: ${data.clicks} times`);
    socket.emit('clickAcknowledged', { status: 'accepted' });
  });

  socket.on('disconnect', () => {
    console.log('A user disconnected');
  });
});

server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
