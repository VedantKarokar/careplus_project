CREATE TABLE IF NOT EXISTS `support_tickets` (
    `Ticket_id` TEXT,
    `Created_at` TEXT,
    `Resolved_at` TEXT,
    `Agent` TEXT,
    `Priority` TEXT,
    `Num_interactions` TEXT,
    `IssUeCat` TEXT,
    `Channel` TEXT,
    `Status` TEXT,
    `Agent_feedback` TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;