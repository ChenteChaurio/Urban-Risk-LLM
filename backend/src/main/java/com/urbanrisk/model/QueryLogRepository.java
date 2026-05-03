package com.urbanrisk.model;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface QueryLogRepository extends JpaRepository<QueryLog, Long> {
    List<QueryLog> findByTenantId(String tenantId);
    List<QueryLog> findTop50ByOrderByTimestampDesc();
}
