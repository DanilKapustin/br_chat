import axios, {AxiosResponse} from "axios";
import {TokenResult, UserPayload, UserResult} from "./data";
import {Component} from "react";

export class AuthApi extends Component<{}, {}> {
    private getBaseUrl(): string {
        return `${window?._env_?.API_URL}/auth`;
    }

    public async login(payload: UserPayload): Promise<TokenResult> {
        console.debug("login, payload=%o", payload);
        const response: AxiosResponse = await axios.post<UserPayload>(`${this.getBaseUrl()}/token`, payload);

        return response.data as TokenResult;
    }

    public async register(payload: UserPayload): Promise<UserResult> {
        console.debug("register, payload=%o", payload);

        const response: AxiosResponse = await axios.post<UserPayload>(
            `${this.getBaseUrl()}/register`,
            payload
        );

        return response.data as UserResult;
    }
}
