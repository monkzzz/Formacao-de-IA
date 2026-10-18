# Checking changed behavior and recording evidence

Paths below refer to AgentDATA unless stated otherwise.

Choose checks that exercise changed behavior: focused tests, boundary/integration
checks, compilation where relevant, links for Markdown and interaction/visual
inspection for interfaces. Do not add tests that merely duplicate a trivial edit.
Record command, working directory, environment, exit status, observed result and
limitations in a dated record under logs/ or a validation report under docs/.
Use PASS, FAIL, BLOCKED or NOT RUN accurately. Keep original failures when a retry
adds meaningful evidence. Linux success is not evidence of Windows execution.
