/** Session completion screen */

interface SessionCompleteProps {
	onRestart?: () => void;
}

export function SessionComplete({ onRestart }: SessionCompleteProps) {
	return (
		<div className="glass-elevated rounded-2xl border border-border/40 p-12 text-center space-y-4">
			<div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto">
				<svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
					<path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
				</svg>
			</div>
			<h2 className="text-xl font-heading font-bold text-text-primary">
				Thank You!
			</h2>
			<p className="text-text-secondary max-w-sm mx-auto">
				Your responses have been submitted successfully. We appreciate your time.
			</p>
			{onRestart && (
				<button
					onClick={onRestart}
					className="px-5 py-2.5 rounded-xl glass border border-border text-text-secondary hover:text-text-primary hover:border-border-hover"
				>
					Start Again
				</button>
			)}
		</div>
	);
}
