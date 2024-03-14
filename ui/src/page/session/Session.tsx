import {FC, useEffect, useState} from "react";
import {App, Button, Col, Dropdown, MenuProps, Row, Space, Table, Tag, theme} from "antd";
import {DeleteOutlined, DownOutlined, ExclamationCircleOutlined, MessageOutlined} from "@ant-design/icons";
import {ColumnsType} from "antd/es/table";
import {FilterValue, SorterResult} from "antd/es/table/interface";
import {Link, useNavigate} from "react-router-dom";
import {useTranslation} from "react-i18next";
import {SessionApi, SessionPageResult, SessionResult} from "@/api/session";
import {ToolApi, ToolResult} from "@/api/tool";

export const Session: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();

    const {t} = useTranslation();
    const api = new SessionApi({});
    const toolApi = new ToolApi({});
    const navigate = useNavigate();

    const [data, setData] = useState<SessionResult[]>([]);
    const [tools, setTools] = useState<ToolResult[]>([]);
    const [tableParams, setTableParams] = useState({
        current: 1,
        pageSize: 10,
        total: 0
    });
    const [loading, setLoading] = useState(false);
    const {message, modal} = App.useApp();

    const loadList = async () => {
        console.debug("loadList");
        setLoading(true);

        try {
            const response: SessionPageResult = await api.getList(tableParams.current, tableParams.pageSize);
            setData(response.items);

            if (tableParams.total !== response.total) {
                console.log("loadList, setting total");
                setTableParams({...tableParams, total: response.total});
                return;
            }
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false)
        }
    };

    const loadTools = async () => {
        console.debug("loadTools");
        setLoading(true);

        try {
            const response: ToolResult[] = await toolApi.getAll();
            setTools(response);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false)
        }
    };

    const handleTableChange = (
        pagination: any,
        filters: Record<string, FilterValue | null>,
        sorter: SorterResult<SessionResult> | SorterResult<SessionResult>[],
    ) => {
        console.debug("handleTableChange, page=%s, size=%s", pagination.current, pagination.pageSize);
        setTableParams({...tableParams, current: pagination.current, pageSize: pagination.pageSize});
    };

    const openDeleteModal = (session: SessionResult) => {
        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.delete", {ns: "session"}),
            onOk() {
                const asyncDelete = async () => {
                    await api.delete(session.id);
                    await loadList();
                };

                asyncDelete().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    };

    const startSession = (toolId: string) => {
        console.debug("startSession, toolId=%s", toolId);
        navigate("/session/start", {state: {toolId: toolId}});
    };

    const getToolTitle = (toolId: string): string => {
        return tools.find((tool) => tool?.id === toolId)?.title || "N/A";
    };

    const getToolMenu = (): MenuProps => {
        return {
            items: tools.map((tool) => {
                return {
                    key: tool.id,
                    label: tool.title
                };
            }),
            onClick: ({key}) => {
                console.debug("getToolMenu, onClick, toolId=%s", key)
                startSession(key);
            }
        } as MenuProps;
    };

    const columns: ColumnsType<SessionResult> = [
        {
            title: t("column.title"),
            dataIndex: "title",
            key: "title",
            render: (text, record: SessionResult) => <Link to={`/session/${record.id}`}>{text}</Link>,
        },
        {
            title: t("column.tool", {ns: "session"}),
            key: "tool_id",
            dataIndex: "tool_id",
            width: "20vw",
            render: (toolId) => (
                <Tag key={toolId}>
                    {getToolTitle(toolId)}
                </Tag>
            ),
        },
        {
            title: t("column.created"),
            dataIndex: "created_at",
            key: "created_at",
            width: "10vw",
        },
        {
            title: t("column.actions"),
            key: "actions",
            width: "5vw",
            render: (_, record: SessionResult) => (
                <Space size="middle">
                    <Button
                        type="primary"
                        title={t("action.delete")}
                        icon={<DeleteOutlined/>}
                        size="small"
                        danger
                        onClick={() => openDeleteModal(record)}/>
                </Space>
            ),
        },
    ];

    useEffect(() => {
        console.log("page.Session, mount");

        const init = async () => {
            await loadList();
            await loadTools();
        };

        init().catch(console.error);

        return () => {
            console.log("page.Session, unmount");
        }
    }, [tableParams]);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12} offset={12} style={{textAlign: "right"}}>
                        <Dropdown menu={getToolMenu()}>
                            <Button type="primary">
                                <Space>
                                    <MessageOutlined/>
                                    {t("action.start", {ns: "session"})}
                                    <DownOutlined/>
                                </Space>
                            </Button>
                        </Dropdown>
                    </Col>
                </Row>

                <Table
                    rowKey={(record) => record.id}
                    columns={columns}
                    dataSource={data}
                    pagination={tableParams}
                    onChange={handleTableChange}
                    loading={loading}>
                </Table>
            </Space>
        </div>
    );
};
