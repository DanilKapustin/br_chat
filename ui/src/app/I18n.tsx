import i18n from "i18next";
import {initReactI18next} from "react-i18next";
import Backend, { HttpBackendOptions } from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

const backendOptions: HttpBackendOptions = {
    loadPath: "/locales/{{lng}}/{{ns}}.json",
};

const isDev = process.env.NODE_ENV === "development";
const defaultLanguage = "ru";

// eslint-disable-next-line import/no-named-as-default-member
i18n.use(Backend)
    .use(LanguageDetector)
    .use(initReactI18next)
    .init<HttpBackendOptions>({
        ns: [
            "menu",
            "configuration",
            "dialog",
            "error",
            "knowledge",
            "session",
            "source",
            "translations",
            "model",
            "tool",
            "question_answering",
            "dashboard",
            "login_registration",
        ],
        defaultNS: "translation",
        backend: backendOptions,
        lng: localStorage.getItem("language") || defaultLanguage,
        fallbackLng: defaultLanguage,
        debug: isDev,
        react: {
            useSuspense: true,
        }
    })
    .catch((error) => console.log(error));

export { i18n };
export { defaultLanguage };
