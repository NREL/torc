//! SQL query builder utility for pagination and sorting

/// Utility for building SQL queries with pagination and sorting
pub struct SqlQueryBuilder {
    base_query: String,
    where_clause: Option<String>,
    order_by_clause: Option<String>,
    limit_clause: Option<String>,
    offset_clause: Option<String>,
}

impl SqlQueryBuilder {
    pub fn new(base_query: String) -> Self {
        Self {
            base_query,
            where_clause: None,
            order_by_clause: None,
            limit_clause: None,
            offset_clause: None,
        }
    }

    pub fn with_where(mut self, where_clause: String) -> Self {
        self.where_clause = Some(where_clause);
        self
    }

    pub fn with_pagination_and_sorting(
        mut self,
        offset: i64,
        limit: i64,
        sort_by: Option<String>,
        reverse_sort: Option<bool>,
        default_sort_column: &str,
    ) -> Self {
        let sort_column = sort_by
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| default_sort_column.to_string());
        let sort_direction = if reverse_sort.unwrap_or(false) {
            "DESC"
        } else {
            "ASC"
        };
        self.order_by_clause = Some(format!("ORDER BY {} {}", sort_column, sort_direction));

        self.limit_clause = Some(format!("LIMIT {}", limit));

        if offset > 0 {
            self.offset_clause = Some(format!("OFFSET {}", offset));
        }

        self
    }

    pub fn build(self) -> String {
        let mut query = self.base_query;

        if let Some(where_clause) = self.where_clause {
            query.push_str(" WHERE ");
            query.push_str(&where_clause);
        }

        if let Some(order_by) = self.order_by_clause {
            query.push(' ');
            query.push_str(&order_by);
        }

        if let Some(limit) = self.limit_clause {
            query.push(' ');
            query.push_str(&limit);
        }

        if let Some(offset) = self.offset_clause {
            query.push(' ');
            query.push_str(&offset);
        }

        query
    }
}
