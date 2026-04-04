import { type ReactNode, useEffect, useRef } from "react";

interface ModalProps {
	open: boolean;
	onClose: () => void;
	title?: string;
	children: ReactNode;
}

export function Modal({ open, onClose, title, children }: ModalProps) {
	const dialogRef = useRef<HTMLDialogElement>(null);

	useEffect(() => {
		const dialog = dialogRef.current;
		if (!dialog) return;
		if (open && !dialog.open) {
			dialog.showModal();
		} else if (!open && dialog.open) {
			dialog.close();
		}
	}, [open]);

	useEffect(() => {
		const dialog = dialogRef.current;
		if (!dialog) return;
		const handleClose = () => onClose();
		dialog.addEventListener("close", handleClose);
		return () => dialog.removeEventListener("close", handleClose);
	}, [onClose]);

	const handleBackdropClick = (e: React.MouseEvent) => {
		if (e.target === dialogRef.current) {
			onClose();
		}
	};

	return (
		<dialog
			ref={dialogRef}
			className="backdrop:bg-black/60 bg-transparent p-0 m-auto max-w-lg w-full"
			onClick={handleBackdropClick}
		>
			<div className="bg-bg-base rounded-xl border-[0.5px] border-stone-200 p-6 shadow-xl">
				{title && (
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-lg font-heading font-medium text-text-primary">
							{title}
						</h2>
						<button
							onClick={onClose}
							className="text-text-tertiary hover:text-text-primary text-xl leading-none transition-colors"
							aria-label="Close"
						>
							&times;
						</button>
					</div>
				)}
				{children}
			</div>
		</dialog>
	);
}
