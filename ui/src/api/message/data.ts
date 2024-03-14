export interface MessageSource {
    id: string
    source_id: string
    source_title: string
    title: string
    subtitle: string
    url: string
    chunk: number
    total_chunks: number
}

export interface MessageResult {
    id: string
    session_id: string
    is_error: boolean
    is_system: boolean
    message: string
    created_at: string
    created_by: string
    sources: MessageSource[]
    rating: number
}

export interface MessageCreatePayload {
    message: string
}
