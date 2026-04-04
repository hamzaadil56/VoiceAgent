import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
	it("renders with default props", () => {
		render(<Button>Click me</Button>);
		expect(screen.getByText("Click me")).toBeInTheDocument();
	});

	it("calls onClick handler", () => {
		const onClick = vi.fn();
		render(<Button onClick={onClick}>Click</Button>);
		fireEvent.click(screen.getByText("Click"));
		expect(onClick).toHaveBeenCalledTimes(1);
	});

	it("shows loading spinner when loading", () => {
		render(<Button loading>Submit</Button>);
		const button = screen.getByText("Submit").closest("button");
		expect(button).toBeDisabled();
		expect(button?.querySelector(".animate-spin")).toBeTruthy();
	});

	it("is disabled when disabled prop is set", () => {
		render(<Button disabled>Disabled</Button>);
		expect(screen.getByText("Disabled").closest("button")).toBeDisabled();
	});

	it("applies variant styles", () => {
		const { container } = render(<Button variant="secondary">Secondary</Button>);
		const button = container.querySelector("button");
		expect(button?.className).toContain("glass");
	});

	it("applies size styles", () => {
		const { container } = render(<Button size="sm">Small</Button>);
		const button = container.querySelector("button");
		expect(button?.className).toContain("text-sm");
	});
});
