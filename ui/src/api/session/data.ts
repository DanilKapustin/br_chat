import { ReactNode } from "react";
import {PageResult} from "../PageResult";

export interface SessionPageResult extends PageResult {
    items: SessionResult[]
}

export interface SessionCreatePayload {
    title: string
    tool_id: string
}

export interface SessionResult {
    id: any
    title: string
    tool_id: string
    created_at: string
    updated_at: string
}
