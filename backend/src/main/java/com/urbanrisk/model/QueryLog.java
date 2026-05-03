package com.urbanrisk.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "query_log")
public class QueryLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String tenantId;

    @Column(nullable = false)
    private String intersectionName;

    @Column(nullable = false)
    private String queryType; // "predict" | "explain"

    private String modelUsed;
    private String riskResult;
    private Double latencyMs;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    @PrePersist
    protected void onCreate() {
        timestamp = LocalDateTime.now();
    }

    // ─── Constructors ─────────────────────────────────────────────────────
    public QueryLog() {}

    public QueryLog(String tenantId, String intersectionName,
                    String queryType, String modelUsed,
                    String riskResult, Double latencyMs) {
        this.tenantId = tenantId;
        this.intersectionName = intersectionName;
        this.queryType = queryType;
        this.modelUsed = modelUsed;
        this.riskResult = riskResult;
        this.latencyMs = latencyMs;
    }

    // ─── Getters / Setters ────────────────────────────────────────────────
    public Long getId() { return id; }
    public String getTenantId() { return tenantId; }
    public String getIntersectionName() { return intersectionName; }
    public String getQueryType() { return queryType; }
    public String getModelUsed() { return modelUsed; }
    public String getRiskResult() { return riskResult; }
    public Double getLatencyMs() { return latencyMs; }
    public LocalDateTime getTimestamp() { return timestamp; }

    public void setTenantId(String tenantId) { this.tenantId = tenantId; }
    public void setIntersectionName(String intersectionName) { this.intersectionName = intersectionName; }
    public void setQueryType(String queryType) { this.queryType = queryType; }
    public void setModelUsed(String modelUsed) { this.modelUsed = modelUsed; }
    public void setRiskResult(String riskResult) { this.riskResult = riskResult; }
    public void setLatencyMs(Double latencyMs) { this.latencyMs = latencyMs; }
}
