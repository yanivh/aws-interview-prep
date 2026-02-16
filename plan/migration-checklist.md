# Async Migration Checklist

Use this checklist to track your progress through the async migration.

## Pre-Migration Setup
- [ ] Review current codebase structure
- [ ] Identify all boto3 client usages
- [ ] Document current performance metrics (baseline)
- [ ] Create feature branch: `git checkout -b feature/async-migration`

## Phase 1: Dependencies
- [ ] Update `lambda/requirements.txt`:
  - [ ] Add `aioboto3>=12.0.0`
  - [ ] Verify Python version (3.11+ recommended)
- [ ] Test dependency installation locally
- [ ] Update deployment scripts if needed

## Phase 2: BedrockService Migration
- [ ] Convert `__init__` to remove sync clients
- [ ] Add `aioboto3.Session()` initialization
- [ ] Convert `generate_question()` to async
- [ ] Convert `_generate_question_candidates()` to async
- [ ] Convert `_refine_question_candidates()` to async
- [ ] Convert `_invoke_bedrock_model()` to async
- [ ] Convert `evaluate_answer()` to async
- [ ] Convert `_evaluate_with_model()` to async
- [ ] Convert `generate_flashcard()` to async
- [ ] Convert `_parse_agent_response()` to async (if needed)
- [ ] Verify all helper methods (non-async ones stay the same)

## Phase 3: Lambda Handler Migration
- [ ] Create `async_lambda_handler()` function
- [ ] Convert `handle_generate_question()` to async
- [ ] Convert `handle_evaluate_answer()` to async
- [ ] Convert `handle_get_topics()` to async
- [ ] Convert `handle_get_flashcard()` to async
- [ ] Convert `handle_get_learning_plan()` to async
- [ ] Convert `handle_get_progress()` to async
- [ ] Convert `handle_update_progress()` to async
- [ ] Add synchronous wrapper `lambda_handler()` using `asyncio.run()`
- [ ] Or configure Lambda to use async handler directly

## Phase 4: Testing
- [ ] Unit tests for async methods
- [ ] Test question generation endpoint
- [ ] Test answer evaluation endpoint
- [ ] Test topics endpoint
- [ ] Test flashcard endpoint
- [ ] Test learning plan endpoint
- [ ] Test error handling
- [ ] Test concurrent requests
- [ ] Load testing

## Phase 5: Optimization
- [ ] Review for parallel operations opportunities
- [ ] Optimize client session reuse
- [ ] Check for resource leaks
- [ ] Performance benchmarking
- [ ] Memory usage analysis

## Phase 6: Deployment
- [ ] Deploy to staging environment
- [ ] Monitor CloudWatch logs
- [ ] Monitor CloudWatch metrics (duration, errors, throttles)
- [ ] Compare performance with baseline
- [ ] Fix any issues found
- [ ] Deploy to production
- [ ] Monitor production for 24-48 hours

## Phase 7: Cleanup
- [ ] Remove old sync code (if keeping both temporarily)
- [ ] Update documentation
- [ ] Merge feature branch to main
- [ ] Update README with async architecture notes

## Rollback Plan (if needed)
- [ ] Keep sync version in git history
- [ ] Document rollback procedure
- [ ] Test rollback process
- [ ] Monitor for issues after deployment

## Notes Section
Use this space to track issues, decisions, and learnings:

```
Date: ___________
Issue: 
Resolution:

Date: ___________
Issue: 
Resolution:
```
