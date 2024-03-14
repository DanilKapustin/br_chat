import {FC, createContext, useContext, useEffect, useState, Context} from 'react';
import {UserPayload, AuthApi, TokenResult} from "@/api/auth";
import {AuthContextType, AuthProviderProps} from "./data";

const AuthContext: Context<AuthContextType> = createContext<AuthContextType>(null!);

export const AuthProvider: FC<AuthProviderProps> = ({children}) => {
    const [token, setToken] = useState<string | null>(null);
    const [email, setEmail] = useState<string | null>(null);
    const api: AuthApi = new AuthApi({});

    useEffect(() => {
        console.debug("AuthProvider, useEffect");
        const token: string | null = localStorage.getItem("token");

        if (token !== null) {
            setToken(token);
            setEmail(getEmail(token));
        }
    }, []);

    const getEmail = (token: string): string | null => {
        const base64Url: string = token.split(".")[1];
        const base64: string = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload: string = decodeURIComponent(
            window
                .atob(base64)
                .split("")
                .map(function (c) {
                    return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
                })
                .join("")
        );

        return JSON.parse(jsonPayload)["sub"];
    };

    const login = async (email: string, password: string): Promise<void> => {
        console.debug("login, email=%s, password=%s", email, password);

        const tokenResult: TokenResult = await api.login({email, password});

        localStorage.setItem("token", tokenResult.access_token);
        setToken(tokenResult.access_token);
        setEmail(getEmail(tokenResult.access_token));
    };

    const register = async (data: UserPayload): Promise<void> => {
        console.debug("register, data=%o", data);
        await api.register(data);
    };

    const logout = (): void => {
        console.debug("logout");

        localStorage.removeItem("token");
        setToken(null);
        setEmail(null);
    };

    return (
        <AuthContext.Provider value={{token, email, login, logout, register}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
