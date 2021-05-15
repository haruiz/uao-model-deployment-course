const express = require("express");
const path = require("path");
const app = express();

const publicFolder = path.join(__dirname, "public");
app.use("/public", express.static(publicFolder));

app.get("/", (req, res)=>{	
	const indexFilePath = path.join(__dirname, "public/index.html")
	return res.sendFile(indexFilePath);
});

app.post("/uploadImage", (req, res)=>{	
		return res.send("almost done!");
});

app.listen(8080, function(){
	console.log("The server is running");
});


