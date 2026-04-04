import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./AuthProvider";

const HomePage = lazy(() => import("../features/admin/pages/HomePage"));
const LoginPage = lazy(() => import("../features/admin/pages/LoginPage"));
const DashboardPage = lazy(() => import("../features/admin/pages/DashboardPage"));
const FormEditorPage = lazy(() => import("../features/admin/pages/FormEditorPage"));
const SubmissionsPage = lazy(() => import("../features/admin/pages/SubmissionsPage"));
const FormPage = lazy(() => import("../features/consumer/pages/FormPage"));
const LegacyVoicePage = lazy(() => import("../features/legacy-voice/pages/LegacyVoicePage"));

function PageLoader() {
	return (
		<div className="flex items-center justify-center min-h-screen" style={{ background: "var(--bg-page)" }}>
			<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
		</div>
	);
}

function AdminLayout() {
	return (
		<div className="min-h-screen relative z-10">
			<Suspense fallback={<PageLoader />}>
				<Outlet />
			</Suspense>
		</div>
	);
}

function ProtectedRoute() {
	const { isAuthenticated, isLoading } = useAuth();

	if (isLoading) {
		return <PageLoader />;
	}

	if (!isAuthenticated) {
		const redirect = encodeURIComponent(window.location.pathname);
		return <Navigate to={`/admin/login?redirect=${redirect}`} replace />;
	}

	return <Outlet />;
}

export function AppRouter() {
	return (
		<BrowserRouter>
			<Suspense fallback={<PageLoader />}>
				<Routes>
					<Route path="/" element={<HomePage />} />

					<Route path="/admin/login" element={<LoginPage />} />
					<Route element={<ProtectedRoute />}>
						<Route path="/admin" element={<AdminLayout />}>
							<Route index element={<DashboardPage />} />
							<Route path="forms/new" element={<FormEditorPage />} />
							<Route path="forms/:formId" element={<FormEditorPage />} />
							<Route path="forms/:formId/submissions" element={<SubmissionsPage />} />
						</Route>
					</Route>

					<Route path="/f/:slug" element={<FormPage />} />
					<Route path="/legacy/voice" element={<LegacyVoicePage />} />
					<Route path="*" element={<Navigate to="/" replace />} />
				</Routes>
			</Suspense>
		</BrowserRouter>
	);
}
