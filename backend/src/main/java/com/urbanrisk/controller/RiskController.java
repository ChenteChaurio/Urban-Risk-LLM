package com.urbanrisk.controller;

import com.urbanrisk.model.QueryLog;
import com.urbanrisk.model.QueryLogRepository;
import com.urbanrisk.service.RiskService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class RiskController {

    private final RiskService riskService;
    private final QueryLogRepository logRepository;

    public RiskController(RiskService riskService, QueryLogRepository logRepository) {
        this.riskService = riskService;
        this.logRepository = logRepository;
    }

    /**
     * Predice el nivel de riesgo de una intersección.
     * Header x-tenant-id determina qué modelo usar por defecto.
     */
    @PostMapping("/predict")
    public ResponseEntity<?> predict(
            @RequestBody Map<String, Object> body,
            @RequestHeader(value = "x-tenant-id", defaultValue = "bogota") String tenantId) {
        try {
            Map<String, Object> result = riskService.predict(body, tenantId);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(503)
                    .body(Map.of("error", "ML service unavailable", "detail", e.getMessage()));
        }
    }

    /**
     * Genera explicación normativa (RAG) para una predicción.
     */
    @PostMapping("/explain")
    public ResponseEntity<?> explain(
            @RequestBody Map<String, Object> body,
            @RequestHeader(value = "x-tenant-id", defaultValue = "bogota") String tenantId) {
        try {
            Map<String, Object> result = riskService.explain(body, tenantId);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(503)
                    .body(Map.of("error", "ML service unavailable", "detail", e.getMessage()));
        }
    }

    /**
     * Métricas de los modelos entrenados.
     */
    @GetMapping("/metrics")
    public ResponseEntity<?> metrics() {
        try {
            return ResponseEntity.ok(riskService.getMetrics());
        } catch (Exception e) {
            return ResponseEntity.status(503)
                    .body(Map.of("error", "ML service unavailable"));
        }
    }

    /**
     * Últimas 50 consultas registradas (trazabilidad).
     */
    @GetMapping("/logs")
    public ResponseEntity<List<QueryLog>> logs(
            @RequestParam(required = false) String tenantId) {
        if (tenantId != null) {
            return ResponseEntity.ok(logRepository.findByTenantId(tenantId));
        }
        return ResponseEntity.ok(logRepository.findTop50ByOrderByTimestampDesc());
    }

    /**
     * Health check del backend y del servicio ML.
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        try {
            Map<?, ?> mlHealth = riskService.mlHealth();
            return ResponseEntity.ok(Map.of(
                    "backend", "ok",
                    "ml_service", mlHealth));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                    "backend", "ok",
                    "ml_service", "unreachable"));
        }
    }
}
