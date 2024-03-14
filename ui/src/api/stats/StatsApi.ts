import {Component} from "react";
import {StatsResult} from "./data";
import axios, {AxiosResponse} from "axios";

export class StatsApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/stats`;
    }

    public async get(): Promise<StatsResult> {
        console.debug("get");

        const response: AxiosResponse = await axios.get(this.getBaseUrl());

        return response.data as StatsResult;
    }
}
