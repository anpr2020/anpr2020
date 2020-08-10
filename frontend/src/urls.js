import Location from "react-app-location";
import * as Yup from "yup";

const djangoServerUrl = "http://127.0.0.1:8000/", djangoWSUrl = "ws://127.0.0.1:8000/ws/";

const urls = {
  Upload: ["/upload"],
  Live: ["/live"],
  Progress: [
    "/progress/:id",
    { id: Yup.string().required() },
  ],
};

const djangoUrls = {
  Process: djangoServerUrl + "process/",
  Progress: djangoWSUrl + "progress/",
};

for (let url in urls) urls[url] = new Location(...urls[url]);

window.djangoUrls = djangoUrls;
window.urls = urls;
