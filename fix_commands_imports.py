import re

with open('frontend/src/components/CommandPalette/CommandPalette.tsx', 'r') as f:
    content = f.read()

if 'useMemo' not in content[:100]:
    content = content.replace("import React, { useState, useEffect, useRef } from 'react';", "import React, { useState, useEffect, useRef, useMemo } from 'react';")

with open('frontend/src/components/CommandPalette/CommandPalette.tsx', 'w') as f:
    f.write(content)
