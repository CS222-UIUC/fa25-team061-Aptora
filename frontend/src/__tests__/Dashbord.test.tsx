import { render, screen } from "@testing-library/react";
import Dashboard from "../pages/Dashboard";

test("renders Dashboard page", () => {
  render(<Dashboard />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
});