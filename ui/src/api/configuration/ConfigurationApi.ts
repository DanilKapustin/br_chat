import {Component} from "react";
import {ConfigurationForm, Language} from "./data";
import axios, {AxiosResponse} from "axios";

export class ConfigurationApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/configuration`;
    }

    public async getLanguageList(): Promise<Language[]> {
        console.debug("getLanguageList");

        const response: AxiosResponse = await axios.get(`${this.getBaseUrl()}/language`);

        return response.data as Language[];
    };

    public async get(): Promise<any> {
        console.debug("get");

        const response: AxiosResponse = await axios.get(this.getBaseUrl());

        return response.data;
    };

    public async save(form: ConfigurationForm): Promise<any> {
        console.debug("save, form=%s", form);

        const response: AxiosResponse = await axios.put<ConfigurationForm>(this.getBaseUrl(), form);

        return response.data;
    };
}
