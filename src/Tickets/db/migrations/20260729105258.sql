-- Create "Tickets" table
CREATE TABLE `Tickets` (
  `ticket_id` varchar(20) NOT NULL,
  `created_at` varchar(20) NULL,
  `resolved_at` varchar(20) NULL,
  `agent` varchar(30) NULL,
  `priority` varchar(10) NULL,
  `num_interactions` varchar(10) NULL,
  `IssueCat` varchar(50) NULL,
  `channel` varchar(10) NULL,
  `status` varchar(10) NULL,
  `agent_feedback` varchar(10) NULL,
  PRIMARY KEY (`ticket_id`)
) CHARSET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
