import {FC, useEffect, useState} from "react";
import {
    App,
    Button,
    Checkbox,
    Col,
    Drawer,
    Form,
    Input,
    Progress,
    Row,
    Select,
    Space,
    Table,
    Tag,
    theme,
    Upload
} from "antd";
import {SourceApi, SourceCreatePayload, SourceResult} from "@/api/source";
import {
    DeleteOutlined,
    ExclamationCircleOutlined,
    PlusOutlined,
    ReloadOutlined,
    SaveOutlined,
    UploadOutlined
} from "@ant-design/icons";
import {ColumnsType} from "antd/es/table";
import type {RcFile, UploadFile, UploadProps} from "antd/es/upload/interface";
import {FilterValue, SorterResult} from "antd/es/table/interface";
import Password from "antd/es/input/Password";
import {useTranslation} from "react-i18next";

const ALLOWED_FILE_EXTENSIONS: string[] = ["txt", "csv", "pdf", "docx", "xlsx", "zip", "xml", "md"];

export const Source: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();
    
    const {t} = useTranslation();
    const api = new SourceApi({});
    const {message, modal} = App.useApp();

    const [data, setData] = useState([]);
    const [tableParams, setTableParams] = useState({
        current: 1,
        pageSize: 10,
        total: 0
    });
    const [loading, setLoading] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [fileList, setFileList] = useState<UploadFile[]>([]);
    const [saving, setSaving] = useState(false);
    const [formType, setFormType] = useState("UPLOAD");
    const [editId, setEditId]= useState("");
    const [editType, setEditType] = useState("");
    const [form] = Form.useForm();
    const [loadTimeout, setLoadTimeout] = useState<any>(null);

    const loadList = () => {
        console.debug("loadList");
        setLoading(true);

        api.getList(tableParams.current, tableParams.pageSize)
            .then((response: any) => {
                setData(response.items);

                if (tableParams.total !== response.total) {
                    console.log("loadList, setting total");
                    setTableParams({...tableParams, total: response.total});
                    return;
                }

                let isIndexing: boolean = response.items.some((item: SourceResult) => item.status === "INDEXING" || item.status === "NEW");

                if (isIndexing && loadTimeout === null) {
                    console.log("loadList, setting timeout");
                    setLoadTimeout(setTimeout(() => loadList(), 5000));
                } else if (!isIndexing && loadTimeout !== null) {
                    clearTimeout(loadTimeout);
                    setLoadTimeout(null);
                }
            })
            .catch((error: any) => message.error(t("message.error.server")))
            .finally(() => setLoading(false));
    };

    const handleTableChange = (
        pagination: any,
        filters: Record<string, FilterValue | null>,
        sorter: SorterResult<SourceResult> | SorterResult<SourceResult>[],
    ) => {
        console.debug("handleTableChange, page=%s, size=%s", pagination.current, pagination.pageSize);
        setTableParams({...tableParams, current: pagination.current, pageSize: pagination.pageSize});
    };

    const handleTypeChange = (type: string) => {
        setFormType(type);
    };

    const openDrawer = () => {
        setDrawerOpen(true);
    };

    const closeDrawer = () => {
        form.resetFields();
        setEditId("");
        setEditType("");

        setDrawerOpen(false);
    };

    const openEditForm = (source: SourceResult) => {
        form.resetFields();

        form.setFieldsValue({...source, ...source.configuration});
        setFormType(source.type);
        setEditId(source.id);
        setEditType(source.type);

        setDrawerOpen(true);
    };

    const openDeleteModal = (source: SourceResult) => {
        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.delete", {ns: "source", title: source.title}),
            onOk() {
                api.delete(source.id)
                    .then(() => loadList())
                    .catch((error: Error) => message.error(t("message.error.server")));
            }
        });
    }

    const openReindexModal = (source: SourceResult) => {
        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.reindex", {ns: "source", title: source.title}),
            onOk() {
                api.reindex(source.id)
                    .then(() => loadList())
                    .catch((error: Error) => message.error(t("message.error.server")));
            }
        });
    }

    const createSource = (form: SourceCreatePayload) => {
        console.debug("createSource, form=%o", form);

        const file: RcFile | null = fileList.length > 0 ? fileList[0] as RcFile : null;
        setSaving(true);

        api.create(form, file)
            .then(() => {
                setFileList([]);
                message.success(t("message.success.created", {ns: "source"}));

                closeDrawer();
                loadList();
            })
            .catch((error: any) => message.error(t("message.error.server")))
            .finally(() => setSaving(false));
    };

    const updateSource = (form: SourceCreatePayload) => {
        console.debug("updateSource, form=%o", form);

        setSaving(true);

        api.update(editId, editType, form)
            .then(() => {
                message.success(t("message.success.updated", {ns: "source"}));

                closeDrawer();
                loadList();
            })
            .catch((error: any) => message.error(t("message.error.server")))
            .finally(() => setSaving(false));
    };

    const fileUploadProperties: UploadProps = {
        onRemove: (file) => {
            const index = fileList.indexOf(file);
            const newFileList = fileList.slice();
            newFileList.splice(index, 1);

            setFileList(newFileList);
        },

        beforeUpload: (file) => {
            const allowedFileExtension: boolean = ALLOWED_FILE_EXTENSIONS.includes(file.name.split(".").pop() || "");

            if (!allowedFileExtension) {
                message.error(t("message.error.fileType", {ns: "source", "file": file.name}));
                return Upload.LIST_IGNORE;
            }

            setFileList([file]);
            form.setFieldValue("title", file.name);

            return false;
        },

        fileList,
    };

    const sourceCanBeEdited = (source: SourceResult) => {
        return (source.status === "FINISHED" || source.status === "ERROR") && source.type !== "UPLOAD";
    };

    const sourceCanBeReindexed = (source: SourceResult) => {
        return (source.status === "FINISHED" || source.status === "NEW" || source.status === "ERROR") && source.type !== "UPLOAD";
    };

    const sourceCanBeDeleted = (source: SourceResult) => {
        return source.status === "FINISHED" || source.status === "ERROR";
    };

    const sourceTypes: any = {
        "UPLOAD": t("type.upload", {ns: "source"}),
        "CONFLUENCE": "Confluence",
        "JIRA": "JIRA"
    };

    const statusColors: any = {
        "NEW": "blue",
        "FINISHED": "green",
        "ERROR": "red"
    };

    const columns: ColumnsType<SourceResult> = [
        {
            title: t("column.title"),
            dataIndex: "title",
            key: "title",
            render: (text, record: SourceResult) => (
                <>
                    {
                        sourceCanBeEdited(record) && 
                        <a onClick={() => openEditForm(record)}>{text}</a> ||
                        <span>{text}</span>
                    }
                </>
            ),
        },
        {
            title: t("column.type"),
            dataIndex: "type",
            key: "type",
            width: "10vw",
            render: (type) => (
                <Tag key={type}>
                    {t([`type.${type}`, type.toUpperCase()], {ns: "source"})}
                </Tag>
            ),
        },
        {
            title: t("column.documents", {ns: "source"}),
            dataIndex: "document_count",
            key: "document_count",
            width: "10vw",
            render: (document_count, record: SourceResult) => (
                <>                    
                    {
                        record.status === "INDEXING" && 
                        <>{record.progress?.indexed_count || 0} of {record.progress?.document_count || 0}</> ||
                        <>{document_count}</>
                    }
                </>
            ),
        },
        {
            title: t("column.created"),
            dataIndex: "created_at",
            key: "created_at",
            width: "10vw",
        },
        {
            title: t("column.updated"),
            dataIndex: "updated_at",
            key: "updated_at",
            width: "10vw",
        },
        {
            title: t("column.status"),
            key: "status",
            dataIndex: "status",
            width: "10vw",
            render: (status, record: SourceResult) => (
                <>                    
                    {
                        status === "INDEXING" && 
                        <Progress percent={record.progress.progress.toFixed(2)} showInfo={true} size={["80%", 5]} /> ||
                        <Tag color={statusColors[status]} key={status}>
                            {t([`status.${status}`, status.toUpperCase()], {ns: "source"}).toUpperCase()}
                        </Tag>
                    }
                </>
            ),
        },        
        {
            title: t("column.actions"),
            key: "actions",
            width: "5vw",
            render: (_, record: SourceResult) => (
                <Space size="middle">
                    <Button title={t("action.reindex", {ns: "source"})} type="primary" icon={<ReloadOutlined/>} size="small"
                            onClick={() => openReindexModal(record)}
                            disabled={!sourceCanBeReindexed(record)}/>

                    <Button title={t("action.delete")} type="primary" icon={<DeleteOutlined/>} size="small" danger
                            onClick={() => openDeleteModal(record)}
                            disabled={!sourceCanBeDeleted(record)}/>
                </Space>
            ),
        },
    ];

    useEffect(() => {
        console.log("page.Source, mount");
        loadList();

        return () => {
            console.log("page.Source, unmount");

            if (loadTimeout !== null) {
                clearTimeout(loadTimeout);
                setLoadTimeout(null);
            }
        }
    }, [tableParams]);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12} offset={12} style={{textAlign: "right"}}>
                        <Button type="primary" onClick={openDrawer}>
                            <PlusOutlined/>
                            {t("action.add", {ns: "source"})}
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
            <Drawer title={editId ? t("action.update", {ns: "source"}) : t("action.add", {ns: "source"})} placement="right" onClose={closeDrawer} open={drawerOpen} width={"30vw"}>
                <Form
                    form={form}
                    labelCol={{span: 8}}
                    wrapperCol={{span: 16}}
                    style={{maxWidth: 600}}
                    initialValues={{remember: true}}
                    onFinish={editId ? updateSource : createSource}
                    autoComplete="off"
                >
                    <Form.Item
                        label={t("column.type")}
                        name="type">
                        <Select defaultValue="UPLOAD" onChange={handleTypeChange}>
                            {Object.keys(sourceTypes).map(key =>
                                <Select.Option key={key} value={key}>{sourceTypes[key]}</Select.Option>
                            )}
                        </Select>
                    </Form.Item>

                    {formType === "UPLOAD" && 
                        <Form.Item
                            label={t("column.file", {ns: "source"})}
                            name="file">
                            <Upload {...fileUploadProperties}>
                                <Button icon={<UploadOutlined/>}>Click to Upload</Button>
                            </Upload>
                        </Form.Item>
                    }

                    {(formType === "CONFLUENCE" || formType === "JIRA") &&
                        <>
                            <Form.Item
                                label={t("column.url")}
                                name="url"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Input/>
                            </Form.Item>

                            <Form.Item
                                name="is_cloud"
                                valuePropName="checked"
                                wrapperCol={{ offset: 8, span: 16 }}>
                                <Checkbox>
                                    {t("description.cloud", {ns: "source"})}
                                </Checkbox>                                
                            </Form.Item>

                            <Form.Item
                                label={t("column.username")}
                                name="username"
                                rules={[{required: true, message:t("message.error.mandatory")}]}>
                                <Input/>
                            </Form.Item>

                            <Form.Item
                                label={t("column.password")}
                                name="password"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Password/>
                            </Form.Item>
                        </>
                    }

                    {formType === "CONFLUENCE" &&
                        <Form.Item
                            label={t("column.spaceKey", {ns: "source"})}
                            name="space_key"
                            rules={[{required: true, message: t("message.error.mandatory")}]}>
                            <Input/>
                        </Form.Item>
                    }

                    {formType === "JIRA" &&
                        <Form.Item
                            label={t("column.jql", {ns: "source"})}
                            name="search_query"
                            extra={t("description.jql", {ns: "source"})}
                            rules={[{required: true, message: t("message.error.mandatory")}]}>
                            <Input/>                            
                        </Form.Item>
                    }

                    <Form.Item
                        label={t("column.title")}
                        name="title"
                        rules={[{required: true, message: t("message.error.mandatory")}]}
                    >
                        <Input/>
                    </Form.Item>

                    <Form.Item
                        label={t("column.description")}
                        name="description"
                    >
                        <Input.TextArea rows={4}/>
                    </Form.Item>

                    <Form.Item wrapperCol={{offset: 8, span: 16}}>
                        <Button type="primary" htmlType="submit" disabled={saving}>
                            <SaveOutlined/>
                            {editId ? t("action.update", {ns: "source"}) : t("action.add", {ns: "source"})}
                        </Button>
                    </Form.Item>
                </Form>
            </Drawer>
        </div>
    );
};
