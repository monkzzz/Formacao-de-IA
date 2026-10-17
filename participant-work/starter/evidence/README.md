# Execution evidence

Owner: the agent records actual actions and results; reviewers assess their scope.
Use dated, uniquely named Markdown or JSON records. Keep historical records intact.
Large binaries belong in the documented artifact store, referenced by hash/version.

Each record should identify:

- Task and acceptance criterion, date/time, actor and source commit if known.
- Command or precise action, working directory, nonsecret environment and tool version.
- Input identity/hash where material, exit code, raw output location and observations.
- Status (`PASS`, `FAIL`, `NOT RUN`), interpretation and explicit limits.
- Follow-up action and links to decisions or findings supported by the result.

Distinguish live, recorded, mocked and synthetic outputs. A successful tool listing
does not prove authentication, write access or a completed operation. Record failed
attempts and subsequent fixes separately. Never invent human review or acceptance.

This generic directory contains the record contract only. Evidence from preparing
the course submission stays outside the reusable starter so it cannot be mistaken
for verification in a future project's environment.
