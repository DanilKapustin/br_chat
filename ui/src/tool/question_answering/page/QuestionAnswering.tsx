import {FC, useEffect, useRef, useState} from "react";
import {App, Button, Form, Input, Space, Spin, theme} from "antd";
import {SessionApi, SessionCreatePayload, SessionResult} from "@/api/session";
import {MessageCreatePayload, MessageResult} from "@/api/message";
import {useTranslation} from "react-i18next";
import {QuestionAnsweringApi} from "../api";
import {ToolProps} from "@/tool";
import {Message} from "@/component/message";

export const QuestionAnswering: FC<ToolProps> = ({sessionId, toolId}: ToolProps) => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();

    const {t} = useTranslation();
    const sessionApi = new SessionApi({});
    const api = new QuestionAnsweringApi({});
    const {message} = App.useApp();

    const [currentSessionId, setCurrentSessionId] = useState(sessionId);
    const [messages, setMessages] = useState<MessageResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [waitingForMessage, setWaitingForMessage] = useState(false);
    const websocket = useRef<WebSocket | null>(null);

    const loadMessages = async () => {
        console.debug("loadMessages");
        setLoading(true);

        try {
            const messages: MessageResult[] = await api.getMessages(currentSessionId as string, 0, 1000);
            setMessages(messages);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const createMessage = async (form: MessageCreatePayload) => {
        console.debug("createMessage, form=%o", form);
        setLoading(true);

        try {
            if (!currentSessionId) {
                const session: SessionResult = await sessionApi.create({
                    title: form.message,
                    tool_id: toolId as string,
                } as SessionCreatePayload);

                console.debug("got session, session=%o", session);
                setCurrentSessionId(session.id);
            } else {
                const message: MessageResult = await api.createMessage(currentSessionId as string, form);
                setMessages((oldMessages: any) => [...oldMessages, message]);
            }

            setWaitingForMessage(true);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const openWebsocket = () => {
        console.debug("openWebsocket");

        if (websocket.current !== null) {
            console.warn("openWebsocket, websocket already open");
            return;
        }

        const ws: WebSocket = api.createWebsocket(currentSessionId as string);

        ws.onopen = () => console.debug("Websocket opened");
        ws.onclose = () => console.debug("Websocket closed");
        ws.onerror = () => console.debug("Websocket error");
        ws.onmessage = getWebsocketMessage;

        websocket.current = ws;
    };

    const closeWebsocket = () => {
        console.debug("closeWebsocket");

        if (websocket.current !== null) {
            api.closeWebsocket(websocket.current);
            websocket.current = null;
        }
    };

    const getWebsocketMessage = (message: MessageEvent) => {
        console.debug("getWebsocketMessage, message=%o", message);

        if (message.data === "ping") {
            return;
        }

        setMessages((oldMessages: any) => [...oldMessages, JSON.parse(message.data)]);
        setWaitingForMessage(false);
    };

    const onRate = async (msg: MessageResult, rating: number) => {
        console.debug("onRate, message=%o, rating=%o", msg, rating);

        setLoading(true);

        try {
            await api.rate(msg.session_id, msg.id, rating);
            msg.rating = rating;
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const onRegenerate = async (msg: MessageResult) => {
        console.debug("onRegenerate, msg=%o", message);

        setLoading(true);

        try {
            await api.regenerate(msg.session_id, msg.id);
            setMessages((oldMessages: any) => oldMessages.slice(0, -1));
            setWaitingForMessage(true);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const initSession = async () => {
        await loadMessages();
        openWebsocket();
    };

    useEffect(() => {
        console.log("question_answering, mount");

        if (currentSessionId) {
            const init = async () => {
                await initSession();
            }

            init().catch(console.error);
        }

        return () => {
            console.log("question_answering, unmount");
            closeWebsocket();
        }
    }, [currentSessionId]);

    return (
        <div style={{paddingTop: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                {messages.map((message: MessageResult, index: number) =>
                    <Message
                        message={message}
                        isLast={index + 1 === messages.length}
                        onRate={onRate}
                        onRegenerate={onRegenerate}
                        loading={loading}/>
                )}

                {waitingForMessage &&
                    <div>
                        <Spin/>
                    </div>
                }

                <Form
                    labelCol={{span: 8}}
                    wrapperCol={{span: 16}}
                    initialValues={{remember: true}}
                    onFinish={createMessage}
                    autoComplete="off">
                    <Form.Item
                        label={t("column.message", {ns: "question_answering"})}
                        name="message">
                        <Input.TextArea rows={6}/>
                    </Form.Item>

                    <Form.Item wrapperCol={{offset: 8, span: 16}}>
                        <Button type="primary" htmlType="submit" loading={loading}>
                            {t("action.send", {ns: "question_answering"})}
                        </Button>
                    </Form.Item>
                </Form>
            </Space>
        </div>
    );
};
