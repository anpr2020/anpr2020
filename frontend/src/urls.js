import Location from "react-app-location";

const urls = {
	HomeLocation: "/",
	ResultLocation : "/result"
};

const djangoServerUrl = "http://127.0.0.1:8000/";

const djangoUrls = {
  Process: "process/"
};

for (let url in djangoUrls) djangoUrls[url] = djangoServerUrl + djangoUrls[url];

for (let url in urls) urls[url] = new Location(urls[url]);

export { djangoUrls };

export default urls;
