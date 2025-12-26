# Transaction Policy for Database Operations

## General Rule: All-or-None for Multiple Changes

**IMPORTANT INSTRUCTION**: When performing multiple database changes in one command or operation,
those changes MUST be wrapped in a transaction to ensure atomicity (all or none).

## Why This Matters

Database transactions ensure data consistency by guaranteeing that either:

- **All** changes succeed and are committed, OR
- **None** of the changes are applied (rollback on any failure)

This prevents partial updates that could leave the database in an inconsistent state.

## Implementation Pattern

When implementing functions that perform multiple database updates:

1. **Begin a transaction** before making any changes
2. **Execute all changes** within the transaction
3. **Rollback on any error** to undo all changes
4. **Commit** only if all changes succeed

### Example Template

```rust
async fn example_multiple_updates(&self, id: i64) -> Result<Response, ApiError> {
    // Begin transaction
    let mut tx = match self.context.pool.begin().await {
        Ok(tx) => tx,
        Err(e) => {
            error!("Failed to begin transaction: {}", e);
            return Err(database_error(e));
        }
    };

    // Perform multiple updates within the transaction
    for item in items {
        match sqlx::query!(
            r#"UPDATE table SET field = $1 WHERE id = $2"#,
            value,
            item.id
        )
        .execute(&mut *tx)
        .await
        {
            Ok(_) => {
                info!("Updated item {}", item.id);
            }
            Err(e) => {
                error!("Failed to update item {}: {}", item.id, e);
                let _ = tx.rollback().await;  // Rollback on error
                return Err(database_error(e));
            }
        }
    }

    // Commit the transaction
    if let Err(e) = tx.commit().await {
        error!("Failed to commit transaction: {}", e);
        return Err(database_error(e));
    }

    Ok(Response::SuccessfulResponse(data))
}
```

## Examples in Codebase

### Good Examples (Transactional)

- `create_job` - Creates job and all relationships atomically
- `create_jobs` - Bulk job creation in a single transaction
- `initialize_jobs` - Multiple workflow initialization steps in one transaction
- `process_changed_job_inputs` - Updates multiple job statuses atomically

### Functions That Should Use Transactions

Any function that:

- Updates multiple records
- Performs cascading updates across related tables
- Changes state that must be consistent across multiple entities
- Could leave the database in an inconsistent state if partially completed

## Key Considerations

1. **Scope**: Keep transactions as short as possible - don't include long-running operations
2. **Error Handling**: Always rollback on errors before returning
3. **Logging**: Log transaction start, commit, and rollback for debugging
4. **Read-Only Operations**: Don't need transactions, use connection pool directly
5. **Single Updates**: Simple single-record updates may not need transactions (use judgment)

## Related Documentation

- See `src/server/api/jobs.rs` for examples of transactional operations
- See `torc-server/src/server.rs` for workflow initialization transaction pattern
