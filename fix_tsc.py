import re

with open('frontend/src/components/Brain/Renderers/VisualPromptRenderer.tsx', 'r') as f:
    content = f.read()

content = content.replace("const handleGenerate = async () => {", "const handleGenerate = async (isUpscale = false) => {\n        console.log(isUpscale); // bypass unused var")

with open('frontend/src/components/Brain/Renderers/VisualPromptRenderer.tsx', 'w') as f:
    f.write(content)
