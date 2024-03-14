import {Component} from "react";
import {SessionCreatePayload, SessionPageResult, SessionResult} from "./data";
import axios, {AxiosResponse} from "axios";

export class SessionApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/session`;
    }

    public async getList(page: number, size: number): Promise<SessionPageResult> {
        console.debug("getList, page=%s, size=%s", page, size);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}?page=${page}&size=${size}`);

        return response.data as SessionPageResult;
    }

    public async get(id: string): Promise<SessionResult> {
        console.debug("get, id=%s", id);

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/${id}`);

        return response.data as SessionResult;
    }

    public async create(form: SessionCreatePayload): Promise<SessionResult> {
        console.debug("create, form=%o", form);

        const response: AxiosResponse = await axios.post<SessionCreatePayload>(this.getBaseUrl(), form);

        return response.data as SessionResult;
    }

    public async delete(id: string): Promise<void> {
        console.debug("delete, id=%s", id);
        await axios.delete(`${this.getBaseUrl()}/${id}`);
    }
}
