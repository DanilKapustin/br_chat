import React, {FC, lazy, LazyExoticComponent, ReactNode, Suspense, useEffect, useState} from "react";
import {App, Button, Col, Row, Space, theme} from "antd";
import {LeftOutlined} from "@ant-design/icons";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import {useTranslation} from "react-i18next";
import {ToolProps} from "@/tool";
import {SessionApi, SessionResult} from "@/api/session";
import {ToolApi, ToolResult} from "@/api/tool";

const QuestionAnswering = lazy(() => import("@/tool/question_answering"));

export const SessionTool: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();

    const {t} = useTranslation();
    const navigate = useNavigate();
    const sessionApi = new SessionApi({});
    const toolApi = new ToolApi({});
    const {sessionId} = useParams();
    const {toolId} = useLocation().state || {};
    const [loading, setLoading] = useState(false);
    const [tool, setTool] = useState<ToolResult | null>(null);
    const {message} = App.useApp();

    const loadSession = async () => {
        console.debug("loadSession");
        setLoading(true);

        if (sessionId === null) {
            console.warn("loadSession, sessionId is null");
            return;
        }

        try {
            const session: SessionResult = await sessionApi.get(sessionId || "");
            await loadTool(session.tool_id);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const loadTool = async (toolId: string) => {
        console.debug("loadTool, toolId=%s", toolId);
        setLoading(true);

        try {
            const tool: ToolResult = await toolApi.get(toolId);
            setTool(tool);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const goToSessionList = () => {
        console.debug("goToSessionList");
        navigate("/session");
    };

    const TOOL_NAME_TO_PAGE_COMPONENT: Record<string, LazyExoticComponent<FC<ToolProps>>> = {
        "question_answering": QuestionAnswering,
    };

    const getComponent = (): ReactNode => {
        const fallbackComponent: ReactNode = <div>{t("message.loading", {ns: "session"})}</div>;

        if (tool === null) {
            return fallbackComponent;
        }

        const ToolNode = TOOL_NAME_TO_PAGE_COMPONENT[tool.name] || fallbackComponent;
        const props: ToolProps = {
            sessionId,
            toolId
        };

        return (
            <ToolNode {...props} />
        );
    };

    useEffect(() => {
        console.log("page.Tool, mount");

        const init = async () => {
            if (sessionId) {
                await loadSession();
            } else if (toolId) {
                await loadTool(toolId);
            }
        };

        init().catch(console.error);

        return () => {
            console.log("page.Tool, unmount");
        }
    }, [sessionId]);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12}>
                        <b>{tool?.title || t("message.loading", {ns: "session"})}</b>
                    </Col>
                    <Col span={12} style={{textAlign: "right"}}>
                        <Button type="default" onClick={goToSessionList}>
                            <LeftOutlined/>
                            {t("action.back")}
                        </Button>
                    </Col>
                </Row>
            </Space>

            <Suspense fallback={<div>{t("message.loading", {ns: "session"})}</div>}>
                {getComponent()}
            </Suspense>
        </div>
    );
}
