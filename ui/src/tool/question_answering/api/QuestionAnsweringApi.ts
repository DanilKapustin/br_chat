import {Component} from "react";
import {MessageCreatePayload, MessageResult} from "@/api/message";
import axios, {AxiosResponse} from "axios";

export class QuestionAnsweringApi extends Component<{}, {}> {
    getBaseUrl(sessionId: string): string {
        return `${window?._env_?.API_URL}/session/${sessionId}/tool/question_answering`;
    }

    async getMessages(sessionId: string, offset: number, limit: number): Promise<MessageResult[]> {
        console.debug("getMessages, sessionId=%s, offset=%s, limit=%s", sessionId, offset, limit);

        const response: AxiosResponse = await axios.get(
            `${this.getBaseUrl(sessionId)}?offset=${offset}&limit=${limit}`);

        return response.data as MessageResult[];
    }

    async createMessage(sessionId: string, form: MessageCreatePayload): Promise<MessageResult> {
        console.debug("create, sessionId=%s, form=%s", sessionId, form);

        const response: AxiosResponse = await axios.post<MessageCreatePayload>(this.getBaseUrl(sessionId), form);

        return response.data as MessageResult;
    }

    async rate(sessionId: string, messageId: string, rating: number): Promise<MessageResult> {
        console.debug("rate, sessionId=%s, messageId=%s, rating=%s", sessionId, messageId, rating);

        const response: AxiosResponse = await axios.post(
            `${this.getBaseUrl(sessionId)}/message/${messageId}/rate`, {rating: rating});

        return response.data as MessageResult;
    }

    async regenerate(sessionId: string, messageId: string): Promise<void> {
        console.debug("regenerate, sessionId=%s, messageId=%s", sessionId, messageId);
        await axios.post(`${this.getBaseUrl(sessionId)}/message/${messageId}/regenerate`);
    }

    createWebsocket(sessionId: string): WebSocket {
        console.debug("createWebsocket, sessionId=%s", sessionId);
        const websocketUrl = this.getBaseUrl(sessionId)
            .replace(/^http/, "ws") || "";
        return new WebSocket(`${websocketUrl}/ws`);
    }

    closeWebsocket(socket: WebSocket) {
        console.debug("closeWebsocket, socket=%s", socket);

        socket.onopen = null;
        socket.onmessage = null;
        socket.onerror = null;

        socket.close();
    }
}
