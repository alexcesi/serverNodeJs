const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const cors = require('cors');
const app = express();
const port = 3001;

app.use(cors());
app.use(bodyParser.json());

app.post('/api/call-script', (req, res) => {
    const { idArticle, quantity } = req.body;

    console.log('idArticle:', idArticle);
    console.log('quantity:', quantity);

    const command = `python main.py ${idArticle} ${quantity}`;
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Erreur lors de l'exécution du script : ${error}`);
            res.json({
                success: false,
                error: "Erreur lors de l'exécution du script."
            });
            return;
        }
        console.log(stdout)

        res.json({ success: true, result: stdout });
    });
});

app.listen(port, () => {
    console.log(`Le serveur fonctionne sur le port ${port}`);
});
