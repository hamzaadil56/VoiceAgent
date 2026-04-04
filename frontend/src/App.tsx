import { AuthProvider } from "./app/AuthProvider";
import { QueryProvider } from "./app/QueryProvider";
import { AppRouter } from "./app/Router";
import { ErrorBoundary } from "./shared/ui/ErrorBoundary";

export default function App() {
	return (
		<ErrorBoundary>
			<QueryProvider>
				<AuthProvider>
					<AppRouter />
				</AuthProvider>
			</QueryProvider>
		</ErrorBoundary>
	);
}
