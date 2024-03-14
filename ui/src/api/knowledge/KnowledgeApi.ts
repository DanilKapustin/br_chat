import {Component} from "react";
import {KnowledgeResultPage} from "./data";
import axios, {AxiosResponse} from "axios";

export class KnowledgeApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/knowledge`;
    }

    public async getList(page: number | undefined = 1, size: number | undefined = 10): Promise<KnowledgeResultPage> {
        console.debug("getList, page=%s, size=%s", page, size);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}?page=${page}&size=${size}`);

        return response.data as KnowledgeResultPage;
    }

    public async delete(id: string): Promise<void> {
        console.debug("delete, id=%s", id);
        await axios.delete(`${this.getBaseUrl()}/${id}`);
    }

    public async deleteAll(): Promise<void> {
        console.debug("deleteAll");
        await axios.delete(this.getBaseUrl());
    }
}
