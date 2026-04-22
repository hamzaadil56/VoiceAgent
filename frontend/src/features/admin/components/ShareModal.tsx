import { useState } from "react";

interface ShareModalProps {
	slug: string;
	onClose: () => void;
}

export function ShareModal({ slug, onClose }: ShareModalProps) {
	const [copied, setCopied] = useState<string | null>(null);

	const baseUrl = window.location.origin;
	const formUrl = `${baseUrl}/f/${slug}`;
	const embedCode = `<iframe src="${formUrl}?embed=true" width="100%" height="700" frameborder="0" style="border: none; border-radius: 12px;"></iframe>`;

	const copyToClipboard = (text: string, key: string) => {
		navigator.clipboard.writeText(text);
		setCopied(key);
		setTimeout(() => setCopied(null), 2000);
	};

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
			<div className="bg-bg-base rounded-xl border-[0.5px] border-stone-200 shadow-2xl w-full max-w-lg p-6 animate-fade-up">
				<div className="flex items-center justify-between mb-6">
					<h2 className="font-heading text-[20px] font-semibold text-text-primary">
						Share Form
					</h2>
					<button
						type="button"
						onClick={onClose}
						className="w-8 h-8 rounded-md hover:bg-stone-100 grid place-items-center text-text-tertiary hover:text-text-primary transition-colors"
					>
						<svg
							className="w-4 h-4"
							fill="none"
							viewBox="0 0 24 24"
							strokeWidth={2}
							stroke="currentColor"
						>
							<path
								strokeLinecap="round"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<div className="space-y-5">
					{/* Direct Link */}
					<div>
						<label className="block text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-2">
							Direct Link
						</label>
						<div className="flex gap-2">
							<input
								readOnly
								value={formUrl}
								className="flex-1 px-3 py-[9px] rounded-md text-[13px] font-mono text-text-primary border-[0.5px] border-stone-200 bg-stone-50 outline-none"
							/>
							<button
								type="button"
								onClick={() =>
									copyToClipboard(formUrl, "link")
								}
								className="px-4 py-[9px] rounded-md text-[13px] font-medium text-white bg-forest-500 hover:bg-forest-600 transition-all shadow-forest"
							>
								{copied === "link" ? "Copied!" : "Copy"}
							</button>
						</div>
					</div>

					{/* Embed Code */}
					<div>
						<label className="block text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-2">
							Embed Code
						</label>
						<div className="relative">
							<textarea
								readOnly
								value={embedCode}
								rows={3}
								className="w-full px-3 py-[9px] rounded-md text-[12px] font-mono text-text-secondary border-[0.5px] border-stone-200 bg-stone-50 outline-none resize-none"
							/>
							<button
								type="button"
								onClick={() =>
									copyToClipboard(embedCode, "embed")
								}
								className="absolute top-2 right-2 px-3 py-1 rounded text-[11px] font-medium bg-bg-base border-[0.5px] border-stone-200 text-text-secondary hover:text-text-primary"
							>
								{copied === "embed" ? "Copied!" : "Copy"}
							</button>
						</div>
					</div>

					{/* QR Code placeholder */}
					<div>
						<label className="block text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-2">
							QR Code
						</label>
						<div className="flex items-center gap-4">
							<div className="w-24 h-24 bg-stone-100 rounded-lg grid place-items-center border border-stone-200">
								{/* Client-side QR via CSS/SVG */}
								<svg
									viewBox="0 0 100 100"
									className="w-16 h-16"
								>
									<rect
										fill="#2d6a5a"
										x="10"
										y="10"
										width="20"
										height="20"
									/>
									<rect
										fill="#2d6a5a"
										x="70"
										y="10"
										width="20"
										height="20"
									/>
									<rect
										fill="#2d6a5a"
										x="10"
										y="70"
										width="20"
										height="20"
									/>
									<rect
										fill="#2d6a5a"
										x="40"
										y="40"
										width="20"
										height="20"
									/>
									<rect
										fill="#2d6a5a"
										x="40"
										y="10"
										width="10"
										height="10"
									/>
									<rect
										fill="#2d6a5a"
										x="10"
										y="40"
										width="10"
										height="10"
									/>
									<rect
										fill="#2d6a5a"
										x="70"
										y="70"
										width="20"
										height="20"
									/>
								</svg>
							</div>
							<p className="text-[12px] text-text-tertiary">
								Scan to open the form on mobile. Install a QR
								library for a production QR code.
							</p>
						</div>
					</div>

					{/* Social Share */}
					<div className="flex gap-2 pt-2">
						<a
							href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(formUrl)}&text=Fill out this form`}
							target="_blank"
							rel="noopener noreferrer"
							className="px-4 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
						>
							Share on X
						</a>
						<a
							href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(formUrl)}`}
							target="_blank"
							rel="noopener noreferrer"
							className="px-4 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
						>
							Share on LinkedIn
						</a>
					</div>
				</div>
			</div>
		</div>
	);
}
