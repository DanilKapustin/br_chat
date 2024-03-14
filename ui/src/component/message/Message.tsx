import React, {FC} from "react";
import {Avatar, Button, Card, Col, Collapse, Divider, Row, Space, Tag, theme, Tooltip} from "antd";
import {MessageProps} from "./props";
import {MessageResult, MessageSource} from "@/api/message";
import {useTranslation} from "react-i18next";
import SyntaxHighlighter from "react-syntax-highlighter";
import {xt256} from "react-syntax-highlighter/dist/esm/styles/hljs";
import {
    CopyOutlined,
    DislikeFilled,
    DislikeOutlined,
    FileOutlined,
    LikeFilled,
    LikeOutlined,
    ReloadOutlined,
    RobotOutlined,
    UserOutlined
} from "@ant-design/icons";
import CopyToClipboard from "react-copy-to-clipboard";

export const Message: FC<MessageProps> = ({message, isLast, onRate, onRegenerate, loading}) => {
    const {
        token: {colorBgTextActive, colorBgElevated},
    } = theme.useToken();
    const {t} = useTranslation();

    const getMessageColor = (message: MessageResult): string => {
        if (message.is_error) {
            return "darkred";
        }

        return message.is_system ? colorBgTextActive : colorBgElevated;
    };

    const getTooltip = (source: MessageSource): JSX.Element => {
        let result: JSX.Element = <>{source.source_title}</>;

        if (source.subtitle) {
            result = <>
                {result} / {source.subtitle}
            </>;
        }

        if (source.url && !source.url.startsWith("http")) {
            result = <>
                {result}<br/>
                <span style={{fontSize: "60%", color: "#ddd"}}>{source.url}</span>
            </>;
        }

        return result;
    }

    const getSourceColor = (source: MessageSource): string => {
        if (source.url && source.url.startsWith("http")) {
            return "#1668dc";
        }

        return "#0e912b";
    };

    const renderText = (text: string): JSX.Element => {
        const regex: RegExp = /`([^`]+)`/g;
        const parts: string[] = text.split(regex);

        const elements: (JSX.Element | null)[] = parts
            .map((part: string, index: number) => {
                if (index % 2 === 0) {
                    return <>{part}</>;
                } else if (index % 2 === 1) {
                    return <span style={{fontFamily: "monospace", background: colorBgTextActive}}>{part}</span>;
                }

                // skip closing parts
                return null;
            })
            .filter(Boolean);

        return (
            <>
                {elements.map((element: JSX.Element | null) => (
                    <>{element}</>
                ))}
            </>
        );
    };

    const renderCode = (language: string, text: string): JSX.Element => {
        return (
            <>
                <Row>
                    <Col span={12}>
                        <b>
                            {t("description.code", {ns: "session", language: language})}:
                        </b>
                    </Col>
                    <Col span={12} style={{textAlign: "right"}}>
                        <CopyToClipboard text={text}>
                            <Button size="small">
                                <CopyOutlined/>
                                {t("action.copy_code", {ns: "session"})}
                            </Button>
                        </CopyToClipboard>
                    </Col>
                </Row>

                <SyntaxHighlighter
                    showLineNumbers={true}
                    language={language}
                    style={xt256}>
                    {text}
                </SyntaxHighlighter>
            </>
        );
    };

    const renderMessage = (message: MessageResult): JSX.Element => {
        const regex: RegExp = /```(\w*)\n([\s\S]*?)```/g;

        const matches: RegExpMatchArray[] = Array.from(message.message.matchAll(regex));
        const parts: string[] = message.message.split(regex);

        const elements: (JSX.Element | null)[] = parts
            .map((part: string, index: number) => {
                if (index % 3 === 0) {
                    return renderText(part);
                } else if (index % 3 === 1) {
                    const language = part;
                    const code = matches[(index - 1) / 3][2];
                    return renderCode(language, code);
                }

                // skip closing parts
                return null;
            })
            .filter(Boolean);

        return (
            <>
                {elements.map((element: JSX.Element | null) => (
                    <div>
                        {element}
                    </div>
                ))}
            </>
        );
    };

    const handleLike = (message: MessageResult) => {
        console.debug("handleLike, message=%o", message);
        onRate(message, 5);
    };

    const handleDislike = (message: MessageResult) => {
        console.debug("handleDislike, message=%o", message);
        onRate(message, 0);
    };

    const handleRegenerate = (message: MessageResult) => {
        console.debug("handleRegenerate, message=%o", message);
        onRegenerate(message);
    };

    return (
        <Row key={message.id}>
            <Col span={message.is_system ? 24 : 16} offset={message.is_system ? 0 : 8}>
                <Card style={{background: getMessageColor(message)}}>
                    <Card.Meta
                        avatar={<Avatar icon={message.is_system ? <RobotOutlined/> : <UserOutlined/>}/>}
                        title={message.created_by}
                        description={message.created_at}/>

                    <Divider/>

                    <Row>
                        <Col span={24} style={{whiteSpace: "pre-wrap"}}>
                            {renderMessage(message)}
                        </Col>
                    </Row>

                    {message.sources?.length > 0 &&
                        <Collapse
                            ghost
                            size="small"
                            style={{marginTop: 10}}
                            items={[{
                                key: "1", label: <b>{t("action.view_sources", {ns: "session"})}</b>, children:
                                    <Space size={[5, 10]} wrap>
                                        {message.sources.map((source: MessageSource) =>
                                            <Tooltip title={getTooltip(source)} placement="top">
                                                <Tag
                                                    color={getSourceColor(source)}
                                                    icon={<FileOutlined/>}
                                                    key={source.id}>
                                                    {source.url && source.url.startsWith("http") ?
                                                        <a href={source.url} target="_blank"
                                                           rel="noreferrer">{source.title}</a> : source.title}
                                                </Tag>
                                            </Tooltip>
                                        )}
                                    </Space>
                            }]}/>
                    }

                    {message.is_system &&
                        <Row style={{marginTop: 10}}>
                            <Col>
                                <Space size={[10, 10]} wrap>
                                    <Tooltip title={t("action.like", {ns: "session"})} placement="top">
                                        <Button
                                            loading={loading}
                                            shape="circle"
                                            icon={message.rating > 0 ? <LikeFilled/> : <LikeOutlined/>}
                                            onClick={() => handleLike(message)}/>
                                    </Tooltip>

                                    <Tooltip title={t("action.dislike", {ns: "session"})} placement="top">
                                        <Button
                                            loading={loading}
                                            shape="circle"
                                            icon={message.rating === 0 ? <DislikeFilled/> : <DislikeOutlined/>}
                                            onClick={() => handleDislike(message)}/>
                                    </Tooltip>

                                    {isLast &&
                                        <Tooltip title={t("action.regenerate", {ns: "session"})} placement="top">
                                            <Button
                                                loading={loading}
                                                shape="circle"
                                                icon={<ReloadOutlined/>}
                                                onClick={() => handleRegenerate(message)}/>
                                        </Tooltip>
                                    }
                                </Space>
                            </Col>
                        </Row>
                    }
                </Card>
            </Col>
        </Row>
    );
};
