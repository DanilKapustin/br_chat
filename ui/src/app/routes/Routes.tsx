import { createBrowserRouter, createRoutesFromElements, Route, Outlet, Navigate } from 'react-router-dom';
import {Dashboard} from "@/page/dashboard";
import {Knowledge} from "@/page/knowledge";
import {Source} from "@/page/source";
import {Session, SessionTool} from "@/page/session";
import {Layout} from "@/component/layout";
import {Configuration} from "@/page/configuration";
import {Model} from "@/page/model";
import {Tool} from "@/page/tool";
import {SessionApi} from "@/api/session";
import {LoginPage} from "@/page/login/LoginPage";
import {RegisterPage} from "@/page/register/RegisterPage";
import ProtectedRoute from "./ProtectedRoute";

const sessionApi = new SessionApi({});

export const Routes = (): any => {
    return createBrowserRouter(
        createRoutesFromElements(
            <Route>
                <Route path={"/login"} element={<LoginPage />} />
                <Route path={"/register"} element={<RegisterPage />} />
                <Route path="/" element={<ProtectedRoute />} handle="menu:dashboard">
                    <Route element={<Layout />}>
                        <Route index element={<Dashboard />} />
                        <Route path={"/session"} element={<Outlet/>} handle="menu:sessions">
                            <Route path={""} element={<Session/>}/>
                            <Route path={"/session/start"} element={<SessionTool/>} handle="session:action.start"/>
                            <Route
                                path={"/session/:sessionId"}
                                element={<SessionTool/>}
                                loader={({params}) => sessionApi.get(params.sessionId || "")}
                                handle={(data: any) => data.title}/>
                        </Route>
                        <Route path={"/source"} element={<Source/>} handle="menu:sources"/>
                        <Route path={"/knowledge"} element={<Knowledge/>} handle="menu:knowledgeDb"/>
                        <Route path={"/configuration"} element={<Configuration/>} handle="menu:configuration"/>
                        <Route path={"/model"} element={<Model/>} handle="menu:models"/>
                        <Route path={"/tool"} element={<Tool/>} handle="menu:tools"/>
                        <Route path={"*"} element={<Navigate to="/" />} />
                    </Route>
                </Route>
            </Route>
        )
    );
};
