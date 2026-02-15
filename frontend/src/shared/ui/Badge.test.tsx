import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge, StatusBadge } from "./Badge";

describe("Badge", () => {
	it("renders with default variant", () => {
		render(<Badge>Default</Badge>);
		expect(screen.getByText("Default")).toBeInTheDocument();
	});

	it("renders success variant", () => {
		const { container } = render(<Badge variant="success">Active</Badge>);
		expect(container.firstChild).toHaveClass("bg-success/20");
	});
});

describe("StatusBadge", () => {
	it("renders published status as success", () => {
		const { container } = render(<StatusBadge status="published" />);
		expect(container.firstChild).toHaveClass("bg-success/20");
	});

	it("renders draft status as warning", () => {
		const { container } = render(<StatusBadge status="draft" />);
		expect(container.firstChild).toHaveClass("bg-warning/20");
	});
});
