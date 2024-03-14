import {FC} from "react";
import {Button, Dropdown, Layout, MenuProps, theme} from "antd";
import {UserOutlined} from "@ant-design/icons";
import {useAuth} from "@/app/auth";
import {useTranslation} from "react-i18next";

const Header: FC = () => {
    const {
        token: {colorBgContainer},
    } = theme.useToken();

    const {t} = useTranslation();
    const {logout, email} = useAuth();

    const items: MenuProps["items"] = [
        {
            key: "0",
            label: email,
        },
        {
            key: "1",
            label: (
                <Button type="text" onClick={() => handleLogout()}>
                    {t("action.logout")}
                </Button>
            ),
        }
    ];

    const handleLogout = () => {
        console.debug("handleLogout");
        logout();
    }

    return (
        <Layout.Header style={{padding: 0, background: colorBgContainer}}>
            <div style={{paddingRight: 36, width: "100%", background: colorBgContainer, textAlign: "right"}}>
                <Dropdown menu={{items}} placement="bottom" arrow>
                    <Button shape="circle" style={{marginRight: 8}}>
                        <UserOutlined/>
                    </Button>
                </Dropdown>
            </div>
        </Layout.Header>
    );
};

export default Header;
