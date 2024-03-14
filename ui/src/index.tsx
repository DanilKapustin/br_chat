import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./app/App";
import "./app/I18n";
import reportWebVitals from "./reportWebVitals";
import axios, {AxiosResponse} from "axios";

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

axios.defaults.validateStatus = (status: number) => {
    return status === 200 || status === 201 || status === 204;
};

axios.interceptors.response.use((response: AxiosResponse) => {
    return response;
}, (error) => {
    if (error.response.status === 401) {
        localStorage.removeItem("token");
        return window.location.href = "/login";
    }

    return Promise.reject(error);
});

axios.interceptors.request.use(
    (config) => {
        const token: string | null = localStorage.getItem("token");
        config.headers.Authorization = token ? `Bearer ${token}` : '';
        return config;
    }
)

root.render(
    <App/>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
