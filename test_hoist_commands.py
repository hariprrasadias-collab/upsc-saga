import re

with open('frontend/src/components/CommandPalette/CommandPalette.tsx', 'r') as f:
    content = f.read()

commands_block = re.search(r'// Define available commands\s+const commands: CommandOption\[\] = \[\s*// Navigation.*?\];', content, re.DOTALL)
if commands_block:
    memoized = commands_block.group(0).replace('const commands: CommandOption[] = [', 'const commands: CommandOption[] = useMemo(() => [')
    memoized = memoized[:-1] + ', [setCurrentTab, toggleRageMode, toggleTimer, isRunning]);'

    content = content.replace(commands_block.group(0), memoized)

    # Also wrap filteredCommands in useMemo
    filtered_block = re.search(r'const filteredCommands = commands\.filter\(cmd =>\s*cmd\.label\.toLowerCase\(\)\.includes\(query\.toLowerCase\(\)\)\s*\);', content)
    memoized_filtered = filtered_block.group(0).replace('const filteredCommands =', 'const filteredCommands = useMemo(() =>').replace(');', '),\n    [commands, query]);')

    content = content.replace(filtered_block.group(0), memoized_filtered)

    # Needs to import useMemo
    content = content.replace("import React, { useState, useEffect, useRef } from 'react';", "import React, { useState, useEffect, useRef, useMemo } from 'react';")

    with open('frontend/src/components/CommandPalette/CommandPalette.tsx', 'w') as f:
        f.write(content)
