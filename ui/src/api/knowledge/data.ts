import {PageResult} from "@/api/PageResult";

export interface KnowledgeResultPage extends PageResult{
    items: KnowledgeResult[]
}

export interface KnowledgeResult {
    id: any,
    source_id: string
    source_title: string
    title: string
    subtitle: string
    url: string
    chunk: number
    total_chunks: number
    text: string
}
