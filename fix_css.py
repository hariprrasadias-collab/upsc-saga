import re

with open('frontend/src/components/DashboardMain/RevisionWidget.css', 'r') as f:
    content = f.read()

# The corrupted block starts at `.more-count {` around line 303 and ends before `.revision-empty-state {`
# We will just replace it entirely.
pattern = re.compile(r'\.more-count \{[\s\S]*?(?=\.revision-empty-state \{)')

replacement = """.more-count {
    text-align: center;
    font-size: 0.8rem;
    color: #8b9bb4;
    margin-top: 12px;
    font-style: italic;
    opacity: 0.6;
    font-family: 'Cinzel', serif;
}

"""

new_content = pattern.sub(replacement, content)

with open('frontend/src/components/DashboardMain/RevisionWidget.css', 'w') as f:
    f.write(new_content)

print("CSS Fixed")
