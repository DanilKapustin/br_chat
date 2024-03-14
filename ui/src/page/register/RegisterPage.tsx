import {FC} from "react";
import {UserPayload} from "@/api/auth";
import {useNavigate} from "react-router-dom";
import {App, Button, Card, Col, Form, Input, Row, theme} from 'antd';
import {useTranslation} from "react-i18next";
import {useAuth} from "@/app/auth";

export const RegisterPage: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();

    const {t} = useTranslation();
    const {message} = App.useApp();
    const {register} = useAuth();
    const navigate = useNavigate();

    const handleRegister = async (form: UserPayload): Promise<void> => {
        console.debug("handleRegister, form=%o", form);

        try {
            await register(form);
            message.success(t("message.success.registration", {ns: "login_registration"}));
            navigate("/login");
        } catch {
            message.error(t("message.error.server"));
        }
    };

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Row justify="space-around" align="middle">
                <Col span={6}>
                    <Card>
                        <h2>{t("title.registration", {ns: "login_registration"})}</h2>

                        <Form
                            name="registerForm"
                            initialValues={{remember: true}}
                            onFinish={handleRegister}>
                            <Form.Item
                                label={t("column.email")}
                                name="email"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Input type="email"/>
                            </Form.Item>
                            <Form.Item
                                label={t("column.password")}
                                name="password"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Input.Password/>
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" htmlType="submit">
                                    {t("action.register")}
                                </Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};
