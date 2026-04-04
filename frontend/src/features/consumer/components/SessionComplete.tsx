interface SessionCompleteProps {
	onRestart?: () => void;
}

export function SessionComplete({ onRestart }: SessionCompleteProps) {
	return (
		<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-12 text-center space-y-5 animate-fade-up shadow-md">
			{/* Success icon — forest teal */}
			<div
				className="w-[72px] h-[72px] rounded-full grid place-items-center mx-auto text-white text-[32px] bg-forest-500 shadow-forest"
				style={{ animation: "success-burst 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both" }}
			>
				✓
			</div>
			<h2 className="font-heading font-semibold text-[22px] text-text-primary">
				Thank You!
			</h2>
			<p className="text-[15px] text-text-secondary max-w-sm mx-auto leading-relaxed">
				Your responses have been submitted successfully. We appreciate your time.
			</p>
			{onRestart && (
				<button
					onClick={onRestart}
					className="px-5 py-[9px] rounded-md font-medium text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
				>
					Start Again
				</button>
			)}
		</div>
	);
}
