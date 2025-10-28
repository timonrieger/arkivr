import dotenv

dotenv.load_dotenv()

MEDIUM_CHOICES = [
    "Website",
    "Video",
    "Repository",
    "Tool",
    "Documentation",
    "Article",
    "Paper",
]

CATEGORY_CHOICES = [
    "Education",
    "Code",
    "Data Science",
    "Security",
    "Crypto",
    "Design",
    "Research",
    "Finance",
    "Productivity",
    "Data",
    "Politics",
    "Utility",
]

TAGS_CHOICES = [
    "Framework",
    "Language",
    "Algorithms",
    "Containerization",
    "Visualization",
    "Authentication",
    "Blockchain",
    "DeFi",
    "CI/CD",
    "Virtualization",
    "Cloud",
    "Server",
    "Testing",
    "Frontend",
    "Search",
    "Design",
    "Backend",
    "Data Analysis",
    "AI",
    "Charting",
    "Version Control",
    "API",
    "Maths",
    "Analytics",
    "Open Source",
    "Communication",
    "IoT",
    "Payments",
]

RESSOURCE_SCHEMA = {
    "required": ["name", "link", "description", "category", "medium"],
    "optional": ["tags", "private"],
}
