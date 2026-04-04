import { Link } from "react-router-dom";

export default function HomePage() {
	return (
		<div className="min-h-screen flex items-center justify-center px-4 bg-bg-page">
			<div className="text-center space-y-8 animate-fade-up">
				<div>
					<div className="w-14 h-14 rounded-lg bg-forest-500 grid place-items-center mx-auto mb-6 text-white shadow-forest">
						<svg width="28" height="28" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
							<path d="M20 2H8a4 4 0 0 0-4 4v20l8-8h8a4 4 0 0 0 4-4V6a4 4 0 0 0-4-4z" />
						</svg>
					</div>
					<h1 className="font-heading font-semibold text-[48px] text-text-primary leading-[1.1] tracking-tight">
						AgentForms
					</h1>
					<p className="text-text-secondary text-[17px] mt-3 max-w-md mx-auto leading-relaxed">
						Admins craft intelligent form journeys. Consumers experience them through natural conversation.
					</p>
				</div>
				<div className="flex flex-wrap gap-3 justify-center">
					<Link
						to="/admin/login"
						className="px-6 py-[9px] rounded-md font-medium text-[14px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 shadow-forest"
					>
						Admin Login
					</Link>
					<Link
						to="/legacy/voice"
						className="px-6 py-[9px] rounded-md font-medium text-[14px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all duration-150"
					>
						Legacy Voice Agent
					</Link>
				</div>
			</div>
		</div>
	);
}
