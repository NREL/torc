//! Event-related API endpoints

use async_trait::async_trait;
use chrono::{DateTime, Utc};
use log::{debug, error};
use sqlx::Row;
use swagger::{ApiError, Has, XSpanIdString};

use crate::server::api_types::{
    CreateEventResponse, DeleteEventResponse, DeleteEventsResponse, GetEventResponse,
    GetLatestEventTimestampResponse, ListEventsResponse, UpdateEventResponse,
};

use crate::models;

use super::{
    ApiContext, MAX_RECORD_TRANSFER_COUNT, SqlQueryBuilder, database_error, json_parse_error,
};

/// Trait defining event-related API operations
#[async_trait]
pub trait EventsApi<C> {
    /// Store an event.
    async fn create_event(
        &self,
        mut body: models::EventModel,
        context: &C,
    ) -> Result<CreateEventResponse, ApiError>;

    /// Retrieve an event by ID.
    async fn get_event(&self, id: i64, context: &C) -> Result<GetEventResponse, ApiError>;

    /// Retrieve all events for one workflow.
    async fn list_events(
        &self,
        workflow_id: i64,
        offset: i64,
        limit: i64,
        sort_by: Option<String>,
        reverse_sort: Option<bool>,
        category: Option<String>,
        after_timestamp: Option<f64>,
        context: &C,
    ) -> Result<ListEventsResponse, ApiError>;

    /// Update an event.
    async fn update_event(
        &self,
        id: i64,
        body: serde_json::Value,
        context: &C,
    ) -> Result<UpdateEventResponse, ApiError>;

    /// Delete an event.
    async fn delete_event(
        &self,
        id: i64,
        body: Option<serde_json::Value>,
        context: &C,
    ) -> Result<DeleteEventResponse, ApiError>;

    /// Delete all events for one workflow.
    async fn delete_events(
        &self,
        workflow_id: i64,
        body: Option<serde_json::Value>,
        context: &C,
    ) -> Result<DeleteEventsResponse, ApiError>;

    /// Return the timestamp of the latest event in ms since the epoch in UTC.
    async fn get_latest_event_timestamp(
        &self,
        id: i64,
        context: &C,
    ) -> Result<GetLatestEventTimestampResponse, ApiError>;
}

/// Implementation of events API for the server
#[derive(Clone)]
pub struct EventsApiImpl {
    pub context: ApiContext,
}

impl EventsApiImpl {
    pub fn new(context: ApiContext) -> Self {
        Self { context }
    }
}

#[async_trait]
impl<C> EventsApi<C> for EventsApiImpl
where
    C: Has<XSpanIdString> + Send + Sync,
{
    /// Store an event.
    async fn create_event(
        &self,
        mut body: models::EventModel,
        context: &C,
    ) -> Result<CreateEventResponse, ApiError> {
        debug!(
            "create_event({:?}) - X-Span-ID: {:?}",
            body,
            context.get().0.clone()
        );

        let timestamp = Utc::now().format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string();
        let data = body.data.to_string();

        let result = match sqlx::query!(
            r#"
            INSERT INTO event
            (
                workflow_id,
                timestamp,
                data
            )
            VALUES ($1, $2, $3)
            RETURNING rowid
            "#,
            body.workflow_id,
            timestamp,
            data,
        )
        .fetch_one(self.context.pool.as_ref())
        .await
        {
            Ok(result) => result,
            Err(e) => {
                return Err(database_error(e));
            }
        };

        body.id = Some(result.id);
        Ok(CreateEventResponse::SuccessfulResponse(body))
    }

    /// Retrieve an event by ID.
    async fn get_event(&self, id: i64, context: &C) -> Result<GetEventResponse, ApiError> {
        debug!(
            "get_event({}) - X-Span-ID: {:?}",
            id,
            context.get().0.clone()
        );

        let record = match sqlx::query!(
            r#"
            SELECT id, workflow_id, timestamp, data as "data: String"
            FROM event
            WHERE id = $1
            "#,
            id
        )
        .fetch_optional(self.context.pool.as_ref())
        .await
        {
            Ok(Some(rec)) => rec,
            Ok(None) => {
                let error_response = models::ErrorResponse::new(serde_json::json!({
                    "message": format!("Event not found with ID: {}", id)
                }));
                return Ok(GetEventResponse::NotFoundErrorResponse(error_response));
            }
            Err(e) => {
                return Err(database_error(e));
            }
        };

        let data = match serde_json::from_str(&record.data) {
            Ok(json) => json,
            Err(e) => {
                return Err(json_parse_error(e));
            }
        };

        let event = models::EventModel {
            id: Some(record.id),
            workflow_id: record.workflow_id,
            timestamp: record.timestamp,
            data,
        };

        Ok(GetEventResponse::SuccessfulResponse(event))
    }

    /// Retrieve all events for one workflow.
    async fn list_events(
        &self,
        workflow_id: i64,
        offset: i64,
        limit: i64,
        sort_by: Option<String>,
        reverse_sort: Option<bool>,
        category: Option<String>,
        after_timestamp: Option<f64>,
        context: &C,
    ) -> Result<ListEventsResponse, ApiError> {
        debug!(
            "list_events({}, {}, {}, {:?}, {:?}, {:?}, {:?}) - X-Span-ID: {:?}",
            workflow_id,
            offset,
            limit,
            sort_by,
            reverse_sort,
            category,
            after_timestamp,
            context.get().0.clone()
        );

        // Build base query
        let base_query = "SELECT id, workflow_id, timestamp, data FROM event".to_string();

        // Build WHERE clause conditions
        let mut where_conditions = vec!["workflow_id = ?".to_string()];

        // Add timestamp filter if provided
        let timestamp_str = if let Some(timestamp) = after_timestamp {
            // Convert timestamp from milliseconds since epoch to DateTime
            let timestamp_seconds = timestamp / 1000.0;
            let datetime = match DateTime::from_timestamp(
                timestamp_seconds as i64,
                (timestamp_seconds.fract() * 1_000_000_000.0) as u32,
            ) {
                Some(dt) => dt,
                None => {
                    return Err(ApiError(format!("Invalid timestamp: {}", timestamp)));
                }
            };

            // Convert to ISO 8601 string format for comparison
            let ts_str = datetime.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string();
            where_conditions.push("timestamp > ?".to_string());
            Some(ts_str)
        } else {
            None
        };

        // Note: Category filtering is not implemented in current schema
        let _category = category; // Acknowledge the parameter to avoid unused warnings

        let where_clause = where_conditions.join(" AND ");

        // Build the complete query with pagination and sorting
        let query = SqlQueryBuilder::new(base_query)
            .with_where(where_clause.clone())
            .with_pagination_and_sorting(offset, limit, sort_by, reverse_sort, "id")
            .build();

        debug!("Executing query: {}", query);

        // Execute the query
        let mut sqlx_query = sqlx::query(&query);

        // Bind workflow_id
        sqlx_query = sqlx_query.bind(workflow_id);

        // Bind timestamp if provided
        if let Some(ref ts_str) = timestamp_str {
            sqlx_query = sqlx_query.bind(ts_str);
        }

        let records = match sqlx_query.fetch_all(self.context.pool.as_ref()).await {
            Ok(recs) => recs,
            Err(e) => {
                error!("Database error: {}", e);
                return Err(database_error(e));
            }
        };

        let mut items: Vec<models::EventModel> = Vec::new();
        for record in records {
            let data_str: String = record.get("data");
            let data = match serde_json::from_str(&data_str) {
                Ok(json) => json,
                Err(e) => {
                    return Err(json_parse_error(e));
                }
            };

            items.push(models::EventModel {
                id: Some(record.get("id")),
                workflow_id: record.get("workflow_id"),
                timestamp: record.get("timestamp"),
                data,
            });
        }

        // For proper pagination, we should get the total count without LIMIT/OFFSET
        let count_query = SqlQueryBuilder::new("SELECT COUNT(*) as total FROM event".to_string())
            .with_where(where_clause)
            .build();

        let mut count_sqlx_query = sqlx::query(&count_query);
        count_sqlx_query = count_sqlx_query.bind(workflow_id);

        // Bind timestamp for count query if provided
        if let Some(ref ts_str) = timestamp_str {
            count_sqlx_query = count_sqlx_query.bind(ts_str);
        }

        let total_count = match count_sqlx_query.fetch_one(self.context.pool.as_ref()).await {
            Ok(row) => row.get::<i64, _>("total"),
            Err(e) => {
                error!("Database error getting count: {}", e);
                return Err(database_error(e));
            }
        };

        let current_count = items.len() as i64;
        let offset_val = offset;
        let has_more = offset_val + current_count < total_count;

        debug!(
            "list_events({}, {}/{}) - X-Span-ID: {:?}",
            workflow_id,
            current_count,
            total_count,
            context.get().0.clone()
        );

        Ok(ListEventsResponse::SuccessfulResponse(
            models::ListEventsResponse {
                items: Some(items),
                offset: offset_val,
                max_limit: MAX_RECORD_TRANSFER_COUNT,
                count: current_count,
                total_count,
                has_more,
            },
        ))
    }

    /// Update an event.
    async fn update_event(
        &self,
        id: i64,
        body: serde_json::Value,
        context: &C,
    ) -> Result<UpdateEventResponse, ApiError> {
        debug!(
            "update_event({}, {:?}) - X-Span-ID: {:?}",
            id,
            body,
            context.get().0.clone()
        );

        // First get the existing event to ensure it exists
        match self.get_event(id, context).await? {
            GetEventResponse::SuccessfulResponse(_) => {}
            GetEventResponse::NotFoundErrorResponse(err) => {
                return Ok(UpdateEventResponse::NotFoundErrorResponse(err));
            }
            GetEventResponse::DefaultErrorResponse(_) => {
                return Err(ApiError("Failed to get event".to_string()));
            }
        };

        // Convert body to string for database storage
        let data_str = body.to_string();

        let result = match sqlx::query(
            r#"
            UPDATE event
            SET data = $1
            WHERE id = $2
            "#,
        )
        .bind(data_str)
        .bind(id)
        .execute(self.context.pool.as_ref())
        .await
        {
            Ok(result) => result,
            Err(e) => {
                error!("Database error: {}", e);
                return Err(database_error(e));
            }
        };

        if result.rows_affected() == 0 {
            let error_response = models::ErrorResponse::new(serde_json::json!({
                "message": format!("Event not found with ID: {}", id)
            }));
            return Ok(UpdateEventResponse::NotFoundErrorResponse(error_response));
        }

        // Return the updated event by fetching it again
        let updated_event = match self.get_event(id, context).await? {
            GetEventResponse::SuccessfulResponse(event) => event,
            _ => return Err(ApiError("Failed to get updated event".to_string())),
        };

        debug!("Modified event with id: {}", id);
        Ok(UpdateEventResponse::SuccessfulResponse(updated_event))
    }

    /// Delete an event.
    async fn delete_event(
        &self,
        id: i64,
        body: Option<serde_json::Value>,
        context: &C,
    ) -> Result<DeleteEventResponse, ApiError> {
        debug!(
            "delete_event({}, {:?}) - X-Span-ID: {:?}",
            id,
            body,
            context.get().0.clone()
        );

        // First get the event to ensure it exists and extract the EventModel
        let event = match self.get_event(id, context).await? {
            GetEventResponse::SuccessfulResponse(event) => event,
            GetEventResponse::NotFoundErrorResponse(err) => {
                return Ok(DeleteEventResponse::NotFoundErrorResponse(err));
            }
            GetEventResponse::DefaultErrorResponse(_) => {
                return Err(ApiError("Failed to get event".to_string()));
            }
        };

        match sqlx::query!(r#"DELETE FROM event WHERE id = $1"#, id)
            .execute(self.context.pool.as_ref())
            .await
        {
            Ok(res) => {
                if res.rows_affected() > 1 {
                    Err(ApiError(format!(
                        "Database error: Unexpected number of rows affected: {}",
                        res.rows_affected()
                    )))
                } else if res.rows_affected() == 0 {
                    Err(ApiError("Database error: No rows affected".to_string()))
                } else {
                    Ok(DeleteEventResponse::SuccessfulResponse(event))
                }
            }
            Err(e) => Err(ApiError(format!("Database error: {}", e))),
        }
    }

    /// Delete all events for one workflow.
    async fn delete_events(
        &self,
        workflow_id: i64,
        body: Option<serde_json::Value>,
        context: &C,
    ) -> Result<DeleteEventsResponse, ApiError> {
        debug!(
            "delete_events(\"{}\", {:?}) - X-Span-ID: {:?}",
            workflow_id,
            body,
            context.get().0.clone()
        );
        Err(ApiError("Api-Error: Operation is NOT implemented".into()))
    }

    /// Return the timestamp of the latest event in ms since the epoch in UTC.
    async fn get_latest_event_timestamp(
        &self,
        id: i64,
        context: &C,
    ) -> Result<GetLatestEventTimestampResponse, ApiError> {
        debug!(
            "get_latest_event_timestamp({}) - X-Span-ID: {:?}",
            id,
            context.get().0.clone()
        );

        // Find the event with the highest ID for the given workflow
        let record = match sqlx::query!(
            r#"
            SELECT timestamp
            FROM event
            WHERE workflow_id = $1
            ORDER BY id DESC
            LIMIT 1
            "#,
            id
        )
        .fetch_optional(self.context.pool.as_ref())
        .await
        {
            Ok(Some(rec)) => rec,
            Ok(None) => {
                let error_response = models::ErrorResponse::new(serde_json::json!({
                    "message": format!("No events found for workflow_id: {}", id)
                }));
                return Ok(GetLatestEventTimestampResponse::NotFoundErrorResponse(
                    error_response,
                ));
            }
            Err(e) => {
                return Err(database_error(e));
            }
        };

        // Parse the ISO 8601 timestamp string
        let datetime = match DateTime::parse_from_rfc3339(&record.timestamp) {
            Ok(dt) => dt.with_timezone(&Utc),
            Err(e) => {
                return Err(ApiError(format!(
                    "Failed to parse timestamp '{}': {}",
                    record.timestamp, e
                )));
            }
        };

        // Convert to milliseconds since epoch
        let timestamp_ms = datetime.timestamp_millis();

        debug!(
            "Latest event timestamp for workflow {}: {} ms ({})",
            id, timestamp_ms, record.timestamp
        );

        // TODO: change this to a proper data model
        Ok(GetLatestEventTimestampResponse::SuccessfulResponse(
            serde_json::json!({ "timestamp": timestamp_ms }),
        ))
    }
}
