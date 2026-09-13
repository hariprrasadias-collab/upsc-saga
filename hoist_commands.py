import re

with open('frontend/src/components/CommandPalette/CommandPalette.tsx', 'r') as f:
    content = f.read()

commands_block = re.search(r'// Define available commands\s+const commands: CommandOption\[\] = \[\s*// Navigation.*?\];', content, re.DOTALL)
if commands_block:
    # Need to keep the action references lazy or pass them in?
    # Actually, toggleTimer and toggleRageMode and setCurrentTab depend on hooks.
    # So we can't completely hoist the commands array out of the component without changing their signature.
    # BUT we can wrap it in useMemo!

    memoized = commands_block.group(0).replace('const commands: CommandOption[] = [', 'const commands: CommandOption[] = useMemo(() => [') + '\n    ], [setCurrentTab, toggleRageMode, toggleTimer, isRunning]);'

    # Also wrap filteredCommands in useMemo
    filtered_block = re.search(r'const filteredCommands = commands\.filter\(cmd =>\s*cmd\.label\.toLowerCase\(\)\.includes\(query\.toLowerCase\(\)\)\s*\);', content)
    memoized_filtered = filtered_block.group(0).replace('const filteredCommands =', 'const filteredCommands = useMemo(() =>').replace(');', '), [commands, query]);')

    # Needs to import useMemo
    content = content.replace("import React, { useState, useEffect, useRef } from 'react';", "import React, { useState, useEffect, useRef, useMemo } from 'react';")

    print("Found commands to wrap")
else:
    print("Could not find commands block")
