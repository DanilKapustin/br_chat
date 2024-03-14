export interface UserPayload {
    email: string;
    password: string;
}

export interface UserResult {
    email: string;
}

export interface TokenResult {
    access_token: string;
    token_type: string;
}
