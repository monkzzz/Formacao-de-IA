# Building a project CLI or operational script

Paths below refer to AgentDATA unless stated otherwise.

Establish purpose, inputs, output format, exit codes and side effects first.
Follow the chosen project runtime; scripts/ does not require TypeScript. Keep
paths portable, arguments quoted and failures diagnosable. Exercise real success
and relevant error paths. Do not install a global executable without scope.
Register the verified command in tools/ and document its environment requirements.
