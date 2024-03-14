import {MessageResult} from "@/api/message";

export interface MessageProps {
    message: MessageResult;
    isLast: boolean;
    onRate: (message: MessageResult, rating: number) => void;
    onRegenerate: (message: MessageResult) => void;
    loading: boolean;
}
