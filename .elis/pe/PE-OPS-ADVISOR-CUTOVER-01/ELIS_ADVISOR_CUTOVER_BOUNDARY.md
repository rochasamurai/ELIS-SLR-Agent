# ELIS Advisor Production Cutover Boundary Document

## 1. Objective
Finalize the ELIS Advisor production handoff/cutover on Hermes, defining clear boundaries, readiness gates, evidence requirements, rollback expectations, and operational constraints.

## 2. Cutover Boundary
The cutover boundary encompasses the transition from the existing advisor runtime environment to the production Hermes environment with clear separation of duties and operational boundaries.

### 2.1 Runtime Context
- **Current Environment**: ELIS Advisor operates on elis-server as a separate Hermes profile, Discord bot, and systemd service
- **Production Environment**: ELIS Advisor on Hermes with specific channel bindings
- **Gateway Runtime**: Single, controlled Hermes instance with specific profile configuration
- **Channel Bindings**: Dedicated Discord channel `<#1502602267931578378>` for advisor interactions
- **Active Sessions**: Only one advisor session/gateway is permitted active at any time

### 2.2 Boundary Parameters
- No simultaneous runtime instances are permitted
- No cross-environment message relaying
- No shared state between current and production environments
- Strict separation of concern between advisory and implementing functions

## 3. Readiness Gates

### 3.1 Pre-Cutover Verification 
1. **Worktree State Verification**:
   - Clean git status with no uncommitted changes
   - Verified feature branch `feature/pe-ops-advisor-cutover-01`
   - Correct HEAD commit `bf865e117a4bbd44a3a6d7ca92161100f38df185`

2. **Runtime Environment Checks**:
   - Advisor gateway session integrity
   - Channel binding validity
   - Permission scopes properly configured
   - No conflicting dispatcher activities

3. **Security Audits**:
   - Token/secret handling policies verified
   - Access controls validated
   - Identity preservation protocols confirmed

### 3.2 Operational Requirements 
1. **Identity and Session Preservation**:
   - Existing advisor identity maintained
   - Session continuity requirements met
   - Channel access credentials verified

2. **Monitoring and Log Validation**:
   - Real-time logging capability verified
   - Alerting mechanisms in place
   - Audit trails established

3. **Evidence Collection**:
   - All necessary documentation in place
   - Configuration checkpoints captured
   - Before/after state comparisons ready

## 4. Evidence Requirements
Evidence must demonstrate all cutover components have been verified and are ready for production handoff.

### 4.1 Required Evidence Items
1. **Git Status Verification**:
   ```
   git status -sb
   ```
   
2. **Branch and Commit Confirmation**:
   ```
   git branch --show-current
   git rev-parse HEAD
   ```
   
3. **Remote Repository Validation**:
   ```
   git remote -v
   ```

4. **Change Diff Verification**:
   - Only the approved opening files have been modified
   - No unauthorized modifications to runtime or configuration files

5. **Operational Readiness Check**:
   - Advisor gateway session status
   - Channel binding confirmation
   - Runtime configuration compliance

### 4.2 Validation Criteria
- All gates passed successfully
- No violations detected in operational boundaries
- Evidence items are captured and accessible
- All stakeholders have reviewed findings

## 5. Rollback Expectations 

### 5.1 Immediate Recovery Steps
1. **Revert Configuration Changes**:
   - Revert `CURRENT_PE.md` to previous state
   - Remove `.elis/pe/PE-OPS-ADVISOR-CUTOVER-01/PE_TASK.md`
   - Clean up feature branch if required

2. **Service Restoration**:
   - Restart any affected services back to prior state
   - Restore original advisor session
   - Reestablish original channel bindings

3. **Data Preservation**:
   - Maintain all captured evidence
   - Preserve any operational logs
   - Secure any temporary artifacts

### 5.2 Comprehensive Recovery Procedures
- System state restoration to known good baseline
- Channel access verification
- Identity validation restoration
- Full auditing of rollback operations  

## 6. Runtime Ownership Checks
All runtime operations must maintain strict ownership boundaries and access controls.

### 6.1 Access Control Protocols
- **Identity Management**:
  - Advisor identity remains consistent throughout cutover
  - Session tokens handled securely
  - Access rights remain restricted as specified

- **Permission Boundaries**:
  - No service restart privileges
  - No config modification access
  - No secret handling authority
  - No GitHub write permissions

### 6.2 Monitoring and Validation Expectations
- Real-time health monitoring activated
- Log aggregation pipeline verified
- Alert thresholds properly configured
- Audit trail enabled for all actions

## 7. Secret Handling Constraints
All secrets and access credentials must follow defined handling procedures.

### 7.1 Security Compliance
- Secrets accessed only through trusted methods
- No storage of secrets in plain text files
- Credential rotation policies enforced
- Minimal privilege access principles applied

### 7.2 Handling Methods
- Encrypted credential storage used
- Access logging implemented
- Manual verification required for any credential access
- Automated systems restricted to necessary minimum

## 8. Identity and Session Preservation Requirements
Critical to maintaining continuity of advisor operations.

### 8.1 Session Integrity
- Advisor identity preserved end-to-end
- Session tokens renewed appropriately
- Channel binding maintained throughout process
- Communication protocols unchanged

### 8.2 Continuity Assurance
- Seamless transition without session disruption  
- Identity verification before any operational changes
- Cross-environment compatibility validated
- User experience consistency maintained

## 9. Conditions for Live Cutover
All conditions must be satisfied before any live cutover execution.

### 9.1 Pre-Cutover Requirements
1. All readiness gates successfully passed
2. Stakeholder review and approval obtained
3. Evidence repository fully populated
4. Rollback procedures verified and documented

### 9.2 Operational Safety Conditions
1. No pending workloads or active processes
2. Full system monitoring in place
3. Emergency contact availability confirmed
4. Change management authorization in place

### 9.3 Validation Checklist
- [ ] All technical requirements verified
- [ ] Operational boundaries respected
- [ ] Security constraints upheld
- [ ] Identity preservation confirmed
- [ ] Rollback capability validated
- [ ] Stakeholder endorsement received

## 10. Conclusion
This document serves as the authoritative reference for the ELIS Advisor production cutover, ensuring all operational aspects are properly defined, boundaries are enforced, and the process is conducted safely and securely. The formalization of these requirements provides a baseline for any future cutover operations and establishes clear accountability for all involved parties.