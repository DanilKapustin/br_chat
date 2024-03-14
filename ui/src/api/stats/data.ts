export interface SessionStatsResult {
    total: number;
}

export interface MessageStatsResult {
    total: number;
    likes: number;
    dislikes: number;
    regenerations: number;
    ratings: number;
}

export interface StatsResult {
    sessions: SessionStatsResult;
    messages: MessageStatsResult;
}
