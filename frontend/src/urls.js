const djangoServerUrl = "http://127.0.0.1:8000/";

const djangoUrls = {
  Process: "process/"
};

for (let url in djangoUrls) djangoUrls[url] = djangoServerUrl + djangoUrls[url];

export default djangoUrls;
