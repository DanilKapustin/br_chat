import React, {FC} from "react";
import {Breadcrumb} from "antd";
import {useMatches, useLocation} from "react-router-dom";
import {useTranslation} from "react-i18next";

interface BreadcrumbItem {
    title: any;
}

const Breadcrumbs: FC = () => {
    const matches = useMatches();
    const location = useLocation();
    const {t} = useTranslation();

    let crumbs: BreadcrumbItem[] | string = matches
        .filter((match: any) => Boolean(match.handle))
        .map((match: any) => {
            let path: string | undefined = match.pathname;
            let title: string = t(match.handle);

            if (path === location.pathname) {
                path = undefined;
            }

            if (typeof match.handle !== "string") {
                title = match.handle(match.data);
            }

            if (path === undefined) {
                return {title: title};
            }

            return {title: <a key={path} href={path}>{title}</a>};
        });

    return (
        <Breadcrumb style={{margin: "16px 0"}} items={crumbs}/>
    );
};

export default Breadcrumbs;
