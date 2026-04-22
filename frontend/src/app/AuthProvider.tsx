import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
	type ReactNode,
} from "react";
import type { AdminUser } from "../shared/types/api";
import {
	adminApi,
	clearAdminToken,
	getAdminToken,
	setAdminToken,
} from "../shared/lib/httpClient";

interface AuthContextValue {
	admin: AdminUser | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	login: (email: string, password: string) => Promise<void>;
	signup: (
		email: string,
		password: string,
		fullName: string,
		orgName: string,
	) => Promise<void>;
	logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
	const [admin, setAdmin] = useState<AdminUser | null>(null);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const token = getAdminToken();
		if (!token) {
			setIsLoading(false);
			return;
		}

		adminApi
			.get<AdminUser>("/auth/me")
			.then((user) => setAdmin(user))
			.catch(() => clearAdminToken())
			.finally(() => setIsLoading(false));
	}, []);

	const login = useCallback(async (email: string, password: string) => {
		const response = await adminApi.post<{ access_token: string }>(
			"/auth/login",
			{ email, password },
		);
		setAdminToken(response.access_token);

		const user = await adminApi.get<AdminUser>("/auth/me");
		setAdmin(user);
	}, []);

	const signup = useCallback(
		async (
			email: string,
			password: string,
			fullName: string,
			orgName: string,
		) => {
			const response = await adminApi.post<{ access_token: string }>(
				"/auth/register",
				{
					email,
					password,
					full_name: fullName,
					org_name: orgName,
				},
			);
			setAdminToken(response.access_token);

			const user = await adminApi.get<AdminUser>("/auth/me");
			setAdmin(user);
		},
		[],
	);

	const logout = useCallback(() => {
		clearAdminToken();
		setAdmin(null);
	}, []);

	const value = useMemo<AuthContextValue>(
		() => ({
			admin,
			isAuthenticated: admin !== null,
			isLoading,
			login,
			signup,
			logout,
		}),
		[admin, isLoading, login, signup, logout],
	);

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
	const ctx = useContext(AuthContext);
	if (!ctx) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return ctx;
}
