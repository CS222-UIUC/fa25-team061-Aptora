import { render, screen } from "@testing-library/react";
import About from "../pages/About";

test("renders About page", () => {
  render(<About />);
  expect(screen.getByText(/About/i)).toBeInTheDocument();
});