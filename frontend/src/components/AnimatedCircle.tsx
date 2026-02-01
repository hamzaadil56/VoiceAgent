/**
 * AnimatedCircle — Premium visual feedback for AI voice assistant
 *
 * Communicates state through motion and color alone. Designed for production-grade
 * quality: organic, fluid, reactive — never rigid or mechanical.
 *
 * States: idle | listening | processing | speaking
 * Uses spring physics for natural, anxiety-reducing motion.
 */

import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect, useMemo } from "react";
import { AgentState } from "../hooks/useWebSocket";

// Spring config — tuned for organic feel, responsive without jitter
const SPRING_RESPONSIVE = { stiffness: 120, damping: 18 };

// Animation constants — documented for maintainability
const IDLE_SCALE_RANGE = 0.03; // 1.0 → 1.03 breathing amplitude
const LISTENING_SCALE_RESPONSE = 0.25; // Audio drives 0–0.25 additional scale
const PROCESSING_SCALE = 0.92; // Slightly reduced to signal "thinking"
const SPEAKING_RHYTHM_AMPLITUDE = 0.06; // Gentle talk pulse (when no TTS level)

export interface AnimatedCircleProps {
	state: AgentState;
	audioLevel?: number; // 0–1 normalized (mic for listening, TTS for speaking)
	size?: number;
	onClick?: () => void;
}

export default function AnimatedCircle({
	state,
	audioLevel = 0,
	size = 200,
	onClick,
}: AnimatedCircleProps) {
	// Smooth audio level to prevent jitter — critical for organic feel
	const audioSpring = useSpring(audioLevel, SPRING_RESPONSIVE);
	useEffect(() => {
		audioSpring.set(audioLevel);
	}, [audioLevel, audioSpring]);

	// Normalize state for animation (connected → idle, disconnected → dimmed idle)
	const animState = useMemo(() => {
		if (state === "connected") return "idle";
		if (state === "disconnected") return "disconnected";
		return state;
	}, [state]);

	// Main scale: driven by state + audio. Single spring for smooth transitions.
	// For speaking without TTS level, we use animate keyframes (handled in JSX).
	const targetScale = useMemo(() => {
		if (animState === "idle" || animState === "disconnected") return 1;
		if (animState === "listening") {
			return 1 + LISTENING_SCALE_RESPONSE * audioLevel;
		}
		if (animState === "processing") return PROCESSING_SCALE;
		if (animState === "speaking") {
			// When TTS level available, drive scale; else pulse via animate in JSX
			return audioLevel > 0
				? 1 + SPEAKING_RHYTHM_AMPLITUDE * 3 * audioLevel
				: 1;
		}
		return 1;
	}, [animState, audioLevel]);

	const mainScale = useSpring(targetScale, SPRING_RESPONSIVE);
	useEffect(() => {
		mainScale.set(targetScale);
	}, [targetScale, mainScale]);

	// Derived motion values — update automatically without re-renders
	const ringScale = useTransform(audioSpring, [0, 1], [1, 1.08]);
	const haloOpacity = useTransform(audioSpring, [0, 1], [0.4, 0.8]);

	// Gradient stops per state — cool/warm progression
	const gradientConfig = useMemo(
		() => ({
			idle: {
				from: "rgba(100, 149, 237, 0.4)",
				to: "rgba(147, 112, 219, 0.35)",
				glow: "rgba(100, 149, 237, 0.15)",
			},
			listening: {
				from: "rgba(0, 217, 255, 0.5)",
				to: "rgba(0, 255, 200, 0.4)",
				glow: "rgba(0, 217, 255, 0.35)",
			},
			processing: {
				from: "rgba(123, 97, 255, 0.45)",
				to: "rgba(75, 0, 130, 0.4)",
				glow: "rgba(123, 97, 255, 0.25)",
			},
			speaking: {
				from: "rgba(0, 255, 200, 0.45)",
				to: "rgba(34, 197, 94, 0.4)",
				glow: "rgba(0, 255, 136, 0.3)",
			},
			disconnected: {
				from: "rgba(100, 100, 120, 0.25)",
				to: "rgba(80, 80, 100, 0.2)",
				glow: "rgba(100, 100, 120, 0.08)",
			},
		}),
		[]
	);

	const config = gradientConfig[animState] ?? gradientConfig.idle;

	const isClickable = Boolean(onClick);
	const isDisabled = animState === "disconnected";

	return (
		<motion.div
			className="relative flex items-center justify-center select-none"
			onClick={isClickable && !isDisabled ? onClick : undefined}
			role={isClickable ? "button" : undefined}
			tabIndex={isClickable ? 0 : undefined}
			onKeyDown={
				isClickable
					? (e) => {
							if (e.key === "Enter" || e.key === " ") {
								e.preventDefault();
								onClick?.();
							}
					  }
					: undefined
			}
			style={{
				cursor: isClickable && !isDisabled ? "pointer" : "default",
			}}
			whileHover={
				isClickable && !isDisabled ? { scale: 1.02 } : undefined
			}
			whileTap={isClickable && !isDisabled ? { scale: 0.98 } : undefined}
		>
			{/* Outer glow halo — expands with listening/speaking */}
			{(animState === "listening" || animState === "speaking") && (
				<motion.div
					className="absolute rounded-full pointer-events-none"
					style={{
						width: size + 80,
						height: size + 80,
						background: `radial-gradient(circle, ${config.glow} 0%, transparent 70%)`,
						opacity: haloOpacity,
					}}
					animate={{
						scale: [1, 1.15, 1],
					}}
					transition={{
						duration: 2,
						repeat: Infinity,
						ease: "easeInOut",
					}}
				/>
			)}

			{/* Listening: converging rings — energy being consumed / absorbed */}
			{animState === "listening" && (
				<>
					{[0, 1, 2].map((i) => (
						<motion.div
							key={`listen-ring-${i}`}
							className="absolute rounded-full border pointer-events-none origin-center"
							style={{
								width: size + 60 + i * 40,
								height: size + 60 + i * 40,
								left: "50%",
								top: "50%",
								marginLeft: -(size + 60 + i * 40) / 2,
								marginTop: -(size + 60 + i * 40) / 2,
								borderColor: "rgba(0, 217, 255, 0.4)",
								opacity: 0,
							}}
							animate={{
								scale: [1, 0.3],
								opacity: [0.6, 0],
							}}
							transition={{
								duration: 1.2,
								repeat: Infinity,
								ease: "easeOut",
								delay: i * 0.35,
							}}
						/>
					))}
					{/* Inner vortex hint — radial streaks pulled toward center */}
					<motion.div
						className="absolute rounded-full pointer-events-none"
						style={{
							width: size + 40,
							height: size + 40,
							left: "50%",
							top: "50%",
							marginLeft: -(size + 40) / 2,
							marginTop: -(size + 40) / 2,
							background: `radial-gradient(circle at center, transparent 40%, rgba(0, 217, 255, 0.15) 70%, transparent 100%)`,
						}}
						animate={{
							opacity: [0.4, 0.9, 0.4],
							scale: [1, 1.05, 1],
						}}
						transition={{
							duration: 0.8,
							repeat: Infinity,
							ease: "easeInOut",
						}}
					/>
				</>
			)}

			{/* Speaking: sparkles — energetic burst outward */}
			{animState === "speaking" && (
				<>
					{Array.from({ length: 12 }).map((_, i) => {
						const angle = (i / 12) * Math.PI * 2 + Math.PI / 12;
						const radius = size * 0.5;
						const endX = Math.cos(angle) * radius * 0.7;
						const endY = Math.sin(angle) * radius * 0.7;
						return (
							<motion.div
								key={`sparkle-${i}`}
								className="absolute w-1.5 h-1.5 rounded-full pointer-events-none"
								style={{
									left: "50%",
									top: "50%",
									background: "rgba(255, 255, 255, 0.95)",
									boxShadow:
										"0 0 6px rgba(0, 255, 136, 0.9), 0 0 12px rgba(34, 197, 94, 0.6)",
								}}
								animate={{
									x: [0, endX * 0.5, endX],
									y: [0, endY * 0.5, endY],
									opacity: [0, 1, 0],
									scale: [0.3, 1.3, 0.2],
								}}
								transition={{
									duration: 1.4,
									repeat: Infinity,
									ease: "easeOut",
									delay: i * 0.07,
								}}
							/>
						);
					})}
					{/* Soft ember flicker overlay — warm inner glow */}
					<motion.div
						className="absolute rounded-full pointer-events-none"
						style={{
							width: size,
							height: size,
							left: "50%",
							top: "50%",
							marginLeft: -size / 2,
							marginTop: -size / 2,
							background: `radial-gradient(circle at 50% 50%, rgba(255, 255, 200, 0.1) 0%, transparent 55%)`,
							boxShadow: "inset 0 0 40px rgba(0, 255, 136, 0.12)",
						}}
						animate={{
							opacity: [0.6, 1, 0.6],
						}}
						transition={{
							duration: 0.5,
							repeat: Infinity,
							ease: "easeInOut",
						}}
					/>
				</>
			)}

			{/* Main circle — scale driven by state + audio */}
			<motion.div
				className="relative rounded-full overflow-hidden origin-center"
				style={{
					width: size,
					height: size,
					scale:
						animState === "idle" ||
						animState === "disconnected" ||
						(animState === "speaking" && audioLevel === 0)
							? undefined
							: mainScale,
					opacity: animState === "disconnected" ? 0.6 : 1,
				}}
				animate={
					animState === "idle" || animState === "disconnected"
						? {
								scale: [1, 1 + IDLE_SCALE_RANGE, 1],
						  }
						: animState === "speaking" && audioLevel === 0
						? {
								scale: [
									1,
									1 + SPEAKING_RHYTHM_AMPLITUDE * 2,
									1,
								],
						  }
						: undefined
				}
				transition={
					animState === "idle" || animState === "disconnected"
						? {
								duration: 2.5,
								repeat: Infinity,
								ease: "easeInOut",
						  }
						: animState === "speaking" && audioLevel === 0
						? {
								duration: 1.2,
								repeat: Infinity,
								ease: "easeInOut",
						  }
						: undefined
				}
			>
				{/* Base gradient background */}
				<motion.div
					className="absolute inset-0 rounded-full"
					style={{
						background: `radial-gradient(circle at 30% 30%, ${config.from}, ${config.to})`,
						boxShadow: `inset 0 0 60px rgba(255,255,255,0.08)`,
					}}
					animate={
						animState === "processing"
							? {
									background: [
										`radial-gradient(circle at 30% 30%, ${config.from}, ${config.to})`,
										`radial-gradient(circle at 70% 70%, ${config.to}, ${config.from})`,
										`radial-gradient(circle at 30% 30%, ${config.from}, ${config.to})`,
									],
							  }
							: undefined
					}
					transition={
						animState === "processing"
							? { duration: 4, repeat: Infinity, ease: "linear" }
							: undefined
					}
				/>

				{/* Rotating glow layer for processing — signals intelligence */}
				{animState === "processing" && (
					<motion.div
						className="absolute inset-[-20%] rounded-full opacity-40 pointer-events-none"
						style={{
							background: `conic-gradient(from 0deg, transparent, ${config.glow}, transparent, ${config.glow}, transparent)`,
						}}
						animate={{ rotate: 360 }}
						transition={{
							duration: 8,
							repeat: Infinity,
							ease: "linear",
						}}
					/>
				)}

				{/* Inner core — subtle highlight */}
				<div
					className="absolute inset-[15%] rounded-full pointer-events-none"
					style={{
						background: `radial-gradient(circle, rgba(255,255,255,0.15), transparent)`,
						backdropFilter: "blur(8px)",
					}}
				/>
			</motion.div>

			{/* Responsive ring — listening/speaking reacts to audio */}
			{(animState === "listening" || animState === "speaking") && (
				<motion.div
					className="absolute rounded-full border-2 pointer-events-none origin-center"
					style={{
						width: size + 20,
						height: size + 20,
						left: "50%",
						top: "50%",
						marginLeft: -(size + 20) / 2,
						marginTop: -(size + 20) / 2,
						borderColor:
							animState === "listening"
								? "rgba(0, 217, 255, 0.5)"
								: "rgba(0, 255, 136, 0.5)",
						opacity: haloOpacity,
						scale: ringScale,
					}}
				/>
			)}
		</motion.div>
	);
}
