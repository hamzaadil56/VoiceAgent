import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Input } from "./Input";

describe("Input", () => {
	it("renders with label", () => {
		render(<Input label="Email" />);
		expect(screen.getByLabelText("Email")).toBeInTheDocument();
	});

	it("shows error message", () => {
		render(<Input label="Email" error="Required field" />);
		expect(screen.getByText("Required field")).toBeInTheDocument();
		expect(screen.getByRole("alert")).toBeInTheDocument();
	});

	it("shows hint text", () => {
		render(<Input label="Name" hint="Enter your full name" />);
		expect(screen.getByText("Enter your full name")).toBeInTheDocument();
	});

	it("fires onChange", () => {
		const onChange = vi.fn();
		render(<Input label="Name" onChange={onChange} />);
		fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Test" } });
		expect(onChange).toHaveBeenCalled();
	});

	it("sets aria-invalid when error is present", () => {
		render(<Input label="Email" error="Invalid" />);
		expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "true");
	});
});
