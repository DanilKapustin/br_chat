import {FC, useEffect, useState} from "react";
import {App, Button, Col, Form, Row, Select, Space, theme} from "antd";
import {useTranslation} from "react-i18next";
import {ConfigurationApi, ConfigurationForm, Language} from "@/api/configuration";

export const Configuration: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();
    
    const {t} = useTranslation();
    const api = new ConfigurationApi({});
    const {message} = App.useApp();
    const [saving, setSaving] = useState(false);
    const [languages, setLanguages] = useState<Language[]>([]);
    const [form] = Form.useForm();

    const loadConfiguration = () => {
        console.debug("loadConfiguration");

        api.getLanguageList()
            .then((languages: Language[]) => {
                setLanguages(languages);

                api.get()
                    .then((response: any) => {
                        form.setFieldValue("language", response[0].value);
                    })
                    .catch((error: any) => message.error(t("message.error.server")));
            })
            .catch((error: any) => message.error(t("message.error.server")));        
    };

    const saveConfiguration = (form: ConfigurationForm) => {
        console.debug("saveConfiguration, form=%o", form);
        setSaving(true);

        api.save(form)
            .then(() => {
                message.success(t("message.success.saved", {ns: "configuration"}));
            })
            .catch((error: any) => message.error(t("message.error.server")))
            .finally(() => setSaving(false));
    };

    useEffect(() => {
        console.log("page.Configuration, mount");
        loadConfiguration();

        return () => {
            console.log("page.Configuration, unmount");
        }
    }, []);

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Space direction="vertical" size="middle" style={{display: "flex"}}>
                <Row>
                    <Col span={12}>
                        <Form
                            form={form}
                            labelCol={{span: 8}}
                            wrapperCol={{span: 16}}
                            style={{maxWidth: "100%"}}
                            initialValues={{remember: true}}
                            onFinish={saveConfiguration}
                            autoComplete="off">
                            <Form.Item
                                label={t("column.defaultLanguage", {ns: "configuration"})}
                                name="language">
                                <Select>
                                    {languages.map(language =>
                                        <Select.Option key={language.code} value={language.code}>{language.title}</Select.Option>
                                    )}
                                </Select>
                            </Form.Item>

                            <Form.Item wrapperCol={{offset: 8, span: 16}}>
                                <Button type="primary" htmlType="submit" loading={saving}>
                                    {t("action.save")}
                                </Button>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>                
            </Space>                
        </div>
    );
};
