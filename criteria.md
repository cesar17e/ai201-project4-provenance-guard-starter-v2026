# Provenance Guard — Unit 7 Acceptance Criteria

## 1. False-positive rate

**Target:** Among 20 independently verified human-written samples, no more than 1 may receive the high-confidence AI label (a false-positive rate of at most 5%).

**Reason:** Incorrectly accusing a real writer of using AI can damage trust, so I want the system to be cautious about making high-confidence accusations.

## 2. Label coverage

**Target:** All three labels—high-confidence human, unsure, and high-confidence AI—must be reachable through controlled test scores. Every score from 0 to 1 must map to exactly one label, including threshold boundaries.

**Reason:** Every valid score needs an unambiguous, understandable outcome. The system must be able to express uncertainty rather than forcing every result into AI or human.

## 3. Appeal handling

**Target:** For 10 valid appeals referencing 10 existing content IDs, all 10 must create an appeal record in the audit log and change the corresponding content's status to `under_review`.

**Reason:** A writer who disagrees with a decision should have a dependable way to request review, and the service needs to preserve evidence of that request.

## 4. Invalid input handling

**Target:** All 6 invalid submission cases must return an HTTP 4xx response without crashing the service: missing text, empty text, whitespace-only text, missing creator ID, non-string text, and a JSON body that is not an object.

**Reason:** Invalid requests should fail predictably. The detector should not attempt to analyze unusable input or return a server error because the input was malformed.

## 5. Audit logging

**Target:** For 10 valid submissions, all 10 must create an audit log entry containing a timestamp, content ID, creator ID, model signal score, style signal score, combined score, and status. Each entry must correspond to the returned submission ID.

**Reason:** Recording the information behind each decision makes the service easier to debug, allows a writer's appeal to be traced, and supports evaluation in Unit 8.
