import {FC, useEffect, useState} from "react";
import {App, Button, Col, Drawer, Form, Input, Row, Select, Space, Table, Tag, theme} from "antd";
import {ColumnsType} from "antd/es/table";
import {FilterValue, SorterResult} from "antd/es/table/interface";
import {
    CheckOutlined,
    CopyOutlined,
    DeleteOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    MinusOutlined,
    PlusOutlined,
    SaveOutlined
} from "@ant-design/icons";
import {useTranslation} from "react-i18next";
import {
    ToolApi,
    ToolConfigurationFields,
    ToolCreatePayload,
    ToolFieldDefinition,
    ToolPageResult,
    ToolPayload,
    ToolResult,
    ToolUpdatePayload
} from "@/api/tool";
import {ModelApi, ModelResult} from "@/api/model";

export const Tool: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();
    
    const {t} = useTranslation();
    const api = new ToolApi({});
    const modelApi = new ModelApi({});
    const {message, modal} = App.useApp();

    const [data, setData] = useState<ToolResult[]>([]);
    const [tableParams, setTableParams] = useState({
        current: 1,
        pageSize: 10,
        total: 0
    });
    const [loading, setLoading] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [saving, setSaving] = useState(false);
    const [editId, setEditId]= useState("");
    const [editName, setEditName] = useState<string>("");
    const [form] = Form.useForm();
    const [configurationFields, setConfigurationFields] = useState<ToolConfigurationFields[]>([]);
    const [models, setModels] = useState<ModelResult[]>([]);

    const loadList = async () => {
        console.debug("loadList");
        setLoading(true);

        try {
            const response: ToolPageResult = await api.getList(tableParams.current, tableParams.pageSize);
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

    const loadConfigurationFields = async () => {
        console.debug("loadConfigurationFields");
        setLoading(true);

        try {
            const response: ToolConfigurationFields[] = await api.getConfigurationFields();
            setConfigurationFields(response);
            setEditName(response[0].name);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false)
        }
    };

    const loadModels = async () => {
        console.debug("loadModels");
        setLoading(true);

        try {
            const response: ModelResult[] = await modelApi.getAll();
            setModels(response);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false)
        }
    };

    const handleTableChange = (
        pagination: any,
        filters: Record<string, FilterValue | null>,
        sorter: SorterResult<ToolResult> | SorterResult<ToolResult>[],
    ) => {
        console.debug("handleTableChange, page=%s, size=%s", pagination.current, pagination.pageSize);
        setTableParams({...tableParams, current: pagination.current, pageSize: pagination.pageSize});
    };

    const handleNameChange = (name: string) => {
        console.debug("handleNameChange, name=%s", name);
        setEditName(name);
        form.setFieldsValue(getDefaultConfigurationValues(name));
    };

    const openDrawer = () => {
        console.debug("openDrawer");
        setDrawerOpen(true);
    };

    const closeDrawer = () => {
        console.debug("closeDrawer");
        form.resetFields();

        setEditId("");
        setEditName("");

        setDrawerOpen(false);
    };

    const openCreateForm = () => {
        console.debug("openCreateForm");
        form.resetFields();

        setEditName(configurationFields[0].name);
        form.setFieldsValue(getDefaultConfigurationValues(configurationFields[0].name));

        openDrawer();
    };

    const openEditForm = (tool: ToolResult) => {
        console.debug("openEditForm, tool=%o", tool);

        form.resetFields();
        const configurationFields: any = {};

        Object.keys(tool.configuration).forEach((key: string) => {
            configurationFields["configuration__" + key] = tool.configuration[key];
        });

        form.setFieldsValue({...tool, ...configurationFields});
        setEditId(tool.id);
        setEditName(tool.name);

        openDrawer();
    };

    const openDeleteModal = (tool: ToolResult) => {
        console.debug("openDeleteModal, tool=%o", tool);

        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.delete", {ns: "tool", title: tool.title}),
            onOk() {
                console.debug("openDeleteModal, onOk");

                const asyncDelete = async () => {
                    await api.delete(tool.id);
                    await loadList();
                };

                asyncDelete().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const openDuplicateModal = (tool: ToolResult) => {
        console.debug("openDuplicateModal, tool=%o", tool);

        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <InfoCircleOutlined/>,
            content: t("description.duplicate", {ns: "tool", title: tool.title}),
            onOk() {
                console.debug("openDuplicateModal, onOk");

                const asyncDuplicate = async () => {
                    await api.duplicate(tool.id);
                    await loadList();
                };

                asyncDuplicate().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const createTool = async (form: ToolPayload) => {
        console.debug("createTool, form=%o", form);

        setSaving(true);

        try {
            await api.create(form as ToolCreatePayload);
            message.success(t("message.success.created", {ns: "tool"}));

            closeDrawer();
            await loadList();
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setSaving(false);
        }
    };

    const updateTool = async (form: ToolPayload) => {
        console.debug("updateTool, form=%o", form);

        setSaving(true);

        try {
            await api.update(editId, form as ToolUpdatePayload);
            message.success(t("message.success.updated", {ns: "tool"}));

            closeDrawer();
            await loadList();
        } catch (error: any) {
            message.error(t("message.error.server"))
        } finally {
            setSaving(false);
        }
    };

    const canBeDeleted = (tool: ToolResult): boolean => {
        return !tool.is_system;
    };

    const getConfigurationFields = (name: string): [string, ToolFieldDefinition][] => {
        return Object.entries(
            configurationFields.find(item => item.name === name)?.fields.properties || {}
        );
    };

    const getDefaultConfigurationValues = (name: string): any => {
        const initialValues: [string, any][] = getConfigurationFields(name)
            .map(([field, definition]) => [
                "configuration__" + field,
                definition.default
            ]) || [];

        if (configurationFields.length > 0) {
            initialValues.push(["name", configurationFields[0].name]);
        }

        return Object.fromEntries(initialValues);
    };

    const getDynamicFieldLabel = (field: string): string => {
        return t("column." + field, {ns: editName});
    };

    const columns: ColumnsType<ToolResult> = [
        {
            title: t("column.title"),
            dataIndex: "title",
            key: "title",
            render: (text, record: ToolResult) => (
                <>
                    <a onClick={() => openEditForm(record)}>{text}</a>
                </>
            ),
        },
        {
            title: t("column.name"),
            dataIndex: "name",
            key: "name",
            width: "10vw",
            render: (name: string) => (
                <Tag key={name}>
                    {t("tool." + name, {ns: "tool"})}
                </Tag>
            ),
        },
        {
            title: t("column.system", {ns: "tool"}),
            dataIndex: "is_system",
            key: "is_system",
            width: "10vw",
            render: (is_system) => (
                <>
                    {(is_system && <CheckOutlined/>) || <MinusOutlined/>}
                </>
            ),
        },
        {
            title: t("column.description"),
            dataIndex: "description",
            key: "description",
        },
        {
            title: t("column.actions"),
            key: "actions",
            width: "5vw",
            render: (_, record: ToolResult) => (
                <Space size="middle">
                    <Button
                        title={t("action.duplicate")}
                        type="default"
                        icon={<CopyOutlined/>}
                        size="small"
                        onClick={() => openDuplicateModal(record)}/>

                    <Button
                        title={t("action.delete")}
                        type="primary"
                        icon={<DeleteOutlined/>}
                        size="small"
                        danger
                        onClick={() => openDeleteModal(record)}
                        disabled={!canBeDeleted(record)}/>
                </Space>
            ),
        },
    ];

    useEffect(() => {
        console.log("page.Tool, mount");

        const init = async () => {
            await loadList();
            await loadConfigurationFields();
            await loadModels();
        };

        init().catch(console.error);

        return () => {
            console.log("page.Tool, unmount");
        }
    }, [tableParams]);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12} offset={12} style={{textAlign: "right"}}>
                        <Space direction="horizontal">
                            <Button type="primary" onClick={openCreateForm}>
                                <PlusOutlined/>
                                {t("action.add", {ns: "tool"})}
                            </Button>
                        </Space>
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
            <Drawer
                title={editId ? t("action.update", {ns: "tool"}) : t("action.add", {ns: "tool"})}
                placement="right"
                onClose={closeDrawer}
                open={drawerOpen}
                width={"50vw"}>
                <Form
                    form={form}
                    labelCol={{span: 8}}
                    wrapperCol={{span: 16}}
                    onFinish={editId ? updateTool : createTool}
                    initialValues={getDefaultConfigurationValues(editName)}
                    autoComplete="off">
                    <Form.Item
                        label={t("column.name")}
                        name="name">
                        {configurationFields.length > 0 &&
                            <Select
                                onChange={handleNameChange}
                                disabled={!!editId}>
                                {configurationFields.map(configuration =>
                                    <Select.Option
                                        key={configuration.name}
                                        value={configuration.name}>
                                        {t("tool." + configuration.name, {ns: "tool"})}
                                    </Select.Option>
                                )}
                            </Select>
                        }
                    </Form.Item>

                    <Form.Item
                        label={t("column.title")}
                        name="title">
                        <Input/>
                    </Form.Item>

                    <Form.Item
                        label={t("column.description")}
                        name="description">
                        <Input.TextArea rows={4}/>
                    </Form.Item>

                    <Form.Item
                        label={t("column.model", {ns: "tool"})}
                        name="model_id">
                        {models.length > 0 &&
                            <Select>
                                {models.map(model =>
                                    <Select.Option
                                        key={model.title}
                                        value={model.id}>{model.title}</Select.Option>
                                )}
                            </Select>
                        }
                    </Form.Item>

                    {getConfigurationFields(editName)
                        .map(([field]) => {
                            return <Form.Item
                                key={field}
                                label={getDynamicFieldLabel(field)}
                                name={"configuration__" + field}>
                                {(field.startsWith("prompt_") && <Input.TextArea rows={8}/>) || <Input/>}
                            </Form.Item>;
                        }
                    )}

                    <Form.Item wrapperCol={{offset: 8, span: 16}}>
                        <Button type="primary" htmlType="submit" disabled={saving}>
                            <SaveOutlined/>
                            {editId ? t("action.update", {ns: "tool"}) : t("action.add", {ns: "tool"})}
                        </Button>
                    </Form.Item>
                </Form>
            </Drawer>
        </div>
    );
};
