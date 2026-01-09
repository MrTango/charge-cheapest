# Spec and Implement (Multi-Agent)

This command chains together the full specification-to-implementation workflow without pausing for user input. Use this after `/shape-spec` when you want to go straight from requirements to implemented code.

This command will execute the following phases IN SEQUENCE without asking for confirmation:

1. **Write Spec**: Delegate to spec-writer to create spec.md
2. **Create Tasks**: Delegate to tasks-list-creator to generate tasks.md
3. **Implement Tasks**: Delegate to implementer to implement ALL tasks
4. **Verify**: Delegate to implementation-verifier for final verification

Follow each of these phases and their individual workflows IN SEQUENCE:

## Multi-Phase Process

### PHASE 1: Locate the spec folder

Find the most recent spec folder in `agent-os/specs/` that has a `planning/requirements.md` file but does NOT yet have a `spec.md` file.

IF no such spec folder exists, output this message and STOP:

```
No spec folder found with requirements ready for specification writing.

Please run `/shape-spec` first to initialize a spec and gather requirements.
```

Store the spec folder path for use in subsequent phases.

### PHASE 2: Write Specification

Delegate to the **spec-writer** subagent to create the specification document:

Provide the spec-writer with:
- The spec folder path
- The requirements from `planning/requirements.md`
- Any visual assets in `planning/visuals/`

The spec-writer will create `spec.md` inside the spec folder.

Immediately proceed to PHASE 3 once spec.md is created.

### PHASE 3: Create Tasks List

Delegate to the **tasks-list-creator** subagent to create the tasks breakdown:

Provide the tasks-list-creator with:
- The spec folder path
- The spec.md that was just created
- The requirements from `planning/requirements.md`

The tasks-list-creator will create `tasks.md` inside the spec folder.

Immediately proceed to PHASE 4 once tasks.md is created.

### PHASE 4: Implement All Tasks

**IMPORTANT**: Do NOT ask which tasks to implement. Implement ALL task groups automatically.

Delegate to the **implementer** subagent to implement ALL task groups:

Provide the implementer with:
- ALL task groups from `agent-os/specs/[this-spec]/tasks.md`
- The spec file: `agent-os/specs/[this-spec]/spec.md`
- The requirements: `agent-os/specs/[this-spec]/planning/requirements.md`
- Any visuals: `agent-os/specs/[this-spec]/planning/visuals/`

Instruct the implementer to:
1. Implement ALL task groups in sequence
2. Mark each completed task with `- [x]` in tasks.md
3. Continue until ALL tasks are marked complete

Once ALL tasks are marked complete, proceed to PHASE 5.

### PHASE 5: Verify Implementation

Delegate to the **implementation-verifier** subagent for final verification:

Provide the implementation-verifier with:
- The spec folder path: `agent-os/specs/[this-spec]`

Instruct the implementation-verifier to:
1. Run all final verifications according to its built-in workflow
2. Produce the final verification report in `agent-os/specs/[this-spec]/verification/final-verification.md`

### PHASE 6: Display Completion Summary

After verification is complete, display the following summary to the user:

```
Spec and Implementation Complete!

Spec: `agent-os/specs/[this-spec]/spec.md`
Tasks: `agent-os/specs/[this-spec]/tasks.md`
Verification: `agent-os/specs/[this-spec]/verification/final-verification.md`

All phases completed:
1. Specification written
2. Tasks created
3. All tasks implemented
4. Verification complete

Please review the verification report for any issues that may need attention.
```
