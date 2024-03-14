import {Component} from "react";
import {
    ModelConfigurationFields,
    ModelCreatePayload,
    ModelPageResult,
    ModelPayload,
    ModelResult,
    ModelUpdatePayload
} from "./data";
import axios, {AxiosResponse} from "axios";

export class ModelApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/model`;
    }

    public async getList(page: number | undefined = 1, size: number | undefined = 10): Promise<ModelPageResult> {
        console.debug("getList, page=%s, size=%s", page, size);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}?page=${page}&size=${size}`);

        return response.data as ModelPageResult;
    }

    public async getAll(): Promise<ModelResult[]> {
        console.debug("getAll");

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/all`);

        return response.data as ModelResult[];
    }

    public async getConfigurationFields(): Promise<ModelConfigurationFields[]> {
        console.debug("getConfigurationFields");

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/configuration-fields`);

        return response.data as ModelConfigurationFields[];
    }

    private prepareConfigurationPayload(payload: ModelPayload): ModelPayload {
        const configuration: any = {};

        Object.keys(payload).filter(key => key.startsWith("configuration__")).forEach(key => {
            configuration[key.replace("configuration__", "")] = payload[key];
            delete payload[key];
        });

        payload.configuration = configuration;

        return payload;
    }

    public async create(form: ModelCreatePayload): Promise<ModelResult> {
        console.debug("create, form=%o", form);

        const response: AxiosResponse = await axios.post<ModelCreatePayload>(
            this.getBaseUrl(), this.prepareConfigurationPayload(form));

        return response.data as ModelResult;
    }

    public async update(id: string, form: ModelUpdatePayload): Promise<ModelResult> {
        console.debug("update, id=%s, form=%o", id, form);

        form.id = id;

        const response: AxiosResponse = await axios.put<ModelUpdatePayload>(
            `${this.getBaseUrl()}/${id}`, this.prepareConfigurationPayload(form));

        return response.data as ModelResult;
    }

    public async duplicate(id: string): Promise<ModelResult> {
        console.debug("duplicate, id=%s", id);

        const response: AxiosResponse = await axios.post(`${this.getBaseUrl()}/${id}/duplicate`);

        return response.data as ModelResult;
    }

    public async delete(id: string): Promise<void> {
        await axios.delete(`${this.getBaseUrl()}/${id}`);
    }
}
