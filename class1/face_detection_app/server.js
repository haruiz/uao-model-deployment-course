const express = require("express");
const path = require("path");
const app = express();
const multer = require("multer");
const upload = multer();
const GoogleAPI = require("./GoogleApi");

// process.env["GOOGLE_APPLICATION_CREDENTIALS"] =
//   "/home/haruiz/uao-face-detection-cd951b31b2bf.json";

const publicFolder = path.join(__dirname, "public");
app.use("/public", express.static(publicFolder));

app.get("/", (req, res) => {
  const indexFilePath = path.join(__dirname, "public/index.html");
  return res.sendFile(indexFilePath);
});

app.post("/uploadImage", upload.none(), async (req, res) => {
  const imageBase64 = req.body["image"].replace(
    /^data:image\/jpeg;base64,/,
    ""
  );
  const name = req.body["name"];
  const imageBuffer = Buffer.from(imageBase64, "base64");
  const googleApi = new GoogleAPI(imageBuffer);
  const facesAnnotations = await googleApi.detectFaces();
  const textAnnotations = await googleApi.extractText();
  const all = { textAnnotations, facesAnnotations };
  return res.json(all);
});

app.listen(8080, function () {
  console.log("The server is running");
});
