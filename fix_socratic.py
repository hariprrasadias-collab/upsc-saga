import re

with open('frontend/src/components/Socratic/SocraticHistory.tsx', 'r') as f:
    content = f.read()

filtered = re.search(r'const filteredHistory = useMemo\(\(\) => \{.*?\}, \[searchTerm, history\]\);', content, re.DOTALL)
if filtered:
    content = content.replace("import React, { useState, useEffect, useRef }", "import React, { useState, useEffect, useRef, useMemo }")
    with open('frontend/src/components/Socratic/SocraticHistory.tsx', 'w') as f:
        f.write(content)
