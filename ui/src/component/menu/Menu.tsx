import React, {FC, useState} from "react";
import {Layout} from "antd";
import {Menu as AMenu, theme} from "antd";
import "./Menu.css";
import {useNavigate, useLocation} from "react-router-dom";
import {useTranslation} from "react-i18next";
import type {MenuProps} from "antd";
import {
    DashboardOutlined,
    CloudDownloadOutlined,
    DatabaseOutlined,
    MessageOutlined,
    RobotOutlined,
    SettingOutlined, 
    ToolOutlined
} from "@ant-design/icons";
import LogoStack from "./logo-brc.svg";

type MenuItem = Required<MenuProps>["items"][number];

const Menu: FC = () => {
    const {t} = useTranslation();
    const [collapsed, setCollapsed] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    function item(label: React.ReactNode, key: React.Key, icon?: React.ReactNode, children?: MenuItem[]): MenuItem {
        return {key, icon, label, children} as MenuItem;
    }

    function divider(): MenuItem {
        return {type: "divider"} as MenuItem;
    }

    function getSelectedMenuItems(): string[] {
        const result: string[] = [];
        var currentPath = "";

        location.pathname.split("/").forEach((path) => {
            if (path === "") {
                return;
            }

            currentPath += "/" + path;
            result.push(currentPath);
        })

        return result;
    }

    return (
        <Layout.Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)} theme="light">
            <div className={collapsed ? "logo-collapsed" : "logo"}>
                <img src={LogoStack} style={{height: 24}} alt="logo" />
            </div>
            <AMenu
                selectedKeys={getSelectedMenuItems()}
                mode="inline"
                onClick={({key}) => navigate(key)}
                items={[
                    item(t("dashboard", {ns: "menu"}), "/", <DashboardOutlined/>),
                    item(t("sessions", {ns: "menu"}), "/session", <MessageOutlined/>),
                    divider(),
                    item(t("sources", {ns: "menu"}), "/source", <CloudDownloadOutlined/>),
                    item(t("knowledgeDb", {ns: "menu"}), "/knowledge", <DatabaseOutlined/>),
                    divider(),
                    item(t("configuration", {ns: "menu"}), "/configuration", <SettingOutlined/>),
                    item(t("models", {ns: "menu"}), "/model", <RobotOutlined/>),
                    item(t("tools", {ns: "menu"}), "/tool", <ToolOutlined/>)
                ]}/>
        </Layout.Sider>
    );
};

export default Menu;