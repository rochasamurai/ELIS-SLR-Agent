# PR #430 - One-Time Fallback Exception

## Summary
PR #430 was a one-time fallback exception that allowed temporary bypass of the new GitHub Agent source path enforcement rules to maintain backward compatibility during transition.

## Rationale
While the new enforcement rules are strongly recommended, certain legacy operations required a temporary exception to prevent disruption of ongoing workflows.

## Exception Details
- Applied only for specific legacy workflows
- Limited to a single execution window
- Properly documented and reviewed by security/operations team
- Scheduled for removal once migration is completed

## References
- Related PE: PE-OPS-GITHUB-AGENT-ENFORCEMENT-01
- Implementation: Documented in this evidence file for reference
- Future: This exception should not be repeated in new implementations