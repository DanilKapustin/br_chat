import {Component} from "react";
import {
    ToolConfigurationFields,
    ToolCreatePayload,
    ToolPageResult,
    ToolPayload,
    ToolResult,
    ToolUpdatePayload
} from "./data";
import axios, {AxiosResponse} from "axios";

export class ToolApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/tool`;
    }

    public async getList(page: number | undefined = 1, size: number | undefined = 10): Promise<ToolPageResult> {
        console.debug("getList, page=%s, size=%s", page, size);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}?page=${page}&size=${size}`);

        return response.data as ToolPageResult;
    }

    public async getAll(): Promise<ToolResult[]> {
        console.debug("getAll");

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/all`);

        return response.data as ToolResult[];
    }

    public async get(id: string): Promise<ToolResult> {
        console.debug("get, id=%s", id);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/${id}`);


        return response.data as ToolResult;
    }

    public async getConfigurationFields(): Promise<ToolConfigurationFields[]> {
        console.debug("getConfigurationFields");

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/configuration-fields`);

        return response.data as ToolConfigurationFields[];
    }

    private prepareConfigurationPayload(payload: ToolPayload): ToolPayload {
        const configuration: any = {};

        Object.keys(payload).filter(key => key.startsWith("configuration__")).forEach(key => {
            configuration[key.replace("configuration__", "")] = payload[key];
            delete payload[key];
        });

        payload.configuration = configuration;

        return payload;
    }

    public async create(form: ToolCreatePayload): Promise<ToolResult> {
        console.debug("create, form=%o", form);

        const response: AxiosResponse = await axios.post<ToolCreatePayload>(
            this.getBaseUrl(), this.prepareConfigurationPayload(form));

        return response.data as ToolResult;
    }

    public async update(id: string, form: ToolUpdatePayload): Promise<ToolResult> {
        console.debug("update, id=%s, form=%o", id, form);
        form.id = id;

        const response: AxiosResponse = await axios.put<ToolUpdatePayload>(
            `${this.getBaseUrl()}/${id}`, this.prepareConfigurationPayload(form));

        return response.data as ToolResult;
    }

    public async duplicate(id: string): Promise<ToolResult> {
        console.debug("duplicate, id=%s", id);

        const response: AxiosResponse = await axios.post(`${this.getBaseUrl()}/${id}/duplicate`);

        return response.data as ToolResult;
    }

    public async delete(id: string): Promise<void> {
        console.debug("delete, id=%s", id);
        await axios.delete(`${this.getBaseUrl()}/${id}`);
    }
}
