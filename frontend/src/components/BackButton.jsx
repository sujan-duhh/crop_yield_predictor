import { Link } from "react-router-dom";

export default function BackButton() {
  return (
    <div className="mb-4">
      <Link
        to="/"
        className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 transition"
      >
        ⬅ Back to Home
      </Link>
    </div>
  );
}
