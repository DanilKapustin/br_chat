import {FC, useEffect, useState} from "react";
import {App, Card, Col, Row, Space, Statistic} from 'antd';
import {MessageOutlined, LikeOutlined, DislikeOutlined, ReloadOutlined, CheckOutlined, UserOutlined} from "@ant-design/icons";
import {useTranslation} from "react-i18next";
import {StatsApi, StatsResult} from "@/api/stats";


export const Dashboard: FC = () => {
    const {t} = useTranslation();

    const api: StatsApi = new StatsApi({});
    const {message} = App.useApp();
    const [stats, setStats] = useState<StatsResult | null>(null);
    const [loading, setLoading] = useState(false);

    const loadStats = () => {
        console.debug("loadStats");
        setLoading(true);

        api.get()
            .then((response: StatsResult) => {
                setStats(response);
            })
            .catch((error: any) => message.error(t("message.error.server")))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        console.log("page.Dashboard, mount");
        loadStats();

        return () => {
            console.log("page.Dashboard, unmount");
        }
    }, []);

    return (
        <div>
            <Row gutter={[16, 16]}>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.sessions", {ns: "dashboard"})}
                            value={stats?.sessions.total || 0}
                            prefix={<UserOutlined/>}/>
                    </Card>
                </Col>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.messages", {ns: "dashboard"})}
                            value={stats?.messages.total || 0}
                            prefix={<MessageOutlined/>}/>
                    </Card>
                </Col>
            </Row>
            <Row gutter={[16, 16]} style={{marginTop: 16}}>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.ratings", {ns: "dashboard"})}
                            value={stats?.messages.ratings || 0}
                            prefix={<CheckOutlined/>}/>
                    </Card>
                </Col>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.ratings", {ns: "dashboard"})}
                            value={(stats?.messages.ratings || 0) / (stats?.messages.total ? stats?.messages.total : 1) * 100}
                            precision={2}
                            suffix="%"
                            prefix={<CheckOutlined/>}/>
                    </Card>
                </Col>
            </Row>
            <Row gutter={[16, 16]} style={{marginTop: 16}}>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.likes", {ns: "dashboard"})}
                            value={stats?.messages.likes || 0}
                            prefix={<LikeOutlined/>}/>
                    </Card>
                </Col>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.likes", {ns: "dashboard"})}
                            value={(stats?.messages.likes || 0) / (stats?.messages.total ? stats?.messages.total : 1) * 100}
                            precision={2}
                            suffix="%"
                            prefix={<LikeOutlined/>}/>
                    </Card>
                </Col>
            </Row>
            <Row gutter={[16, 16]} style={{marginTop: 16}}>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.dislikes", {ns: "dashboard"})}
                            value={stats?.messages.dislikes}
                            prefix={<DislikeOutlined/>}/>
                    </Card>
                </Col>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.dislikes", {ns: "dashboard"})}
                            value={(stats?.messages.dislikes || 0) / (stats?.messages.total ? stats?.messages.total : 1) * 100}
                            precision={2}
                            suffix="%"
                            prefix={<DislikeOutlined/>}/>
                    </Card>
                </Col>
            </Row>
            <Row gutter={[16, 16]} style={{marginTop: 16}}>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.regenerations", {ns: "dashboard"})}
                            value={stats?.messages.regenerations}
                            prefix={<ReloadOutlined/>}/>
                    </Card>
                </Col>
                <Col span={4}>
                    <Card
                        bordered={true}
                        loading={loading}>
                        <Statistic
                            title={t("column.regenerations", {ns: "dashboard"})}
                            value={(stats?.messages.regenerations || 0) / (stats?.messages.total ? stats?.messages.total : 1) * 100}
                            precision={2}
                            suffix="%"
                            prefix={<ReloadOutlined/>}/>
                    </Card>
                </Col>
            </Row>
        </div>);
};
