const visionAPI = require("@google-cloud/vision");

class GoogleAPI {
  constructor(imageBuffer) {
    this.imageBuffer = imageBuffer;
    this.apiClient = new visionAPI.ImageAnnotatorClient();
  }
  async detectFaces() {
    const request = { image: { content: this.imageBuffer } };
    const response = await this.apiClient.faceDetection(request);
    const faces = response[0].faceAnnotations;
    return faces;
  }
  async extractText() {
    const request = { image: { content: this.imageBuffer } };
    const response = await this.apiClient.textDetection(request);
    const textAnnotations = response[0].fullTextAnnotation;
    return textAnnotations;
  }
}

module.exports = GoogleAPI;
