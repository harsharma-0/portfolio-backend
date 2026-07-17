import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
COLLECTIONS = ("projects", "skills", "experience", "services", "achievements", "testimonials")


class ContentService:
    @staticmethod
    @lru_cache
    def load(name: str) -> Any:
        if name not in {"profile", *COLLECTIONS}:
            raise ValueError("Unknown content collection")
        with (DATA_DIR / f"{name}.json").open(encoding="utf-8") as file:
            return json.load(file)

    def projects(self, category: str | None = None, technology: str | None = None, featured: bool | None = None, search: str | None = None) -> list[dict[str, Any]]:
        projects = list(self.load("projects"))
        if category:
            projects = [p for p in projects if p["category"].casefold() == category.casefold()]
        if technology:
            projects = [p for p in projects if any(t.casefold() == technology.casefold() for t in p["technologies"])]
        if featured is not None:
            projects = [p for p in projects if p["featured"] is featured]
        if search:
            needle = search.casefold()
            projects = [
                project for project in projects
                if needle in " ".join([
                    project["title"], project["short_title"], project["summary"], project["description"], project["category"],
                    *project["technologies"], *project["responsibilities"], *project["challenges"],
                    *project["solutions"], *project["outcomes"],
                    *project.get("keywords", []),
                    *(metric["label"] for metric in project["metrics"]),
                    *(metric["value"] for metric in project["metrics"]),
                ]).casefold()
            ]
        return sorted(projects, key=lambda p: p["display_order"])

    def project(self, slug: str) -> dict[str, Any] | None:
        return next((project for project in self.load("projects") if project["slug"] == slug), None)

    def portfolio(self) -> dict[str, Any]:
        collections = {name: self.load(name) for name in COLLECTIONS}
        collections["projects"] = self.projects()
        return {"profile": self.load("profile"), **collections}


content_service = ContentService()
