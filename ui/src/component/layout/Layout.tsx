import React, {FC} from "react";
import {Menu} from "../menu";
import {Layout as AntLayout} from "antd";
import {Header} from "../header";
import {Footer} from "../footer";
import {Outlet} from "react-router-dom";
import {Breadcrumbs} from "../breadcrumbs";

const Layout: FC = () => {
    return (
        <AntLayout style={{minHeight: "100vh"}}>
            <Menu/>
            <AntLayout>
                <Header />
                <AntLayout.Content style={{margin: "0 16px"}}>
                    <Breadcrumbs/>
                    <Outlet/>
                </AntLayout.Content>
                <Footer/>
            </AntLayout>
        </AntLayout>
    );
};

export default Layout;
