import {FC, useEffect, useState} from "react";
import {App, Button, Col, Modal, Row, Space, Table, theme} from "antd";
import {KnowledgeApi, KnowledgeResult, KnowledgeResultPage} from "@/api/knowledge";
import {FilterValue, SorterResult} from "antd/es/table/interface";
import {ClearOutlined, DeleteOutlined, ExclamationCircleOutlined, InfoCircleOutlined} from "@ant-design/icons";
import {ColumnsType} from "antd/es/table";
import {useTranslation} from "react-i18next";
import "./Knowledge.css";

export const Knowledge: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();

    const {t} = useTranslation();
    const api = new KnowledgeApi({});
    const [data, setData] = useState<KnowledgeResult[]>([]);
    const [tableParams, setTableParams] = useState({
        current: 1,
        pageSize: 10,
        total: 0
    });
    const [loading, setLoading] = useState(false);
    const [textModalOpen, setTextModalOpen] = useState(false);
    const [textModalTitle, setTextModalTitle] = useState("Loading...");
    const [textModalContent, setTextModalContent] = useState("Loading...");
    const {message, modal} = App.useApp();

    const loadList = async () => {
        console.debug("loadList");
        setLoading(true);

        try {
            const response: KnowledgeResultPage = await api.getList(tableParams.current, tableParams.pageSize);
            setData(response.items);

            if (tableParams.total == 0 && response.total != tableParams.total) {
                console.log("loadList, setting total");
                setTableParams({...tableParams, total: response.total});
                return;
            }
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false);
        }
    };

    const handleTableChange = (
        pagination: any,
        filters: Record<string, FilterValue | null>,
        sorter: SorterResult<KnowledgeResult> | SorterResult<KnowledgeResult>[],
    ) => {
        console.debug("handleTableChange, page=%s, size=%s", pagination.current, pagination.pageSize);
        setTableParams({...tableParams, current: pagination.current, pageSize: pagination.pageSize});
    };

    const openDeleteModal = (knowledge: KnowledgeResult) => {
        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.delete", {ns: "knowledge", title: knowledge.title}),
            onOk() {
                console.debug("openDeleteModal, onOk");

                const asyncDelete = async () => {
                    await api.delete(knowledge.id);
                    await loadList();
                };

                asyncDelete().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const openDeleteAllModal = () => {
        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.deleteAll", {ns: "knowledge"}),
            onOk() {
                console.debug("openDeleteAllModal, onOk");

                const asyncDelete = async () => {
                    await api.deleteAll();
                    await loadList();
                };

                asyncDelete().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const openTextModal = (knowledge: KnowledgeResult) => {
        setTextModalContent(knowledge.text);
        setTextModalTitle(knowledge.title);
        setTextModalOpen(true);
    };

    const columns: ColumnsType<KnowledgeResult> = [
        {
            title: t("column.title"),
            dataIndex: "title",
            key: "title",
            render: (_, record: KnowledgeResult) => <>
                {(record.url.startsWith("http") && <a href={record.url} target="_blank">{record.title}</a>) ||
                    record.title}
                {record.subtitle ? <div className="subtitle">{record.subtitle}</div> : null}
            </>,
        },
        {
            title: t("column.source"),
            dataIndex: "source_title",
            key: "source_title",
            width: "20vw",
        },
        {
            title: t("column.chunk", {ns: "knowledge"}),
            dataIndex: "chunk",
            key: "chunk",
            width: "5vw",
            render: (_, record: KnowledgeResult) => (
                <>
                    {record.chunk} / {record.total_chunks}
                </>
            )
        },
        {
            title: t("column.actions"),
            key: "actions",
            width: "5vw",
            render: (_, record: KnowledgeResult) => (
                <Space size="middle">
                    <Button
                        type="default"
                        icon={<InfoCircleOutlined/>}
                        size="small"
                        title={t("action.text", {ns: "knowledge"})}
                        onClick={() => openTextModal(record)}/>

                    <Button
                        type="primary"
                        icon={<DeleteOutlined/>}
                        size="small"
                        danger
                        title={t("action.delete")}
                        onClick={() => openDeleteModal(record)}/>
                </Space>
            ),
        },
    ];

    useEffect(() => {
        loadList();
    }, [tableParams]);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12} offset={12} style={{textAlign: "right"}}>
                        <Button type="primary" danger onClick={() => openDeleteAllModal()}>
                            <ClearOutlined/>
                            {t("action.deleteAll", {ns: "knowledge"})}
                        </Button>
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

            <Modal
                title={textModalTitle}
                centered
                open={textModalOpen}
                onOk={() => setTextModalOpen(false)}
                onCancel={() => setTextModalOpen(false)}
                width="50vw">
                <div className="text-modal">{textModalContent}</div>
            </Modal>
        </div>
    );
};
