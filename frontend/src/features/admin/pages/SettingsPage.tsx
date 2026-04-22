import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import {
	createApiKey,
	fetchApiKeys,
	fetchBilling,
	fetchInvitations,
	fetchMembers,
	inviteMember,
} from "../api/adminApi";
import { AdminShell, PageBody, PageHeader } from "../../../shared/ui/Layout";
import type {
	ApiKeyItem,
	BillingResponse,
	InvitationItem,
	TeamMember,
} from "../../../shared/types/api";

type TabKey = "billing" | "team" | "api-keys";

const TABS: { key: TabKey; label: string }[] = [
	{ key: "billing", label: "Billing & Usage" },
	{ key: "team", label: "Team" },
	{ key: "api-keys", label: "API Keys" },
];

const PLAN_DISPLAY: Record<string, { name: string; price: string }> = {
	free: { name: "Free", price: "$0/mo" },
	pro: { name: "Pro", price: "$29/mo" },
	business: { name: "Business", price: "$79/mo" },
	enterprise: { name: "Enterprise", price: "Custom" },
};

export default function SettingsPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const { tab } = useParams<{ tab: string }>();
	const orgId = admin?.memberships[0]?.org_id;

	const activeTab = (tab as TabKey) || "billing";

	return (
		<AdminShell
			email={admin?.email}
			onLogout={() => {
				logout();
				navigate("/admin/login");
			}}
		>
			<PageHeader
				title="Settings"
				subtitle="Manage your workspace, billing, team, and integrations."
				backTo="/admin"
				backLabel="Dashboard"
			/>
			<PageBody>
				<div className="flex gap-1 mb-6 bg-stone-100 p-1 rounded-lg w-fit">
					{TABS.map((t) => (
						<button
							key={t.key}
							type="button"
							onClick={() =>
								navigate(`/admin/settings/${t.key}`)
							}
							className={`px-4 py-2 rounded-md text-[13px] font-medium transition-all ${
								activeTab === t.key
									? "bg-bg-base text-text-primary shadow-sm"
									: "text-text-secondary hover:text-text-primary"
							}`}
						>
							{t.label}
						</button>
					))}
				</div>

				{activeTab === "billing" && orgId && (
					<BillingTab orgId={orgId} />
				)}
				{activeTab === "team" && orgId && <TeamTab orgId={orgId} />}
				{activeTab === "api-keys" && orgId && (
					<ApiKeysTab orgId={orgId} />
				)}
			</PageBody>
		</AdminShell>
	);
}

function BillingTab({ orgId }: { orgId: string }) {
	const [billing, setBilling] = useState<BillingResponse | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchBilling(orgId)
			.then(setBilling)
			.catch(() => {})
			.finally(() => setLoading(false));
	}, [orgId]);

	if (loading) {
		return (
			<div className="flex justify-center py-12">
				<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
			</div>
		);
	}

	if (!billing) return null;

	const plan = PLAN_DISPLAY[billing.plan.plan] || PLAN_DISPLAY.free;

	return (
		<div className="max-w-2xl space-y-6">
			{/* Current Plan */}
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<div className="flex items-center justify-between mb-4">
					<div>
						<h2 className="font-heading text-[20px] font-semibold text-text-primary">
							{plan.name} Plan
						</h2>
						<p className="text-[13px] text-text-secondary">
							{plan.price}
						</p>
					</div>
					{billing.plan.plan === "free" && (
						<button
							type="button"
							className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all shadow-forest"
						>
							Upgrade to Pro
						</button>
					)}
				</div>
			</section>

			{/* Usage */}
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6 space-y-4">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary">
					Usage This Period
				</h3>
				<UsageMeter
					label="Responses"
					used={billing.usage.responses_used}
					limit={billing.usage.responses_limit}
				/>
				<UsageMeter
					label="Forms"
					used={billing.usage.forms_used}
					limit={billing.usage.forms_limit}
				/>
				<UsageMeter
					label="Voice Minutes"
					used={Math.round(billing.usage.voice_minutes_used)}
					limit={billing.usage.voice_minutes_limit}
				/>
				<UsageMeter
					label="Team Seats"
					used={billing.usage.seats_used}
					limit={billing.usage.seats_limit}
				/>
			</section>

			{/* Plan comparison */}
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-4">
					Plans
				</h3>
				<div className="grid grid-cols-1 md:grid-cols-4 gap-3">
					{(
						[
							{
								key: "free",
								features: [
									"3 forms",
									"50 responses/mo",
									"Chat only",
								],
							},
							{
								key: "pro",
								features: [
									"Unlimited forms",
									"1,000 responses/mo",
									"Chat + Voice",
									"Custom branding",
								],
							},
							{
								key: "business",
								features: [
									"5,000 responses/mo",
									"500 voice min",
									"Webhooks",
									"Priority support",
								],
							},
							{
								key: "enterprise",
								features: [
									"Unlimited",
									"SSO",
									"Self-host",
									"SLA",
								],
							},
						] as const
					).map((p) => {
						const display = PLAN_DISPLAY[p.key];
						const isCurrent = billing.plan.plan === p.key;
						return (
							<div
								key={p.key}
								className={`rounded-lg border p-4 ${
									isCurrent
										? "border-forest-300 bg-forest-50/50"
										: "border-stone-200"
								}`}
							>
								<p className="text-[14px] font-semibold text-text-primary">
									{display.name}
								</p>
								<p className="text-[12px] text-text-secondary mb-3">
									{display.price}
								</p>
								<ul className="space-y-1">
									{p.features.map((f) => (
										<li
											key={f}
											className="text-[12px] text-text-secondary flex items-center gap-1.5"
										>
											<span className="w-1 h-1 rounded-full bg-forest-400" />
											{f}
										</li>
									))}
								</ul>
								{isCurrent && (
									<p className="mt-3 text-[11px] text-forest-600 font-medium">
										Current plan
									</p>
								)}
							</div>
						);
					})}
				</div>
			</section>
		</div>
	);
}

function UsageMeter({
	label,
	used,
	limit,
}: {
	label: string;
	used: number;
	limit: number;
}) {
	const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
	const isHigh = pct >= 80;
	return (
		<div>
			<div className="flex justify-between text-[13px] mb-1.5">
				<span className="text-text-primary font-medium">{label}</span>
				<span
					className={`tabular-nums ${isHigh ? "text-clay-600 font-medium" : "text-text-secondary"}`}
				>
					{used.toLocaleString()} / {limit >= 999999 ? "Unlimited" : limit.toLocaleString()}
				</span>
			</div>
			<div className="h-2 rounded-full bg-stone-100 overflow-hidden">
				<div
					className={`h-full rounded-full transition-all duration-500 ${isHigh ? "bg-clay-500" : "bg-forest-400/90"}`}
					style={{ width: `${pct}%` }}
				/>
			</div>
		</div>
	);
}

function TeamTab({ orgId }: { orgId: string }) {
	const [members, setMembers] = useState<TeamMember[]>([]);
	const [invitations, setInvitations] = useState<InvitationItem[]>([]);
	const [loading, setLoading] = useState(true);

	const [inviteEmail, setInviteEmail] = useState("");
	const [inviteRole, setInviteRole] = useState("org_editor");
	const [inviting, setInviting] = useState(false);
	const [inviteStatus, setInviteStatus] = useState("");

	useEffect(() => {
		Promise.all([fetchMembers(orgId), fetchInvitations(orgId)])
			.then(([m, i]) => {
				setMembers(m);
				setInvitations(i);
			})
			.catch(() => {})
			.finally(() => setLoading(false));
	}, [orgId]);

	const handleInvite = async () => {
		if (!inviteEmail) return;
		setInviting(true);
		setInviteStatus("");
		try {
			const inv = await inviteMember(orgId, {
				email: inviteEmail,
				role: inviteRole,
			});
			setInvitations((prev) => [inv, ...prev]);
			setInviteEmail("");
			setInviteStatus("Invitation sent!");
		} catch (err) {
			setInviteStatus(
				err instanceof Error ? err.message : "Failed to invite",
			);
		} finally {
			setInviting(false);
		}
	};

	if (loading) {
		return (
			<div className="flex justify-center py-12">
				<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
			</div>
		);
	}

	return (
		<div className="max-w-2xl space-y-6">
			{/* Invite */}
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
					Invite Team Member
				</h3>
				<div className="flex gap-2">
					<input
						className="flex-1 px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none focus:border-forest-500 focus:shadow-forest-ring"
						placeholder="colleague@company.com"
						value={inviteEmail}
						onChange={(e) => setInviteEmail(e.target.value)}
						type="email"
					/>
					<select
						className="px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none focus:border-forest-500 focus:shadow-forest-ring"
						value={inviteRole}
						onChange={(e) => setInviteRole(e.target.value)}
					>
						<option value="org_admin">Admin</option>
						<option value="org_editor">Editor</option>
						<option value="org_viewer">Viewer</option>
					</select>
					<button
						type="button"
						onClick={handleInvite}
						disabled={inviting || !inviteEmail}
						className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all disabled:opacity-50 shadow-forest"
					>
						{inviting ? "Sending..." : "Invite"}
					</button>
				</div>
				{inviteStatus && (
					<p className="text-[12px] text-text-secondary mt-2">
						{inviteStatus}
					</p>
				)}
			</section>

			{/* Members */}
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
					Members ({members.length})
				</h3>
				<div className="space-y-3">
					{members.map((m) => (
						<div
							key={m.id}
							className="flex items-center justify-between py-2"
						>
							<div className="flex items-center gap-3">
								<div className="w-8 h-8 rounded-full bg-forest-100 text-forest-700 grid place-items-center text-[13px] font-semibold">
									{(m.full_name || m.email)
										.charAt(0)
										.toUpperCase()}
								</div>
								<div>
									<p className="text-[14px] text-text-primary font-medium">
										{m.full_name}
									</p>
									<p className="text-[12px] text-text-tertiary">
										{m.email}
									</p>
								</div>
							</div>
							<span className="text-[12px] px-2.5 py-1 rounded-full bg-stone-100 text-text-tertiary capitalize">
								{m.role.replace("org_", "")}
							</span>
						</div>
					))}
				</div>
			</section>

			{/* Pending invitations */}
			{invitations.filter((i) => i.status === "pending").length > 0 && (
				<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
					<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
						Pending Invitations
					</h3>
					<div className="space-y-2">
						{invitations
							.filter((i) => i.status === "pending")
							.map((inv) => (
								<div
									key={inv.id}
									className="flex items-center justify-between py-2"
								>
									<span className="text-[13px] text-text-primary">
										{inv.email}
									</span>
									<span className="text-[11px] px-2 py-0.5 rounded-full bg-clay-100 text-clay-600">
										{inv.role.replace("org_", "")} ·
										pending
									</span>
								</div>
							))}
					</div>
				</section>
			)}
		</div>
	);
}

function ApiKeysTab({ orgId }: { orgId: string }) {
	const [keys, setKeys] = useState<ApiKeyItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [newKeyName, setNewKeyName] = useState("");
	const [creating, setCreating] = useState(false);
	const [newKeyValue, setNewKeyValue] = useState<string | null>(null);

	useEffect(() => {
		fetchApiKeys(orgId)
			.then(setKeys)
			.catch(() => {})
			.finally(() => setLoading(false));
	}, [orgId]);

	const handleCreate = async () => {
		if (!newKeyName.trim()) return;
		setCreating(true);
		try {
			const result = await createApiKey(orgId, { name: newKeyName });
			setNewKeyValue(result.key);
			setKeys((prev) => [result, ...prev]);
			setNewKeyName("");
		} catch {
			// handle silently
		} finally {
			setCreating(false);
		}
	};

	if (loading) {
		return (
			<div className="flex justify-center py-12">
				<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
			</div>
		);
	}

	return (
		<div className="max-w-2xl space-y-6">
			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
					Create API Key
				</h3>
				<div className="flex gap-2">
					<input
						className="flex-1 px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none focus:border-forest-500 focus:shadow-forest-ring"
						placeholder="Key name (e.g. Production)"
						value={newKeyName}
						onChange={(e) => setNewKeyName(e.target.value)}
					/>
					<button
						type="button"
						onClick={handleCreate}
						disabled={creating || !newKeyName.trim()}
						className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all disabled:opacity-50 shadow-forest"
					>
						{creating ? "Creating..." : "Create Key"}
					</button>
				</div>
				{newKeyValue && (
					<div className="mt-3 p-3 rounded-md bg-clay-50 border border-clay-200">
						<p className="text-[12px] text-clay-700 font-medium mb-1">
							Copy this key now — it won't be shown again:
						</p>
						<code className="text-[13px] font-mono text-clay-800 break-all">
							{newKeyValue}
						</code>
					</div>
				)}
			</section>

			<section className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6">
				<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
					Your API Keys ({keys.length})
				</h3>
				{keys.length === 0 ? (
					<p className="text-[13px] text-text-tertiary py-4 text-center">
						No API keys yet.
					</p>
				) : (
					<div className="space-y-3">
						{keys.map((k) => (
							<div
								key={k.id}
								className="flex items-center justify-between py-2 border-b border-stone-100 last:border-0"
							>
								<div>
									<p className="text-[14px] text-text-primary font-medium">
										{k.name}
									</p>
									<p className="text-[12px] text-text-tertiary font-mono">
										{k.prefix}...
									</p>
								</div>
								<span
									className={`text-[11px] px-2 py-0.5 rounded-full ${
										k.is_active
											? "bg-forest-100 text-forest-600"
											: "bg-stone-100 text-stone-500"
									}`}
								>
									{k.is_active ? "Active" : "Inactive"}
								</span>
							</div>
						))}
					</div>
				)}
			</section>
		</div>
	);
}
