import {ReactNode} from "react";
import {UserResult, UserPayload} from "@/api/auth";

export interface AuthContextType {
    token: string | null;
    email: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    register: (data: UserPayload) => Promise<void>;
}

export interface AuthProviderProps {
    children: ReactNode;
}
