import "./App.css";
import type {Locale} from "antd/es/locale";
import ruRU from "antd/locale/ru_RU";
import {App as AntApp, ConfigProvider, theme} from "antd";
import {Routes} from "./routes";
import {RouterProvider} from "react-router-dom";
import {defaultLanguage} from "./I18n";
import {AuthProvider} from "@/app/auth";

function App() {
    const translationMap: Record<string, Locale> = {
        "ru": ruRU
    };
    const getLanguage = () => translationMap[defaultLanguage];

    return (
        <ConfigProvider
            theme={{algorithm: theme.defaultAlgorithm}}
            locale={getLanguage()}>
            <AntApp>
                <AuthProvider>
                    <RouterProvider router={Routes()}/>
                </AuthProvider>
            </AntApp>
        </ConfigProvider>
    );
}

export default App;
