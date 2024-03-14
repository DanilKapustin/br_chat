import {Component} from "react";
import {RcFile} from "antd/lib/upload";
import {
    ConfluenceConfiguration,
    JiraConfiguration,
    SourceConfiguration,
    SourceCreatePayload,
    SourceResult,
    SourceResultPage
} from "./data";
import axios, {AxiosResponse} from "axios";

export class SourceApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/source`;
    }

    public async getList(page: number | undefined = 1, size: number | undefined = 10): Promise<SourceResultPage> {
        console.debug("getList, page=%s, size=%s", page, size);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}?page=${page}&size=${size}`);

        return response.data as SourceResultPage;
    }

    public async create(form: SourceCreatePayload, file: RcFile | null = null): Promise<SourceResult> {
        console.debug("create, form=%o, file=%o", form, file);
        let configuration: SourceConfiguration = {};

        switch (form.type) {
            case "CONFLUENCE":
                configuration = new ConfluenceConfiguration(form);
                file = null;
                break;

            case "JIRA":
                configuration = new JiraConfiguration(form);
                file = null;
                break;
        }

        const response: AxiosResponse = await axios.post(this.getBaseUrl(), {
            title: form.title,
            description: form.description,
            type: form.type,
            configuration: configuration
        });

        const sourceResult: SourceResult = response.data as SourceResult;
        console.debug("create, sourceResult=%o", sourceResult);

        if (file == null) {
            return sourceResult;
        }

        console.debug("createSource, uploading file for source=%s", sourceResult.id);

        const uploadForm = new FormData();
        uploadForm.append("upload", file);

        const uploadResponse: AxiosResponse = await axios.post(
            `${this.getBaseUrl()}/${sourceResult.id}/upload`, uploadForm);

        return uploadResponse.data as SourceResult;
    }

    public async update(id: string, type: string, form: SourceCreatePayload): Promise<SourceResult> {
        console.debug("update, id=%s, type=%s, form=%s", id, type, form);
        let configuration: SourceConfiguration = {};

        switch (type) {
            case "CONFLUENCE":
                configuration = new ConfluenceConfiguration(form);
                break;

            case "JIRA":
                configuration = new JiraConfiguration(form);
                break;
        }

        const response: AxiosResponse = await axios.put(`${this.getBaseUrl()}/${id}`, {
            id: id,
            title: form.title,
            description: form.description,
            configuration: configuration
        });

        return response.data as SourceResult;
    }

    public async delete(id: string): Promise<void> {
        console.debug("delete, id=%s", id);
        await axios.delete(`${this.getBaseUrl()}/${id}`);
    }

    public async reindex(id: string): Promise<void> {
        console.debug("reindex, id=%s", id);
        await axios.post(`${this.getBaseUrl()}/${id}/reindex`);
    }
}
