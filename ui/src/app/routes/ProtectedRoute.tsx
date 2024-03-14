import {FC} from "react";
import {Outlet, Navigate} from "react-router-dom";
import {useAuth} from "@/app/auth";

const ProtectedRoute: FC = () => {
    const {token} = useAuth();

    if (!token) {
        console.debug("ProtectedRoute, user is not logged in");
        return <Navigate to={"/login"} replace />;
    }

    console.log("ProtectedRoute, user is logged in");

    return (<Outlet />);
};

export default ProtectedRoute;
