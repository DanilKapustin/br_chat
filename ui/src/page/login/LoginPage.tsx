import {FC} from "react";
import {UserPayload} from "@/api/auth";
import {Navigate, useNavigate} from "react-router-dom";
import {App, Button, Card, Col, Form, Input, Row, theme} from "antd";
import {useTranslation} from "react-i18next";
import {useAuth} from "@/app/auth";

export const LoginPage: FC = () => {
    const {
        token: {colorBgContainer, colorText},
    } = theme.useToken();
    const {login, token} = useAuth();

    const {t} = useTranslation();
    const {message} = App.useApp();
    const navigate= useNavigate();

    if (token) {
        return <Navigate to="/dashboard" replace/>;
    }

    const handleLogin = async (form: UserPayload): Promise<void> => {
        console.debug("handleLogin, form=%o", form);

        try {
            await login(form.email, form.password);
            message.success(t("message.success.login", {ns: "login_registration"}));
            navigate("/dashboard");
        } catch {
            message.error(t("message.error.server"));
        }
    };

    return (
        <div style={{padding: 24, height: "100%", background: colorBgContainer, color: colorText}}>
            <Row justify="space-around" align="middle">
                <Col span={10}>
                    <Card>
                        <h2>{t("title.login", {ns: "login_registration"})}</h2>

                        <Form
                            name="loginForm"
                            initialValues={{remember: true}}
                            onFinish={handleLogin}>
                            <Form.Item
                                label={t("column.email")}
                                name="email"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Input
                                    type="text"
                                    id="email"/>
                            </Form.Item>
                            <Form.Item
                                label={t("column.password")}
                                name="password"
                                rules={[{required: true, message: t("message.error.mandatory")}]}>
                                <Input
                                    type="password"
                                    id="password"/>
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" htmlType="submit">
                                    {t("action.login")}
                                </Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};
