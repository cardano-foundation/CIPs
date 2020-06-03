const path = require('path')
const express = require('express')
const app = express()

app.use(express.static(path.join(__dirname, '..', 'public')))
app.listen(5000, 'localhost')
console.log('listening on http://localhost:5000')
