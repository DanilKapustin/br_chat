import {FC, useEffect, useState} from "react";
import {App, Button, Col, Drawer, Form, Input, Row, Select, Space, Table, Tag, theme} from "antd";
import {
    ModelApi,
    ModelConfigurationFields,
    ModelCreatePayload,
    ModelFieldDefinition,
    ModelPageResult,
    ModelPayload,
    ModelResult,
    ModelUpdatePayload
} from "@/api/model";
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

export const Model: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();
    
    const {t} = useTranslation();
    const api = new ModelApi({});
    const {message, modal} = App.useApp();

    const [data, setData] = useState<ModelResult[]>([]);
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
    const [configurationFields, setConfigurationFields] = useState<ModelConfigurationFields[]>([]);

    const loadList = async () => {
        console.debug("loadList");
        setLoading(true);

        try {
            const response: ModelPageResult = await api.getList(tableParams.current, tableParams.pageSize);
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
            const response: ModelConfigurationFields[] = await api.getConfigurationFields();
            setConfigurationFields(response);
            setEditName(response[0].name);
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setLoading(false)
        }
    };

    const handleTableChange = (
        pagination: any,
        filters: Record<string, FilterValue | null>,
        sorter: SorterResult<ModelResult> | SorterResult<ModelResult>[],
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

    const openEditForm = (model: ModelResult) => {
        console.debug("openEditForm, model=%o", model);

        form.resetFields();
        const configurationFields: any = {};

        Object.keys(model.configuration).forEach((key: string) => {
            configurationFields["configuration__" + key] = model.configuration[key];
        });

        form.setFieldsValue({...model, ...configurationFields});
        setEditId(model.id);
        setEditName(model.name);

        openDrawer();
    };

    const openDeleteModal = (model: ModelResult) => {
        console.debug("openDeleteModal, model=%o", model);

        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <ExclamationCircleOutlined/>,
            content: t("description.delete", {ns: "model", title: model.title}),
            onOk() {
                console.debug("openDeleteModal, onOk");

                const asyncDelete = async () => {
                    await api.delete(model.id);
                    await loadList();
                };

                asyncDelete().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const openDuplicateModal = (model: ModelResult) => {
        console.debug("openDuplicateModal, model=%o", model);

        modal.confirm({
            title: t("confirmation.title", {ns: "dialog"}),
            icon: <InfoCircleOutlined/>,
            content: t("description.duplicate", {ns: "model", title: model.title}),
            onOk() {
                console.debug("openDuplicateModal, onOk");

                const asyncDuplicate = async () => {
                    await api.duplicate(model.id);
                    await loadList();
                };

                asyncDuplicate().catch(() => {
                    message.error(t("message.error.server"));
                });
            }
        });
    }

    const createModel = async (form: ModelPayload) => {
        console.debug("createModel, form=%o", form);

        setSaving(true);

        try {
            await api.create(form as ModelCreatePayload);
            message.success(t("message.success.created", {ns: "model"}));

            closeDrawer();
            await loadList();
        } catch (error: any) {
            message.error(t("message.error.server"));
        } finally {
            setSaving(false);
        }
    };

    const updateModel = async (form: ModelPayload) => {
        console.debug("updateModel, form=%o", form);

        setSaving(true);

        try {
            await api.update(editId, form as ModelUpdatePayload);
            message.success(t("message.success.updated", {ns: "model"}));

            closeDrawer();
            await loadList();
        } catch (error: any) {
            message.error(t("message.error.server"))
        } finally {
            setSaving(false);
        }
    };

    const canBeDeleted = (model: ModelResult): boolean => {
        return !model.is_system;
    };

    const getConfigurationFields = (name: string): [string, ModelFieldDefinition][] => {
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
            initialValues.push(["name", name]);
        }

        return Object.fromEntries(initialValues);
    };

    const getDynamicFieldLabel = (field: string): string => {
        return t("column." + field, {ns: "model"});
    };

    const columns: ColumnsType<ModelResult> = [
        {
            title: t("column.title"),
            dataIndex: "title",
            key: "title",
            width: "20vw",
            render: (text, record: ModelResult) => (
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
                    {name}
                </Tag>
            ),
        },
        {
            title: t("column.system", {ns: "model"}),
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
            title: "#",
            width: "5vw",
            align: "right",
            render: (_, record: ModelResult) => (
                <>
                    {record.configuration.context_length}
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
            render: (_, record: ModelResult) => (
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
        console.log("page.Model, mount");

        const init = async () => {
            await loadList();
            await loadConfigurationFields();
        };

        init().catch(console.error);

        return () => {
            console.log("page.Model, unmount");
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
                                {t("action.add", {ns: "model"})}
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
                title={editId ? t("action.update", {ns: "model"}) : t("action.add", {ns: "model"})}
                placement="right"
                onClose={closeDrawer}
                open={drawerOpen}
                width={"30vw"}>
                <Form
                    form={form}
                    labelCol={{span: 8}}
                    wrapperCol={{span: 16}}
                    style={{maxWidth: 600}}
                    onFinish={editId ? updateModel : createModel}
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
                                        value={configuration.name}>{configuration.name}</Select.Option>
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

                    {getConfigurationFields(editName)
                        .map(([field]) => {
                            return <Form.Item
                                key={field}
                                label={getDynamicFieldLabel(field)}
                                name={"configuration__" + field}>
                                {
                                    ((field.startsWith("prompt_") || field.endsWith("_prompt")) && <Input.TextArea rows={8}/>) ||
                                    (field.includes("api_key") && <Input.Password/>) ||
                                    <Input/>
                                }
                            </Form.Item>;
                        }
                    )}

                    <Form.Item wrapperCol={{offset: 8, span: 16}}>
                        <Button type="primary" htmlType="submit" disabled={saving}>
                            <SaveOutlined/>
                            {editId ? t("action.update", {ns: "model"}) : t("action.add", {ns: "model"})}
                        </Button>
                    </Form.Item>
                </Form>
            </Drawer>
        </div>
    );
};
